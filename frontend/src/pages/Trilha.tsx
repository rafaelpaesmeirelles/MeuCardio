import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../lib/api";
import GrafoRelacionados from "../components/GrafoRelacionados";

type Etapa = {
  etapa_id: string;
  ordem: number;
  item_type: string;
  item_slug: string;
  por_que: string;
  titulo: string | null;
  link: string;
  concluida: boolean;
  disponivel: boolean;
};

type Detalhe = {
  slug: string;
  titulo: string;
  tema: string | null;
  objetivo: string | null;
  total_etapas: number;
  concluidas: number;
  finalizada_em: string | null;
  concluida_atualmente: boolean;
  conclusao_historica_em: string | null;
  etapas: Etapa[];
  etapas_indisponiveis: number;
};

const TIPO: Record<string, string> = {
  documento: "Protocolo",
  medicamento: "Medicamento",
  estudo: "Estudo",
  calculadora: "Calculadora",
  checklist: "Checklist",
  evidencia: "Evidência",
  caso_clinico: "Caso clínico",
};

export default function Trilha() {
  const { slug = "" } = useParams();
  const [d, setD] = useState<Detalhe | null>(null);
  const [erro, setErro] = useState("");
  const [salvandoEtapa, setSalvandoEtapa] = useState<string | null>(null);
  const slugAtual = useRef(slug);

  useEffect(() => {
    slugAtual.current = slug;
    let ativo = true;
    setD(null);
    setErro("");
    setSalvandoEtapa(null);
    api.get<Detalhe>(`/trilhas/${slug}`)
      .then((dados) => { if (ativo) setD(dados); })
      .catch((e) => { if (ativo) setErro(e?.message || "Erro"); });
    return () => { ativo = false; };
  }, [slug]);

  async function alternar(e: Etapa) {
    if (salvandoEtapa) return;
    setSalvandoEtapa(e.etapa_id);
    setErro("");
    const slugSolicitado = slug;
    try {
      const r = await api.post<Detalhe>(`/trilhas/${slug}/progresso`, {
        etapa_id: e.etapa_id,
        item_type: e.item_type,
        item_slug: e.item_slug,
        concluida: !e.concluida,
      });
      if (slugAtual.current === slugSolicitado) setD(r);
    } catch (err: any) {
      if (slugAtual.current === slugSolicitado) {
        setErro(err?.message || "Não foi possível salvar o progresso.");
      }
    } finally {
      if (slugAtual.current === slugSolicitado) setSalvandoEtapa(null);
    }
  }

  if (erro && !d) return <p className="erro">{erro}</p>;
  if (!d || d.slug !== slug) return <p>Carregando…</p>;

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
        {d.concluida_atualmente && <span className="trilha__concluida">concluída</span>}
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
            key={e.etapa_id}
            className={`trilha__etapa${e.concluida ? " trilha__etapa--ok" : ""}${
              e.disponivel ? "" : " trilha__etapa--indisponivel"
            }`}
          >
            <button
              className="trilha__marcar"
              onClick={() => alternar(e)}
              disabled={salvandoEtapa !== null || (!e.disponivel && !e.concluida)}
              aria-label={
                !e.disponivel && !e.concluida
                  ? "Etapa indisponível enquanto o conteúdo está em revisão"
                  : e.concluida
                    ? "Desmarcar etapa"
                    : "Marcar etapa como concluída"
              }
            >
              {e.concluida ? "✓" : e.ordem}
            </button>
            <div className="trilha__corpo">
              <span className="trilha__tipo">{TIPO[e.item_type] || e.item_type}</span>
              {/* 07/08/2026: título vem de verdade do item referenciado (`titulo`,
                  calculado no backend a partir da tabela certa por `item_type`).
                  O `replace(/-/g, " ")` do slug fica só como último recurso, para
                  etapa cujo item sumiu ou tem slug digitado errado — caso em que
                  não há título nenhum para buscar. */}
              {e.disponivel ? (
                <Link to={e.link} className="trilha__titulo">
                  {e.titulo || e.item_slug.replace(/-/g, " ")}
                </Link>
              ) : (
                <span className="trilha__titulo trilha__titulo--off">
                  {e.titulo || e.item_slug.replace(/-/g, " ")} <em>— em revisão, ainda não publicado</em>
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

      <GrafoRelacionados entityType="trilha" slug={d.slug} />
    </div>
  );
}
