import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

type Resumo = {
  slug: string;
  condicao: string;
  resumo: string | null;
  theme: string | null;
  documento_origem: string | null;
  total_itens: number;
  obrigatorios: number;
};

type Aplicacao = {
  id: number;
  condicao: string;
  identificacao: string | null;
  finalizado_em: string | null;
  criado_em: string;
  marcados: number;
  total: number;
  faltando_obrigatorios: number;
};

export default function Checklists() {
  const [modelos, setModelos] = useState<Resumo[] | null>(null);
  const [minhas, setMinhas] = useState<Aplicacao[]>([]);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.get<Resumo[]>("/checklists").then(setModelos).catch(() => setModelos([]));
    api.get<Aplicacao[]>("/checklists/aplicacoes/minhas").then(setMinhas).catch(() => setMinhas([]));
  }, []);

  async function iniciar(slug: string) {
    const identificacao = window.prompt(
      "Identificação desta alta (opcional — leito, iniciais, o que você usa para se localizar):"
    );
    if (identificacao === null) return;
    try {
      const r = await api.post<{ id: number }>("/checklists/aplicacoes", {
        checklist_slug: slug,
        identificacao_livre: identificacao || null,
      });
      window.location.href = `/checklists/alta/${r.id}`;
    } catch (e: any) {
      setErro(e?.message || "Não foi possível iniciar o checklist.");
    }
  }

  const emAndamento = minhas.filter((a) => !a.finalizado_em);

  return (
    <div>
      <h1>Checklist de alta</h1>
      <p className="subtitulo">
        O que não pode faltar na alta, por condição. Os itens vêm dos protocolos da
        biblioteca — cada um traz a seção de onde saiu.
      </p>
      {erro && <p className="erro">{erro}</p>}

      {emAndamento.length > 0 && (
        <>
          <h2>Em andamento</h2>
          <ul className="checklist__abertas">
            {emAndamento.map((a) => (
              <li key={a.id}>
                <Link to={`/checklists/alta/${a.id}`}>
                  <strong>{a.condicao}</strong>
                  {a.identificacao && <span className="dado">{a.identificacao}</span>}
                </Link>
                <span className="checklist__progresso">
                  {a.marcados}/{a.total}
                  {a.faltando_obrigatorios > 0 && (
                    <em> · {a.faltando_obrigatorios} obrigatório(s) pendente(s)</em>
                  )}
                </span>
              </li>
            ))}
          </ul>
        </>
      )}

      <h2 style={{ marginTop: emAndamento.length ? "1.6rem" : undefined }}>Condições</h2>
      {modelos === null ? (
        <p>Carregando…</p>
      ) : modelos.length === 0 ? (
        <p className="curso__vazio">
          Nenhum checklist publicado ainda. Eles aparecem aqui depois da revisão clínica.
        </p>
      ) : (
        <div className="painel__funcoes">
          {modelos.map((m) => (
            <div key={m.slug} className="cartao painel__funcao">
              <strong>{m.condicao}</strong>
              <span>{m.resumo}</span>
              <span className="dado">
                {m.total_itens} itens · {m.obrigatorios} obrigatórios
              </span>
              <button className="botao botao--acao" onClick={() => iniciar(m.slug)}>
                Usar nesta alta
              </button>
              {m.documento_origem && (
                <Link className="checklist__origem" to={`/biblioteca/${m.documento_origem}`}>
                  Ver o protocolo de origem
                </Link>
              )}
            </div>
          ))}
        </div>
      )}

      {minhas.filter((a) => a.finalizado_em).length > 0 && (
        <>
          <h2 style={{ marginTop: "1.8rem" }}>Finalizadas</h2>
          <ul className="checklist__abertas">
            {minhas
              .filter((a) => a.finalizado_em)
              .slice(0, 20)
              .map((a) => (
                <li key={a.id}>
                  <Link to={`/checklists/alta/${a.id}`}>
                    <strong>{a.condicao}</strong>
                    {a.identificacao && <span className="dado">{a.identificacao}</span>}
                  </Link>
                  <span className="checklist__progresso">
                    {a.marcados}/{a.total}
                    {a.faltando_obrigatorios > 0 && (
                      <em> · finalizada com pendência justificada</em>
                    )}
                  </span>
                </li>
              ))}
          </ul>
        </>
      )}
    </div>
  );
}
