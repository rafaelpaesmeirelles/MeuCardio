import { useEffect, useRef, useState, type ReactNode } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, ApiError, PaginaDe } from "../lib/api";
import { Carregando, Erro, Vazio } from "../components/Estado";
import { documentSection, studySection } from "../lib/documentEditorialTaxonomy";
import { exactSearchAnchors } from "../lib/searchAnchors";
import { mergeSearchResults, resultIdentity, type SearchResult, type ClinicalRole, type MatchReason } from "../lib/searchResults";
import TctDiseaseOverview from "../components/TctDiseaseOverview";

type Res = SearchResult;
type PrimaryDisease = { slug: string; name: string; summary: string; area: string; category: string };
type SearchResponse = { results: Res[]; total: number; next_offset?: number | null; por_frente: Record<string, number>; por_secao?: Partial<Record<Secao, number>>; primary_disease?: PrimaryDisease | null; primary_drug?: { slug: string; generic_name: string } | null; supplementary_groups?: Rel[] };
type Drug = { slug: string; generic_name: string; drug_class: string; brand_names?: string[]; commercial_names?: string[] };
type Insight = Drug & {
  mechanism: string | null; presentations: string[]; dosing: Record<string, unknown>;
  renal_adjustment: string | null; hepatic_adjustment: string | null;
  contraindications: string[]; interactions: string[]; monitoring: string[];
  indications: string[]; adverse_effects: string[];
  half_life_hours: number | null; duration_of_action_hours: number | null;
  sbp_reduction_mmhg: number | null; dbp_reduction_mmhg: number | null; bp_evidence_source: string | null;
};
type RelItem = {
  slug: string; titulo: string; subtitulo?: string; rota: string;
  relation_type?: string; relevance_score?: number; confidence?: string;
  provenance_type?: string; review_status?: string;
  relation_scope?: string; relation_method?: string; context_only?: boolean;
  clinical_role?: ClinicalRole; clinical_context?: string | null; match_reasons?: MatchReason[];
  clinical_contexts?: string[]; clinical_roles?: ClinicalRole[]; relation_types?: string[];
};
type Rel = { tipo: string; rotulo?: string; rota_lista: string; total_disponivel?: number; itens: RelItem[] };
type GraphResponse = { grupos: Rel[]; total: number };

