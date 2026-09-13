import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, READ_TIMEOUT_MS } from "../lib/api";
import { useAuth } from "../lib/auth";

type Alerta = {
  diretriz_revisada: { titulo: string; org: string; ano: number | null };
  nova_versao: { titulo: string; ano: number | null; doi: string | null; url: string | null } | null;
  seus_documentos: { slug: string; titulo: string }[];
  significado: string;
};
type Resposta = { alertas: Alerta[]; nota?: string };

function fontePublica(value: string | null) {
  if (!value) return null;
  try {
    const url = new URL(value);
    return ["https:", "http:"].includes(url.protocol) ? url.href : null;
  } catch { return null; }
}

function AlertasDaConta() {
  const [resposta, setResposta] = useState<Resposta | null>(null);
  const [erro, setErro] = useState(false);
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    let ativo = true;
    const controller = new AbortController();
    setResposta(null); setErro(false);
    api.get<Resposta>("/diretrizes/meus-alertas", { signal: controller.signal, timeoutMs: READ_TIMEOUT_MS })
      .then(value => { if (ativo) setResposta(value); })
      .catch(() => { if (ativo) setErro(true); });
    return () => { ativo = false; controller.abort(); };
  }, [tentativa]);

  return <section className="cartao favorite-guideline-alerts" aria-labelledby="alertas-diretrizes-favoritas">
    <h2 id="alertas-diretrizes-favoritas">Atualizações nas diretrizes dos seus favoritos</h2>
    <p>Revisões das fontes vinculadas aos documentos que você salvou na Biblioteca.</p>
    {!resposta && !erro && <p role="status">Consultando revisões dos seus favoritos…</p>}
    {erro && <p role="alert">Não foi possível consultar as revisões dos seus favoritos. Os demais conteúdos continuam disponíveis.</p>}
    {resposta && <>
      {resposta.nota && <p>{resposta.nota}</p>}
      {!resposta.alertas.length && <p>Nenhuma revisão de diretriz vinculada aos seus documentos favoritos.</p>}
      {resposta.alertas.map((alerta, index) => {
        const nova = alerta.nova_versao;
        const fonte = fontePublica(nova?.url ?? null);
        return <article key={`${alerta.diretriz_revisada.titulo}-${index}`}>
          <h3>{alerta.diretriz_revisada.titulo}</h3>
          <p>{[alerta.diretriz_revisada.org, alerta.diretriz_revisada.ano].filter(value => value != null && value !== "").join(" · ")}</p>
          {nova && <p><strong>Nova versão:</strong> {nova.titulo}{nova.ano ? ` (${nova.ano})` : ""}</p>}
          <p>{alerta.significado}</p>
          <ul>{alerta.seus_documentos.map(documento => <li key={documento.slug}>
            <Link to={`/biblioteca/${encodeURIComponent(documento.slug)}`}>{documento.titulo}</Link>
          </li>)}</ul>
          {fonte && <a href={fonte} target="_blank" rel="noopener noreferrer">Abrir a nova versão na fonte ↗</a>}
          {nova?.doi && <p>DOI: {nova.doi}</p>}
        </article>;
      })}
    </>}
    {(resposta || erro) && <button type="button" className="botao botao--secundario" onClick={() => setTentativa(value => value + 1)}>
      {erro ? "Tentar carregar alertas dos favoritos novamente" : "Atualizar alertas dos favoritos"}
    </button>}
  </section>;
}

export default function AlertasDiretrizesFavoritas() {
  const { usuario } = useAuth();
  // A new account starts a new component before effects run, without exposing
  // the previous account's saved interests or accepting its delayed response.
  return usuario ? <AlertasDaConta key={usuario.id} /> : null;
}
