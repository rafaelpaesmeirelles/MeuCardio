import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";

/** Espelha `_dump` de `app/api/guidelines.py`. A lista não traz qual diretriz
 *  substituiu qual — só o fato de ter sido substituída. Quem cruza as duas
 *  pontas é `/meus-alertas`, e é por isso que ele é a parte de cima da tela. */
type Diretriz = {
  slug: string;
  org: string;
  titulo: string;
  ano: number;
  doi: string | null;
  url: string | null;
  vinculos: number;
  vinculos_confirmados: number;
  substituida: boolean;
  substituida_em: string | null;
};

type Alerta = {
  diretriz_revisada: { titulo: string; org: string; ano: number };
  nova_versao: { titulo: string; ano: number; doi: string | null; url: string | null } | null;
  seus_documentos: { slug: string; titulo: string }[];
  significado: string;
};

type RespostaAlertas = { alertas: Alerta[]; nota?: string };

export default function Diretrizes() {
  const [alertas, setAlertas] = useState<RespostaAlertas | null>(null);
  const [revisadas, setRevisadas] = useState<Diretriz[] | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.get<RespostaAlertas>("/diretrizes/meus-alertas")
      .then(setAlertas)
      .catch((e) => setErro(e.message));
    // A lista geral falha sozinha: sem ela a página ainda mostra os alertas,
    // que são a razão de ela existir.
    api.get<Diretriz[]>("/diretrizes?substituidas=true")
      .then(setRevisadas)
      .catch(() => setRevisadas([]));
  }, []);

  if (erro) return <Erro mensagem={erro} />;
  if (!alertas) return <Carregando />;

  const temAlerta = alertas.alertas.length > 0;

  return (
    <>
      <p className="eyebrow">Diretrizes</p>
      <h1>Alertas de revisão</h1>
      <p style={{ maxWidth: "68ch", color: "var(--texto-secundario)" }}>
        Quando uma diretriz que embasa um conteúdo seu é revisada, o aviso aparece
        aqui. O alerta é sobre <strong>a diretriz ter mudado</strong> — não afirma
        que o material da Corvia esteja desatualizado.
      </p>

      {!temAlerta && (
        <div className="cartao" style={{ marginTop: "1.2rem" }}>
          <strong>Nenhum alerta para você agora.</strong>
          <p style={{ margin: "0.4rem 0 0", fontSize: "0.88rem", color: "var(--texto-secundario)" }}>
            {alertas.nota ??
              "Nenhuma das diretrizes que sustentam os seus documentos favoritados foi revisada."}
          </p>
          <p style={{ margin: "0.6rem 0 0", fontSize: "0.88rem" }}>
            <Link to="/biblioteca">Favoritar documentos</Link> é o que liga este canal:
            os alertas seguem o que você marcou.
          </p>
        </div>
      )}

      {temAlerta && (
        <div style={{ display: "grid", gap: "0.8rem", marginTop: "1.2rem" }}>
          {alertas.alertas.map((a, i) => (
            <article key={i} className="cartao painel__funcao painel__funcao--destaque">
              <strong>
                {a.diretriz_revisada.org} {a.diretriz_revisada.ano} — {a.diretriz_revisada.titulo}
              </strong>
              {a.nova_versao && (
                <span>
                  Versão mais recente: <strong>{a.nova_versao.titulo}</strong> ({a.nova_versao.ano})
                  {a.nova_versao.doi && <> · DOI: {a.nova_versao.doi}</>}
                  {a.nova_versao.url && (
                    <> · <a href={a.nova_versao.url} target="_blank" rel="noreferrer">abrir</a></>
                  )}
                </span>
              )}
              <span>{a.significado}</span>
              <span>
                <strong>Seus documentos que se apoiam nela:</strong>
                <ul style={{ margin: "0.3rem 0 0", paddingLeft: "1.1rem" }}>
                  {a.seus_documentos.map((d) => (
                    <li key={d.slug}>
                      <Link to={`/biblioteca/${d.slug}`}>{d.titulo}</Link>
                    </li>
                  ))}
                </ul>
              </span>
            </article>
          ))}
        </div>
      )}

      {revisadas !== null && revisadas.length > 0 && (
        <section className="painel__grupo">
          <h2>Todas as diretrizes já revisadas</h2>
          <p className="painel__grupo-sub">
            Independentemente de você usar o conteúdo que se apoia nelas.
          </p>
          <div className="painel__funcoes">
            {revisadas.map((g) => (
              <div key={g.slug} className="cartao painel__funcao painel__funcao--breve">
                <strong>
                  {g.org} {g.ano} — {g.titulo}
                </strong>
                <span>
                  Revisada{g.substituida_em ? ` em ${g.substituida_em.slice(0, 10)}` : ""} ·{" "}
                  {g.vinculos === 0
                    ? "sem conteúdo vinculado"
                    : `${g.vinculos} item(ns) da Corvia se apoiam nela`}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}
    </>
  );
}