const SECOES = {
  geral: ["Visão geral e características", "Fundamentos e conteúdo de referência", "/biblioteca", 10],
  conduta: ["Condutas e protocolos", "Manejo, tratamento e aplicação prática", "/biblioteca", 11],
  diretriz: ["Diretrizes e consensos", "Guidelines, consensos e posicionamentos", "/biblioteca", 12],
  fluxo: ["Fluxogramas", "Algoritmos e caminhos de decisão", "/biblioteca", 13],
  publicacao_original: ["Publicações originais", "Fontes científicas armazenadas no acervo", "/intelligence", 25],
  estudo: ["Estudos", "Literatura original e trabalhos científicos", "/estudos", 20],
  evidencia: ["Evidências", "Recomendações e níveis de evidência", "/evidencias", 30],
  exame: ["Exames", "Diagnóstico, indicação e interpretação", "/exames", 40],
  galeria: ["Galeria clínica", "Imagens e achados relacionados", "/galeria", 50],
  medicamento: ["Medicamentos", "Farmacologia, indicações e segurança", "/medicamentos", 60],
  doenca: ["Guia de doenças", "Condições, diferenciais e fluxos clínicos", "/doencas", 70],
  triagem_sintoma: ["Triagem por sintomas", "Roteiros estruturados de avaliação", "/triagem-sintomas", 80],
  emergencia: ["Emergências", "Protocolos para decisão sob pressão", "/emergencia", 90],
  checklist: ["Checklists", "Execução e continuidade do cuidado", "/checklists", 100],
  caso_clinico: ["Casos clínicos", "Raciocínio e decisão contextual", "/casos-clinicos", 110],
  trilha: ["Trilhas", "Aprendizado guiado e progressivo", "/trilhas", 120],
  material_paciente: ["Material para pacientes", "Comunicação clínica revisada", "/material-paciente", 130],
  calculadora: ["Calculadoras", "Escores e ferramentas clínicas verificadas", "/calculadoras", 140],
} as const;
type Secao = keyof typeof SECOES;
const ROTULOS: Record<string, string> = {
  publicacao_original: "Original científico",
  documento: "Documento", estudo: "Estudo", evidencia: "Evidência", exame: "Exame",
  galeria: "Imagem", fluxograma: "Fluxograma", protocolo: "Protocolo",
  medicamento: "Medicamento", doenca: "Doença", triagem_sintoma: "Triagem",
  emergencia: "Emergência", checklist: "Checklist", caso_clinico: "Caso clínico",
  trilha: "Trilha", material_paciente: "Material do paciente", calculadora: "Calculadora",
};
const GRAPH_ENTITY: Record<string, string> = {
  documento: "documento", galeria: "galeria", exame: "exame", evidencia: "evidencia",
  estudo: "estudo", medicamento: "medicamento", caso_clinico: "caso_clinico",
  trilha: "trilha", checklist: "checklist", material_paciente: "material_paciente",
  emergencia: "protocolo_emergencia", doenca: "doenca", triagem_sintoma: "triagem_sintoma",
  calculadora: "calculadora",
};
const REL_LABELS: Record<string, string> = {
  publicacao_original: "Publicações originais",
  documento: "Documentos", fluxograma: "Fluxogramas", evidencia: "Evidências",
  estudo: "Estudos", medicamento: "Medicamentos", exame: "Exames",
  caso_clinico: "Casos clínicos", trilha: "Trilhas", galeria: "Galeria clínica",
  checklist: "Checklists", material_paciente: "Material para pacientes",
  protocolo_emergencia: "Protocolos de emergência", calculadora: "Calculadoras",
  doenca: "Doenças", triagem_sintoma: "Triagem por sintomas",
};
const norm = (s: string) => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
function secao(r: Res): Secao {
  if (r.secao && r.secao in SECOES) return r.secao as Secao;
  if (r.frente === "estudo") return studySection(r.kind) as Secao;
  const exact = r.frente || r.kind;
  if (exact in SECOES) return exact as Secao;
  const f = norm(exact);
  if (f in SECOES) return f as Secao;
  if (/^(estudo|estudos|study)$/.test(f)) return "estudo";
  if (/^(evidencia|evidencias|evidence)$/.test(f)) return "evidencia";
  if (/^(exame|exames|lab test|lab tests)$/.test(f)) return "exame";
  if (/^(galeria|imagem|imagens|gallery)$/.test(f)) return "galeria";
  return documentSection(r.kind) as Secao;
}
function rota(r: Res): string {
  const frente = r.frente || "documento";
  if (frente === "publicacao_original") return `/intelligence?fonte=${encodeURIComponent(r.slug)}`;
  if (frente === "estudo") return `/estudos/${encodeURIComponent(r.slug)}`;
  if (frente === "documento") return `/biblioteca/${encodeURIComponent(r.slug)}`;
  if (frente === "medicamento") return `/medicamentos?slug=${encodeURIComponent(r.slug)}`;
  if (frente === "emergencia") return `/emergencia?protocolo=${encodeURIComponent(r.slug)}`;
  if (frente === "triagem_sintoma") return `/triagem-sintomas?slug=${encodeURIComponent(r.slug)}`;
  if (frente === "calculadora") return `/calculadoras/${encodeURIComponent(r.slug)}`;
  return `${SECOES[secao(r)][2]}/${r.slug}`;
}

function graphEntity(r: Res): string | null {
  if ((r.frente || "documento") === "documento" && r.kind === "fluxograma") return "fluxograma";
  return GRAPH_ENTITY[r.frente || "documento"] ?? null;
}

function graphIdentity(r: Res): string {
  return `${graphEntity(r) ?? r.frente ?? "documento"}:${r.slug}`;
}

