import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../lib/api";

type Etapa = {
  ordem: number;
  item_type: string;
  item_slug: string;
  por_que: string;
  link: string;
  concluida: boolean;
  disponivel: boolean;
};

type Detalhe = {
  slug: string;
  titulo: string;
  objetivo: string | null;
  total_etapas: number;
  concluidas: number;
  finalizada_em: string | null;
  etapas: Etapa[];
  etapas_indisponiveis: number;
};

const TIPO: Record<string, string> = {
  documento: "Protocolo",
  medicamento: "Medicamento",
  estudo: "Estudo",
  calculadora: "Calculadora",
  checklist: "Checklist",
};

export default function Trilha() {
  const { slug = "" } = useParams();
  const [d, setD] = useState<Detalhe | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.get<Detalhe>(`/api/trilhas/${slug}`).then(setD).catch((e) => setErro(e?.message || "Erro"));
  }, [slug]);

  async function alternar(e: Etapa) {
    try {
      const r = await api.post<Detalhe>(`/api/trilhas/${slug}/progresso`, {
        item_slug: e.item_slug,
        concluida: !e.concluida,
      });
      setD(r);
    } catch (err: any) {
      setErro(err?.message || "Não foi possível salvar o progresso.");
    }
  }

  if (erro && !d) return <p className="erro">{erro}</p>;
  if (!d) return <p>Carregando…</p>;

  const pct = d.total_etapas ? Math.round((d.concluidas / d.total_etapas) * 100) : 0;

  return (
    <div>
      <p className="curso__voltar">
        <Link to="/trilhas">← Trilhas</Link>
      </p>
      <h1>{d.titulo}</h1>
      {d.objetivo && <p className="subtitulo">{d.objetivo}</p>}
      {erro && <p className="erro">{erro}</p>}

      <div className="checklist__contador">
        <strong>
          {d.concluidas}/{d.total_etapas}
        </strong>{" "}
        etapas
        <span className="trilha__barra trilha__barra--larga">
          <span style={{ width: `${pct}%` }} />
        </span>
        {d.finalizada_em && <span className="trilha__concluida">concluída</span>}
      </div>

      {d.etapas_indisponiveis > 0 && (
        <p className="aviso">
          {d.etapas_indisponiveis} etapa(s) apontam para conteúdo que ainda está em
          revisão e não foi publicado. A curadoria está completa — falta liberar o
          material.
        </p>
      )}

      <ol className="trilha__etapas">
        {d.etapas.map((e) => (
          <li
            key={e.item_slug}
            className={`trilha__etapa${e.concluida ? " trilha__etapa--ok" : ""}${
              e.disponivel ? "" : " trilha__etapa--indisponivel"
            }`}
          >
            <button
              className="trilha__marcar"
              onClick={() => alternar(e)}
              aria-label={e.concluida ? "Desmarcar etapa" : "Marcar etapa como concluída"}
            >
              {e.concluida ? "✓" : e.ordem}
            </button>
            <div className="trilha__corpo">
              <span className="trilha__tipo">{TIPO[e.item_type] || e.item_type}</span>
              {e.disponivel ? (
                <Link to={e.link} className="trilha__titulo">
                  {e.item_slug.replace(/-/g, " ")}
                </Link>
              ) : (
                <span className="trilha__titulo trilha__titulo--off">
                  {e.item_slug.replace(/-/g, " ")} <em>— em revisão, ainda não publicado</em>
                </span>
              )}
              {/* O "por quê" é o que a trilha acrescenta ao conteúdo que já existe.
                  Fica no corpo da etapa, não escondido, porque é ele que justifica
                  a ordem proposta. */}
              <p className="trilha__porque">{e.por_que}</p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
