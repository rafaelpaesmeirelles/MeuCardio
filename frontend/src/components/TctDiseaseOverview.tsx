import { useEffect, useId, useState } from "react";
import { Link } from "react-router-dom";
import ClinicalText from "./ClinicalText";
import { api } from "../lib/api";

export type TctOverviewDisease = {
  slug: string;
  name: string;
  summary?: string | null;
  area?: string | null;
  category?: string | null;
};

type DiseaseDetail = TctOverviewDisease & {
  epidemiology?: string | null;
  presentation?: unknown;
  diagnostic_approach?: unknown;
  source_refs?: unknown;
  source_urls?: unknown;
};

type ClinicalBlock = { label?: string; text?: string; children?: ClinicalBlock[] };

// Same clinical headings and taxonomy as GuiaDoenca. Technical metadata is
// deliberately not a clinical section, even if a future API response adds it.
const labels: Record<string, string> = {
  confirmacao: "Confirmação diagnóstica",
  avaliacao_inicial: "Avaliação inicial",
  estratificacao: "Estratificação",
  etiologia: "Etiologia e fatores associados",
  fenotipo: "Fenótipo clínico",
  primeiros_dados: "Primeiros dados",
  criterios_de_sangramento_maior: "Critérios de sangramento maior",
  limite: "Limitações",
  description: "Descrição", details: "Detalhes", notes: "Observações",
  criteria: "Critérios", findings: "Achados", symptoms: "Sintomas",
  limitations: "Limitações", indication: "Indicação", value: "Valor",
};
const areas: Record<string, string> = {
  geral: "Cardiologia Geral",
  cardiopediatria: "Cardiologia pediátrica e congênita",
  cardiogeriatria: "Cardiogeriatria",
  cardiooncologia: "Cardio-oncologia",
  gravidez: "Cardiologia na gestação e puerpério",
};
const categories: Record<string, string> = {
  arritmia: "Arritmias", cardiopatia_congenita: "Cardiopatias congênitas",
  cardiologia_fetal: "Cardiologia fetal", doenca_coronariana: "Doença coronariana",
  hipertensao: "Hipertensão", insuficiencia_cardiaca: "Insuficiência cardíaca",
  tromboembolismo: "Tromboembolismo", valvopatia: "Valvopatias",
};
const technicalKey = /^(?:_|id$|slug$|.*_id$|review_|source_|internal|metadata|provenance|debug|audit|version$|published$|condition|operator$|rule|type$)/i;
const narrativeKeys = new Set(["label", "name", "text", "test", "title"]);

function clinicalLabel(key: string) {
  return labels[key] || key.replace(/[_-]+/g, " ").replace(/^./, (letter) => letter.toLocaleUpperCase("pt-BR"));
}

function blocksOf(value: unknown): ClinicalBlock[] {
  if (typeof value === "string") return value.trim() ? [{ text: value }] : [];
  if (typeof value === "number" && Number.isFinite(value)) return [{ text: String(value) }];
  if (typeof value === "boolean") return [{ text: value ? "Sim" : "Não" }];
  if (Array.isArray(value)) return value.flatMap(blocksOf);
  if (!value || typeof value !== "object") return [];
  const entries = Object.entries(value as Record<string, unknown>).filter(([key]) => !technicalKey.test(key));
  // Preserve the narrative fields and all clinical detail; never stringify an object.
  return entries.flatMap(([key, child]) => {
    const children = blocksOf(child);
    if (!children.length) return [];
    return narrativeKeys.has(key) ? children : [{ label: clinicalLabel(key), children }];
  });
}

function blockLength(block: ClinicalBlock): number {
  return (block.text?.length || 0) + (block.label?.length || 0)
    + (block.children || []).reduce((sum, child) => sum + blockLength(child), 0);
}

function Block({ block }: { block: ClinicalBlock }) {
  return <div style={{ marginTop: "0.45rem" }}>
    {block.label && <strong>{block.label}</strong>}
    {block.text && <ClinicalText compact>{block.text}</ClinicalText>}
    {!!block.children?.length && <ul style={{ marginTop: "0.35rem", paddingLeft: "1.2rem" }}>
      {block.children.map((child, index) => <li key={index}><Block block={child} /></li>)}
    </ul>}
  </div>;
}