function mergeGraphGroups(respostas: GraphResponse[], resultados: Res[]): Rel[] {
  const visiveis = new Set(resultados.map(graphIdentity));
  const grupos = new Map<string, Rel>();
  for (const resposta of respostas) {
    for (const grupo of resposta.grupos ?? []) {
      const atual = grupos.get(grupo.tipo) ?? {
        tipo: grupo.tipo,
        rotulo: grupo.rotulo,
        rota_lista: grupo.rota_lista,
        total_disponivel: 0,
        itens: [],
      };
      if (!atual.rotulo && grupo.rotulo) atual.rotulo = grupo.rotulo;
      for (const item of grupo.itens ?? []) {
        if (visiveis.has(`${grupo.tipo}:${item.slug}`)) continue;
        const existing = atual.itens.find((candidate) => candidate.slug === item.slug);
        if (!existing) atual.itens.push({ ...item });
        else {
          const qualify = (value: RelItem): Res => ({ ...value, title: value.titulo, kind: grupo.tipo, frente: grupo.tipo, theme: null, snippet: "" });
          const merged = mergeSearchResults([qualify(existing)], [qualify(item)])[0];
          Object.assign(existing, {
            clinical_contexts: merged.clinical_contexts, clinical_roles: merged.clinical_roles,
            relation_types: merged.relation_types, match_reasons: merged.match_reasons,
            context_only: merged.context_only,
          });
        }
      }
      atual.total_disponivel = Math.max(atual.total_disponivel ?? 0, grupo.total_disponivel ?? atual.itens.length);
      grupos.set(grupo.tipo, atual);
    }
  }
  return [...grupos.values()].filter((grupo) => grupo.itens.length > 0);
}

function connectionLabel(item: Res): string | null {
  const labels: Record<string, string> = {
    contraindicated_in: "Contraindicação relacionada — verificar o contexto",
    contraindicated_with: "Contraindicação de associação — verificar o contexto",
    interacts_with: "Interação medicamentosa relacionada",
    monitor_with: "Monitorização relacionada",
    diagnosed_by: "Investigação diagnóstica relacionada",
    differential_for: "Diagnóstico diferencial relacionado",
    supported_by: "Fundamentação científica relacionada",
    studied_in: "Estudo relacionado ao assunto",
    mentioned_in: "Assunto citado neste conteúdo",
    patient_education_for: "Orientação ao paciente sobre o assunto",
  };
  return item.relation_type ? labels[item.relation_type] ?? null : null;
}

const CLINICAL_ROLES: Record<ClinicalRole, string> = {
  direct: "Relação com o assunto",
  conditional: "Relação condicionada ao contexto",
  comparison: "Comparação ou diagnóstico diferencial",
  mention: "Menção ao assunto",
};

function ClinicalQualifications({ item }: { item: Res }) {
  const contexts = item.clinical_contexts ?? (item.clinical_context ? [item.clinical_context] : []);
  const roles = item.clinical_roles ?? (item.clinical_role ? [item.clinical_role] : []);
  const relations = item.relation_types ?? (item.relation_type ? [item.relation_type] : []);
  const labels = [...new Set(relations.map((relation_type) => connectionLabel({ ...item, relation_type })).filter(Boolean))];
  return <div className="tct-qualifications">
    {roles.map((role) => <span className="selo" key={role}>{CLINICAL_ROLES[role]}</span>)}
    {item.context_only && <span className="selo">Mesmo tema clínico</span>}
    {labels.map((label) => <p key={label}>{label}</p>)}
    {contexts.map((context) => <p className="tct-clinical-context" key={context}>{context}</p>)}
  </div>;
}

function MatchReasons({ item }: { item: Res }) {
  const contexts = new Set([...(item.clinical_contexts ?? []), item.clinical_context]);
  const descriptions = [...new Set((item.match_reasons ?? []).map((reason) => reason.description)
    .filter((description) => Boolean(description) && !contexts.has(description)))];
  return descriptions.length > 0 ? <div className="tct-match-reasons"><span>Por que aparece nesta busca:</span><ul>{descriptions.map((description) => <li key={description}>{description}</li>)}</ul></div> : null;
}

