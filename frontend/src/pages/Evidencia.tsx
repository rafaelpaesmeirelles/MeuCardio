import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";
import BotaoFavorito from "../components/BotaoFavorito";
import TudoSobreEsteTema from "../components/TudoSobreEsteTema";
import { rotuloClasse, rotuloNivel } from "../lib/evidencia";

type Detalhe = {
  id: number;
  slug: string;
  statement: string;
  summary: string;
  recommendation_class: string;
  evidence_level: string;
  society: string;
  year: number;
  theme: string;
  guideline_title: string;
  reference: string;
  source_url: string | null;
  doi: string | null;
  document_slug: string | null;
  tags: string[];
};

export default function Evidencia() {
  const { slug } = useParams();
  const [evidencia, setEvidencia] = useState<Detalhe | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    if (!slug) return;
    api.get<Detalhe>(`/evidence/${slug}`)
      .then(setEvidencia)
      .catch((err) => setErro(err instanceof ApiError ? err.message : "Não foi possível carregar."));
  }, [slug]);

  if (erro) return <Erro mensagem={erro} />;
  if (!evidencia) return <Carregando />;

  return (
    <article style={{ maxWidth: "78ch" }}>
      <Link to="/evidencias" style={{ fontSize: "0.86rem" }}>← Voltar para evidências</Link>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginTop: "0.8rem" }}>
        <p className="eyebrow">{evidencia.society} {evidencia.year} · {evidencia.theme}</p>
        <BotaoFavorito itemType="evidencia" itemId={evidencia.id} />
      </div>

      <section className="cartao" style={{ marginTop: "0.4rem" }}>
        <div style={{ display: "flex", gap: 10, marginBottom: "0.6rem", flexWrap: "wrap" }}>
          <span className="selo" style={{ background: "var(--acento)", color: "var(--branco)" }}>
            {rotuloClasse(evidencia.recommendation_class)}
          </span>
          <span className="selo" style={{ background: "var(--acento)", color: "var(--branco)" }}>
            {rotuloNivel(evidencia.evidence_level)}
          </span>
        </div>
        <h1 style={{ fontSize: "1.25rem", margin: 0 }}>{evidencia.statement}</h1>
      </section>

      {/* 07/08/2026: `summary` nunca é preenchido de fato hoje — as 1.870
       * evidências publicadas têm `summary = null` no banco, e a API
       * (evidence.py) cai no fallback `e.summary or e.statement`, para nunca
       * devolver campo vazio. O efeito colateral, achado em varredura visual
       * real: o enunciado aparecia repetido palavra por palavra logo abaixo
       * de si mesmo. Como o fallback é sobre TODO o registro publicado hoje,
       * a seção some sempre que o resumo for idêntico ao enunciado — volta a
       * aparecer no dia em que `summary` for um texto genuinamente distinto. */}
      {evidencia.summary.trim() !== evidencia.statement.trim() && (
        <section className="cartao" style={{ marginTop: "0.8rem" }}>
          <p className="eyebrow">Resumo clínico</p>
          <p style={{ lineHeight: 1.65, marginBottom: 0 }}>{evidencia.summary}</p>
        </section>
      )}

      <section className="cartao" style={{ marginTop: "0.8rem" }}>
        <p className="eyebrow">Diretriz de origem</p>
        <p>{evidencia.guideline_title}</p>
        {evidencia.doi && <p style={{ fontSize: "0.86rem" }}><strong>DOI:</strong> {evidencia.doi}</p>}
        {evidencia.source_url && (
          <a
            href={evidencia.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="botao"
            style={{ display: "inline-block" }}
          >
            Abrir documento original ↗
          </a>
        )}
      </section>

      <section className="cartao" style={{ marginTop: "0.8rem" }}>
        <p className="eyebrow">Referência completa</p>
        <p style={{ fontSize: "0.88rem", overflowWrap: "anywhere" }}>{evidencia.reference}</p>
      </section>

      {evidencia.document_slug && (
        <Link
          to={`/biblioteca/${evidencia.document_slug}`}
          className="botao botao--secundario"
          style={{ display: "inline-block", marginTop: "0.8rem" }}
        >
          Ver análise relacionada na Biblioteca
        </Link>
      )}

      <TudoSobreEsteTema tema={evidencia.theme} excluirTipo="evidencia" excluirSlug={slug} />
    </article>
  );
}