function OverviewSection({ title, value, preview = 3 }: { title: string; value: unknown; preview?: number }) {
  const [expanded, setExpanded] = useState(false);
  const id = useId();
  const blocks = blocksOf(value);
  if (!blocks.length) return null;
  const longSingleBlock = blocks.length === 1 && blockLength(blocks[0]) > 1400;
  const collapsible = blocks.length > preview || longSingleBlock;
  // Whole blocks only: a dose, limitation or conditional statement is never cut.
  const visible = expanded || !collapsible ? blocks : longSingleBlock ? [] : blocks.slice(0, preview);
  return <section aria-labelledby={id + "-title"} style={{ marginTop: "1rem" }}>
    <h3 id={id + "-title"} style={{ fontSize: "1rem", marginBottom: "0.35rem" }}>{title}</h3>
    <div id={id}>
      {visible.length === 1 ? <Block block={visible[0]} /> : visible.length > 1
        ? <ul style={{ paddingLeft: "1.2rem", marginTop: "0.35rem" }}>
          {visible.map((block, index) => <li key={index}><Block block={block} /></li>)}
        </ul> : null}
    </div>
    {collapsible && <button type="button" className="painel__tema"
      aria-expanded={expanded} aria-controls={id} onClick={() => setExpanded((value) => !value)}
      style={{ marginTop: "0.45rem" }}>
      {expanded ? "Recolher" : longSingleBlock ? "Ler conteúdo" : "Ver restante"}: {title.toLocaleLowerCase("pt-BR")}
    </button>}
  </section>;
}

function stringList(value: unknown): string[] {
  return Array.isArray(value) ? [...new Set(value.filter((item): item is string =>
    typeof item === "string" && Boolean(item.trim())))] : [];
}

function OverviewForDisease({ disease }: { disease: TctOverviewDisease }) {
  const [detail, setDetail] = useState<DiseaseDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const headingId = useId();

  useEffect(() => {
    let active = true;
    setDetail(null);
    setLoading(true);
    setFailed(false);
    api.get<DiseaseDetail>(`/specialty-guides/diseases/${encodeURIComponent(disease.slug)}`)
      .then((response) => {
        if (!active) return;
        if (!response || response.slug !== disease.slug) {
          setFailed(true);
          return;
        }
        setDetail(response);
      })
      .catch(() => { if (active) setFailed(true); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [disease.slug, attempt]);

  const summary = detail?.summary || disease.summary;
  const taxonomy = [areas[detail?.area || disease.area || ""], categories[detail?.category || disease.category || ""]].filter(Boolean);
  const refs = stringList(detail?.source_refs);
  const urls = stringList(detail?.source_urls).filter((url) => /^https?:\/\//i.test(url));
  const hasAdditional = Boolean(detail && (
    blocksOf(detail.epidemiology).length || blocksOf(detail.presentation).length
    || blocksOf(detail.diagnostic_approach).length
  ));

  return <section className="cartao tct-disease-overview" aria-labelledby={headingId}>
    <h2 id={headingId}>O que é {disease.name}?</h2>
    {!!taxonomy.length && <p className="eyebrow">{taxonomy.join(" · ")}</p>}
    {summary && <section aria-label={detail ? "Definição" : "Resumo disponível"}>
      <h3 style={{ fontSize: "1rem" }}>{detail ? "Definição" : "Resumo disponível"}</h3>
      <ClinicalText>{summary}</ClinicalText>
    </section>}
    {loading && <p role="status">Carregando os detalhes publicados do guia…</p>}
    {failed && <div role="status">
      <p>Não foi possível carregar os detalhes do guia. {summary ? "O resumo disponível permanece acima." : "Tente novamente para consultar o conteúdo publicado."}</p>
      <button type="button" className="painel__tema" onClick={() => setAttempt((value) => value + 1)}>Tentar novamente</button>
    </div>}
    {detail && <>
      <OverviewSection title="Epidemiologia e contexto" value={detail.epidemiology} />
      <OverviewSection title="Apresentação clínica" value={detail.presentation} />
      <OverviewSection title="Fundamentos diagnósticos" value={detail.diagnostic_approach} preview={2} />
      {!hasAdditional && <p style={{ color: "var(--texto-secundario)" }}>Este guia não apresenta outros detalhes nestas seções da visão geral.</p>}
      {!!(refs.length || urls.length) && <details style={{ marginTop: "1rem" }}>
        <summary style={{ cursor: "pointer", fontWeight: 600 }}>Fontes desta visão geral</summary>
        {!!refs.length && <ul>{refs.map((reference) => <li key={reference}><ClinicalText compact>{reference}</ClinicalText></li>)}</ul>}
        {!!urls.length && <ul>{urls.map((url, index) => <li key={url}>
          <a href={url} target="_blank" rel="noopener noreferrer">Abrir fonte original {index + 1}</a>
        </li>)}</ul>}
      </details>}
    </>}
    <div className="painel__temas" style={{ marginTop: "1rem" }}>
      <Link className="painel__tema" to={`/doencas/${encodeURIComponent(disease.slug)}`}>Abrir guia completo, condutas e fontes</Link>
    </div>
  </section>;
}

export default function TctDiseaseOverview({ disease }: { disease: TctOverviewDisease }) {
  // Keying the stateful subtree clears expansion, errors and old detail before
  // the next subject paints; cleanup also rejects late responses after unmount.
  return <OverviewForDisease key={disease.slug} disease={disease} />;
}