function Snippet({ texto }: { texto: string }) {
  return <>{texto.split(/<\/?mark>/i).map((p, i) => i % 2 ? <mark key={i}>{p}</mark> : p)}</>;
}
function txt(v: unknown): string {
  if (v == null) return "";
  if (typeof v !== "object") return String(v);
  if (Array.isArray(v)) return v.map(txt).filter(Boolean).join(" · ");
  return Object.entries(v as Record<string, unknown>).map(([k, x]) => `${k.replaceAll("_", " ")}: ${txt(x)}`).filter((x) => !x.endsWith(": ")).join("\n");
}
function Lista({ itens, vazio = "Sem dado estruturado publicado." }: { itens: string[]; vazio?: string }) {
  return itens.length ? <ul>{itens.map((x, i) => <li key={`${i}-${x.slice(0, 20)}`}>{x}</li>)}</ul> : <p>{vazio}</p>;
}
function Topico({ id, nome, titulo, children }: { id: string; nome: string; titulo: string; children: ReactNode }) {
  return <article id={id} className="cartao tct-topic"><p className="eyebrow">{nome}</p><h3>{titulo}</h3>{children}</article>;
}
function PainelDrug({ d }: { d: Insight }) {
  const dose = txt(d.dosing);
  return <section className="cartao">
    <header className="tct-head"><div><p className="eyebrow">Medicamento identificado</p><h2>{d.generic_name}</h2><p>{d.drug_class}</p></div><Link to={`/medicamentos?slug=${d.slug}`}>Verbete completo →</Link></header>
    <nav className="tct-nav" aria-label="Tópicos do medicamento">{[["caracteristicas", "Características"], ["dose", "Posologia e potência"], ["indicacoes", "Indicações"], ["seguranca", "Segurança"]].map(([id, nome]) => <a className="selo" href={`#${id}`} key={id}>{nome}</a>)}</nav>
    <div className="grade grade--2 tct-grid">
      <Topico id="caracteristicas" nome="Características" titulo="Perfil farmacológico">
        <p><strong>Classe:</strong> {d.drug_class}</p>{d.mechanism && <p>{d.mechanism}</p>}
        {d.half_life_hours != null && <p><strong>Meia-vida:</strong> {d.half_life_hours} h</p>}{d.duration_of_action_hours != null && <p><strong>Ação:</strong> {d.duration_of_action_hours} h</p>}{d.presentations.length > 0 && <p><strong>Apresentações:</strong> {d.presentations.join(" · ")}</p>}
      </Topico>
      <Topico id="dose" nome="Posologia e potência" titulo="Dose e efeito publicados">
        <p className="tct-pre">{dose || "Sem posologia estruturada publicada."}</p>
        {(d.sbp_reduction_mmhg != null || d.dbp_reduction_mmhg != null) && <p><strong>PAS:</strong> {d.sbp_reduction_mmhg ?? "—"} mmHg · <strong>PAD:</strong> {d.dbp_reduction_mmhg ?? "—"} mmHg</p>}{d.bp_evidence_source && <small>{d.bp_evidence_source}</small>}
      </Topico>
      <Topico id="indicacoes" nome="Indicações" titulo="Onde se encaixa"><Lista itens={d.indications} /></Topico>
      <Topico id="seguranca" nome="Segurança e monitorização" titulo="O que verificar">
        <Lista itens={d.monitoring} />{d.renal_adjustment && <p><strong>Ajuste renal:</strong> {d.renal_adjustment}</p>}{d.hepatic_adjustment && <p><strong>Ajuste hepático:</strong> {d.hepatic_adjustment}</p>}
        {[["Contraindicações", d.contraindications], ["Interações", d.interactions], ["Efeitos adversos", d.adverse_effects]].map(([nome, itens]) => (itens as string[]).length > 0 && <details key={nome as string}><summary>{nome as string}</summary><Lista itens={itens as string[]} /></details>)}
      </Topico>
    </div>
  </section>;
}

type SearchFilters = { frente: string; secao: string };

export default function Busca() {
  const [params, setParams] = useSearchParams();
  const inicial = params.get("q") ?? params.get("tema")?.replaceAll("-", " ") ?? "";
  const frente = params.get("frente") ?? "";
  const section = params.get("secao") ?? "";
  const filters = { frente: frente in FILTER_FRONTS ? frente : "", secao: section in SECOES ? section : "" };
  // The URL owns the subject and server filters, including Back/Forward. Other
  // parameters keep the current draft, loaded results and pagination intact.
  return <BuscaAssunto key={JSON.stringify([inicial.trim(), filters.frente, filters.secao])}
    inicial={inicial} filters={filters} alterarConsulta={(valor, novosFiltros) => {
      const next = new URLSearchParams(params);
      next.delete("tema");
      if (valor) next.set("q", valor); else next.delete("q");
      const selected = novosFiltros ?? { frente: "", secao: "" };
      for (const key of ["frente", "secao"] as const) {
        if (selected[key]) next.set(key, selected[key]); else next.delete(key);
      }
      setParams(next);
    }} />;
}

const FILTER_FRONTS: Record<string, string> = {
  documento: "Documentos", publicacao_original: "Publicações originais", estudo: "Estudos",
  evidencia: "Evidências", exame: "Exames", galeria: "Galeria clínica", medicamento: "Medicamentos",
  doenca: "Guia de doenças", triagem_sintoma: "Triagem por sintomas", emergencia: "Emergências",
  checklist: "Checklists", caso_clinico: "Casos clínicos", trilha: "Trilhas",
  material_paciente: "Material para pacientes", calculadora: "Calculadoras",
};

function searchQuery(subject: string, filters: SearchFilters, offset?: number) {
  const query = new URLSearchParams({ q: subject, limit: "100" });
  if (filters.frente) query.set("frente", filters.frente);
  if (filters.secao) query.set("secao", filters.secao);
  if (offset !== undefined) query.set("offset", String(offset));
  return `/search?${query}`;
}

// The main list keeps qualifications from any complementary duplicate. The
// complement remains separate because its API does not supply a relevance order.
function preserveComplementQualifications(results: Res[], groups: Rel[]): Res[] {
  return mergeSearchResults([], results.map((result) => {
    let merged = result;
    for (const group of groups) for (const related of group.itens) {
      if (`${group.tipo}:${related.slug}` !== graphIdentity(result)) continue;
      merged = mergeSearchResults([merged], [{
        ...result, clinical_context: related.clinical_context, clinical_role: related.clinical_role,
        clinical_contexts: related.clinical_contexts, clinical_roles: related.clinical_roles,
        relation_type: related.relation_type, relation_types: related.relation_types,
        context_only: related.context_only, match_reasons: related.match_reasons,
      }])[0];
    }
    return merged;
  }));
}

function BuscaAssunto({ inicial, filters, alterarConsulta }: {
  inicial: string; filters: SearchFilters;
  alterarConsulta: (valor: string, filtros?: SearchFilters) => void;
}) {
  const [q, setQ] = useState(inicial), [assunto, setAssunto] = useState(inicial.trim());
  const [res, setRes] = useState<Res[] | null>(null), [drug, setDrug] = useState<Insight | null>(null);
  const [primaryDisease, setPrimaryDisease] = useState<PrimaryDisease | null>(null);
  const [rel, setRel] = useState<Rel[]>([]);
  const [total, setTotal] = useState(0), [nextOffset, setNextOffset] = useState<number | null>(null);
  const [loading, setLoading] = useState(false), [loadingMore, setLoadingMore] = useState(false);
  const [erro, setErro] = useState(""), [aviso, setAviso] = useState(""), [pageError, setPageError] = useState("");
  const seq = useRef(0), pendingSearch = useRef(false), pendingPage = useRef(false);
  const controller = useRef<AbortController | null>(null);
  const complements = useRef<Rel[]>([]);

  async function buscar(valor: string) {
    const termo = valor.trim(); if (termo.length < 2 || pendingSearch.current) return;
    pendingSearch.current = true;
    const id = ++seq.current;
    controller.current?.abort();
    const request = new AbortController(); controller.current = request;
    const options = { signal: request.signal };
    setLoading(true); setLoadingMore(false); setErro(""); setAviso(""); setPageError("");
    setRes(null); setDrug(null); setPrimaryDisease(null); setRel([]); complements.current = [];
    setTotal(0); setNextOffset(null); pendingPage.current = false; setAssunto(termo);
    const [s, ds] = await Promise.allSettled([
      api.get<SearchResponse>(searchQuery(termo, filters), options),
      api.get<PaginaDe<Drug>>(`/drugs?q=${encodeURIComponent(termo)}`, options),
    ]);
    if (id !== seq.current) return;
    if (s.status === "rejected") {
      setErro(s.reason instanceof ApiError ? s.reason.message : "Não foi possível consultar o conteúdo.");
      pendingSearch.current = false; setLoading(false); return;
    }
    const itens = mergeSearchResults([], s.value.results);
    const disease = s.value.primary_disease ?? null;
    setRes(itens); setPrimaryDisease(disease); setTotal(s.value.total ?? itens.length);
    setNextOffset(s.value.next_offset ?? null);
    let medicamentoSlug: string | null = s.value.primary_drug?.slug ?? null;
    if (ds.status === "rejected") setAviso("Conteúdo carregado; catálogo de medicamentos indisponível.");
    else {
      const n = norm(termo), fortes = ds.value.items.filter((d) => norm(d.generic_name) === n || norm(d.slug) === n || norm(d.generic_name).startsWith(`${n} `) || d.brand_names?.some((marca) => norm(marca) === n) || d.commercial_names?.some((marca) => norm(marca) === n));
      if (!medicamentoSlug && fortes.length === 1) medicamentoSlug = fortes[0].slug;
    }
    if (!disease && medicamentoSlug) {
      try {
        const d = await api.get<Insight>(`/drug-insights/${encodeURIComponent(medicamentoSlug)}`, options);
        if (id === seq.current) setDrug(d);
      } catch (e) { if (id === seq.current) setAviso(e instanceof ApiError ? e.message : "Resumo farmacológico indisponível."); }
      if (id !== seq.current) return;
    }
    const fontesRelacionadas: GraphResponse[] = [];
    if (disease) {
      // Published content is already in the complete, paginated /search list.
      // These guide suggestions launch a new search; they are not extra records.
      const grupos = s.value.supplementary_groups ?? [];
      fontesRelacionadas.push({ grupos, total: grupos.reduce((count, group) => count + group.itens.length, 0) });
    } else if (!medicamentoSlug) {
      // Generic exact identities still have a separate ecosystem contract.
      // Never expand a merely lexical hit or mix unordered neighbours into results.
      const exatos = exactSearchAnchors(itens, termo);
      let ecossistemaEntidade: GraphResponse | null = null;
      if (exatos.length === 1 && graphEntity(exatos[0])) {
        try {
          const query = new URLSearchParams({ entity_type: graphEntity(exatos[0])!, slug: exatos[0].slug });
          ecossistemaEntidade = await api.get<GraphResponse>(`/relacionados/ecossistema?${query.toString()}`, options);
        } catch (e) { if (id === seq.current) setAviso(e instanceof ApiError ? e.message : "Conexões do item temporariamente indisponíveis."); }
        if (id !== seq.current) return;
      }
      if (ecossistemaEntidade) fontesRelacionadas.push(ecossistemaEntidade);
      else {
        const candidatos = exatos.filter((item) => graphEntity(item));
        const conexoes = await Promise.allSettled(candidatos.map((item) => {
          const query = new URLSearchParams({ entity_type: graphEntity(item) as string, slug: item.slug, limite_por_tipo: "6" });
          return api.get<GraphResponse>(`/grafo/relacionados?${query.toString()}`, options);
        }));
        if (id !== seq.current) return;
        fontesRelacionadas.push(...conexoes.flatMap((x) => x.status === "fulfilled" && x.value.total > 0 ? [x.value] : []));
        if (conexoes.length > 0 && conexoes.every((x) => x.status === "rejected")) setAviso("Conteúdo encontrado; as conexões verificáveis estão temporariamente indisponíveis.");
      }
    }
    complements.current = fontesRelacionadas.flatMap((response) => response.grupos);
    setRes(preserveComplementQualifications(itens, complements.current));
    setRel(mergeGraphGroups(fontesRelacionadas, itens));
    pendingSearch.current = false; setLoading(false);
  }

  async function carregarMais() {
    if (nextOffset == null || pendingPage.current || assunto.length < 2) return;
    const id = seq.current;
    pendingPage.current = true; setLoadingMore(true); setPageError("");
    try {
      const pagina = await api.get<SearchResponse>(searchQuery(assunto, filters, nextOffset), { signal: controller.current?.signal });
      if (id !== seq.current) return;
      setRes((current) => preserveComplementQualifications(mergeSearchResults(current ?? [], pagina.results), complements.current));
      setNextOffset(pagina.next_offset ?? null);
      setTotal(pagina.total);
      setRel((current) => mergeGraphGroups([{ grupos: current, total: 0 }], pagina.results));
    } catch (e) {
      if (id === seq.current) setPageError(e instanceof ApiError ? e.message : "Não foi possível carregar a próxima página. Tente novamente.");
    } finally {
      if (id === seq.current) { pendingPage.current = false; setLoadingMore(false); }
    }
  }

  useEffect(() => {
    let active = true;
    // StrictMode replay cannot duplicate a request. Cleanup rejects and aborts
    // every stage of the old subject/filter, including insight and pagination.
    queueMicrotask(() => { if (active && inicial.trim().length > 1) void buscar(inicial); });
    return () => { active = false; seq.current += 1; controller.current?.abort(); };
    // The keyed subtree owns exactly one submitted subject and filter pair.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function enviarConsulta() {
    const termo = q.trim(); if (termo.length < 2) return;
    if (termo === inicial.trim()) void buscar(termo); else alterarConsulta(termo);
  }

  const complementarySections = [
    { guided: true, groups: rel.map((group) => ({ ...group, itens: group.itens.filter((item) => item.relation_method === "SpecialtyDisease.tests") })).filter((group) => group.itens.length > 0) },
    { guided: false, groups: rel.map((group) => ({ ...group, itens: group.itens.filter((item) => item.relation_method !== "SpecialtyDisease.tests") })).filter((group) => group.itens.length > 0) },
  ];

  return <main className="tct-page">
    <header className="cartao tct-hero">
      <p className="eyebrow">Tudo com Tudo</p><h1>{assunto ? `Tudo sobre ${assunto}` : "Um assunto, todas as conexões"}</h1>
      <p>Uma lista de conteúdos em ordem de relevância para o assunto pesquisado.</p>
      <form className="tct-search" role="search" onSubmit={(e) => { e.preventDefault(); enviarConsulta(); }}>
        <input type="search" aria-label="Assunto" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Ex.: olmesartana, fibrilação atrial…" />
        <button className="botao" disabled={q.trim().length < 2 || loading}>{loading ? "Buscando…" : "Conectar"}</button>
      </form>
      {assunto.length >= 2 && <div className="tct-filters" aria-label="Filtros da lista completa">
        <label>Frente de conhecimento<select aria-label="Frente de conhecimento" value={filters.frente} onChange={(e) => alterarConsulta(assunto, { frente: e.target.value, secao: "" })}>
          <option value="">Todas as frentes</option>{Object.entries(FILTER_FRONTS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </select></label>
        <label>Seção editorial<select aria-label="Seção editorial" value={filters.secao} onChange={(e) => alterarConsulta(assunto, { ...filters, secao: e.target.value })}>
          <option value="">Todas as seções</option>{Object.entries(SECOES).map(([value, [label]]) => <option key={value} value={value}>{label}</option>)}
        </select></label>
        {(filters.frente || filters.secao) && <button className="botao botao--secundario" type="button" onClick={() => alterarConsulta(assunto, { frente: "", secao: "" })}>Limpar filtros</button>}
      </div>}
    </header>
    {erro && <Erro mensagem={erro} />}{aviso && <p className="cartao" role="status">{aviso}</p>}{loading && <Carregando texto="Conectando o conhecimento…" />}
    {!loading && primaryDisease && <TctDiseaseOverview disease={primaryDisease} />}
    {!loading && drug && <PainelDrug d={drug} />}
    {!loading && res && <section className="cartao" aria-label="Resultados por relevância">
      <header className="tct-head"><div><p className="eyebrow">Conteúdo encontrado</p><h2>Resultados por relevância</h2>
        <p role="status">{res.length} de {total} resultados carregados{filters.frente || filters.secao ? " com os filtros selecionados" : ""}</p>
      </div></header>
      <ol className="tct-results" aria-label="Lista de conteúdos por relevância">
        {res.map((r) => <li key={resultIdentity(r)}><article className="tct-row">
          <small>{ROTULOS[r.frente || r.kind] ?? r.kind} · {SECOES[secao(r)][0]}{r.ano ? ` · ${r.ano}` : ""}</small>
          <ClinicalQualifications item={r} />
          <Link className="tct-result-title" to={rota(r)}>{r.title}</Link>
          {r.frente === "doenca" && r.slug === primaryDisease?.slug && <span className="selo">Doença principal</span>}
          {r.snippet && r.snippet.replace(/<\/?mark>/gi, "") !== r.title && <p><Snippet texto={r.snippet} /></p>}
          <MatchReasons item={r} />
        </article></li>)}
      </ol>
      {res.length === 0 && total === 0 && <Vazio titulo={filters.frente || filters.secao ? "Nenhum conteúdo com estes filtros" : "Nada encontrado"} acao={filters.frente || filters.secao ? "Ajuste ou limpe os filtros para explorar o assunto." : "Tente o princípio ativo ou um sinônimo clínico."} />}
      {pageError && <p role="alert">{pageError}</p>}
      {nextOffset != null && <div className="tct-pagination"><button className="botao botao--secundario" type="button" disabled={loadingMore} onClick={() => void carregarMais()}>{loadingMore ? "Conectando mais conteúdo…" : pageError ? "Tentar carregar mais novamente" : "Carregar mais resultados"}</button></div>}
    </section>}
    {!loading && complementarySections.filter(({ groups }) => groups.length > 0).map(({ guided, groups }) => <section className="cartao" key={guided ? "guided" : "connected"} aria-label={guided ? "Pesquisas orientadas pelo guia" : "Conexões complementares do item"}>
      <h2>{guided ? "Pesquisas orientadas pelo guia" : "Conexões complementares do item identificado"}</h2>
      <p>{guided ? "Termos de exames citados no guia para explorar o acervo. Estas pesquisas não são verbetes adicionais e não entram na contagem de resultados." : "Relações do item identificado no ecossistema, apresentadas separadamente da lista ordenada da busca."}</p>
      {groups.map((g) => <div className="tct-group" key={g.tipo}>
        <h3>{g.rotulo || REL_LABELS[g.tipo] || g.tipo}</h3>
        {!guided && g.total_disponivel != null && g.total_disponivel > g.itens.length && <p>Exibindo {g.itens.length} de {g.total_disponivel} conexões disponíveis.</p>}
        {g.itens.map((x) => {
          const related: Res = { ...x, title: x.titulo, kind: g.tipo, frente: g.tipo, theme: null, snippet: "" };
          return <article className="tct-row" key={`${g.tipo}:${x.slug}`}>
            {guided ? <span className="selo">Pesquisa orientada</span> : <><small>{x.context_only || x.relation_scope === "structured_clinical_topic" ? "Mesmo tema clínico" : x.relation_scope === "clinical_match" ? "Relação contextual determinística" : "Relação direta"}</small><ClinicalQualifications item={related} /></>}
            <Link className="tct-result-title" to={x.rota}>{x.titulo}</Link>
            {x.subtitulo && <p>{x.subtitulo}</p>}<MatchReasons item={related} />
          </article>;
        })}
      </div>)}
    </section>)}
  </main>;
}
