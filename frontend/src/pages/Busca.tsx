import { useEffect, useRef, useState, type ReactNode } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, ApiError, PaginaDe } from "../lib/api";
import { Carregando, Erro, Vazio } from "../components/Estado";

type Res = { slug: string; title: string; kind: string; frente?: string; theme: string | null; snippet: string; ano?: number; rank?: number };
type PrimaryDisease = { slug: string; name: string; summary: string; area: string; category: string };
type SearchResponse = { results: Res[]; total: number; next_offset?: number | null; por_frente: Record<string, number>; primary_disease?: PrimaryDisease | null };
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
};
type Rel = { tipo: string; rotulo?: string; rota_lista: string; total_disponivel?: number; itens: RelItem[] };
type GraphResponse = { grupos: Rel[]; total: number };

const SECOES = {
  geral: ["Visão geral e características", "Fundamentos e conteúdo de referência", "/biblioteca", 10],
  conduta: ["Condutas e protocolos", "Manejo, tratamento e aplicação prática", "/biblioteca", 11],
  diretriz: ["Diretrizes e consensos", "Guidelines, consensos e posicionamentos", "/biblioteca", 12],
  fluxo: ["Fluxogramas", "Algoritmos e caminhos de decisão", "/biblioteca", 13],
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
const ORDEM_DOENCA: Record<Secao, number> = {
  doenca: 10,
  triagem_sintoma: 20,
  exame: 30,
  galeria: 40,
  calculadora: 50,
  fluxo: 60,
  emergencia: 70,
  checklist: 80,
  conduta: 90,
  medicamento: 100,
  diretriz: 110,
  evidencia: 120,
  estudo: 130,
  geral: 140,
  caso_clinico: 150,
  trilha: 160,
  material_paciente: 170,
};
const ROTULOS: Record<string, string> = {
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
  documento: "Documentos", fluxograma: "Fluxogramas", evidencia: "Evidências",
  estudo: "Estudos", medicamento: "Medicamentos", exame: "Exames",
  caso_clinico: "Casos clínicos", trilha: "Trilhas", galeria: "Galeria clínica",
  checklist: "Checklists", material_paciente: "Material para pacientes",
  protocolo_emergencia: "Protocolos de emergência", calculadora: "Calculadoras",
  doenca: "Doenças", triagem_sintoma: "Triagem por sintomas",
};
const norm = (s: string) => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
function secao(r: Res): Secao {
  const f = norm(r.frente || r.kind);
  if (f in SECOES) return f as Secao;
  if (/^(estudo|estudos|study)$/.test(f)) return "estudo";
  if (/^(evidencia|evidencias|evidence)$/.test(f)) return "evidencia";
  if (/^(exame|exames|lab test|lab tests)$/.test(f)) return "exame";
  if (/^(galeria|imagem|imagens|gallery)$/.test(f)) return "galeria";
  const t = norm(`${r.kind} ${r.title}`);
  if (/\b(flux|algoritm|flowchart)/.test(t)) return "fluxo";
  if (/\b(diretr|guideline|consens|posicionamento)/.test(t)) return "diretriz";
  if (/\b(protoc|condut|manejo|tratamento|terapia|abordagem)/.test(t)) return "conduta";
  return "geral";
}
function rota(r: Res): string {
  const frente = r.frente || "documento";
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

function mergeGraphGroups(respostas: GraphResponse[], resultados: Res[]): Rel[] {
  const visiveis = new Set(resultados.map((r) => `${graphEntity(r)}:${r.slug}`));
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
      const existentes = new Set(atual.itens.map((item) => item.slug));
      for (const item of grupo.itens ?? []) {
        if (visiveis.has(`${grupo.tipo}:${item.slug}`) || existentes.has(item.slug)) continue;
        atual.itens.push(item);
        existentes.add(item.slug);
      }
      atual.total_disponivel = Math.max(atual.total_disponivel ?? 0, grupo.total_disponivel ?? atual.itens.length);
      grupos.set(grupo.tipo, atual);
    }
  }
  return [...grupos.values()].filter((grupo) => grupo.itens.length > 0);
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

function PainelDoenca({ disease }: { disease: PrimaryDisease }) {
  return <section className="cartao">
    <header className="tct-head"><div><p className="eyebrow">Definição clínica</p><h2>{disease.name}</h2><p>{disease.category} · {disease.area}</p></div><Link to={`/doencas/${encodeURIComponent(disease.slug)}`}>Abrir guia completo →</Link></header>
    <article className="cartao tct-topic"><p className="eyebrow">O que é</p><h3>Definição da doença</h3><p>{disease.summary}</p></article>
  </section>;
}

export default function Busca() {
  const [params, setParams] = useSearchParams();
  const inicial = params.get("q") ?? params.get("tema")?.replaceAll("-", " ") ?? "";
  const [q, setQ] = useState(inicial), [assunto, setAssunto] = useState(inicial.trim());
  const [res, setRes] = useState<Res[] | null>(null), [drug, setDrug] = useState<Insight | null>(null), [primaryDisease, setPrimaryDisease] = useState<PrimaryDisease | null>(null), [rel, setRel] = useState<Rel[]>([]);
  const [total, setTotal] = useState(0), [nextOffset, setNextOffset] = useState<number | null>(null);
  const [porFrente, setPorFrente] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false), [loadingMore, setLoadingMore] = useState(false), [erro, setErro] = useState(""), [aviso, setAviso] = useState("");
  const seq = useRef(0);

  async function buscar(valor: string) {
    const termo = valor.trim(); if (termo.length < 2) return;
    const id = ++seq.current;
    setLoading(true); setErro(""); setAviso(""); setDrug(null); setPrimaryDisease(null); setRel([]); setTotal(0); setNextOffset(null); setPorFrente({}); setAssunto(termo); setParams({ q: termo }, { replace: true });
    const [s, ds] = await Promise.allSettled([
      api.get<SearchResponse>(`/search?q=${encodeURIComponent(termo)}&limit=100`),
      api.get<PaginaDe<Drug>>(`/drugs?q=${encodeURIComponent(termo)}`),
    ]);
    if (id !== seq.current) return;
    if (s.status === "rejected") { setRes(null); setErro(s.reason instanceof ApiError ? s.reason.message : "Não foi possível consultar o conteúdo."); setLoading(false); return; }
    const itens = s.value.results; const disease = s.value.primary_disease ?? null; setRes(itens); setPrimaryDisease(disease); setTotal(s.value.total ?? itens.length); setNextOffset(s.value.next_offset ?? null); setPorFrente(s.value.por_frente ?? {});
    let medicamentoSlug: string | null = null;
    if (ds.status === "rejected") setAviso("Conteúdo carregado; catálogo de medicamentos indisponível.");
    else {
      const n = norm(termo), fortes = ds.value.items.filter((d) => norm(d.generic_name) === n || norm(d.slug) === n || norm(d.generic_name).startsWith(`${n} `) || d.brand_names?.some((marca) => norm(marca) === n) || d.commercial_names?.some((marca) => norm(marca) === n));
      if (fortes.length === 1) {
        medicamentoSlug = fortes[0].slug;
        try { const d = await api.get<Insight>(`/drug-insights/${fortes[0].slug}`); if (id === seq.current) setDrug(d); }
        catch (e) { if (id === seq.current) setAviso(e instanceof ApiError ? e.message : "Resumo farmacológico indisponível."); }
      }
    }
    let ecossistemaDoenca: GraphResponse | null = null;
    let ecossistemaEntidade: GraphResponse | null = null;
    if (disease) {
      try { ecossistemaDoenca = await api.get<GraphResponse>(`/relacionados/doenca/${encodeURIComponent(disease.slug)}`); }
      catch (e) { if (id === seq.current) setAviso((atual) => atual || (e instanceof ApiError ? e.message : "Ecossistema clínico da doença temporariamente indisponível.")); }
      if (id !== seq.current) return;
    }
    let ecossistemaMedicamento: GraphResponse | null = null;
    if (!disease && medicamentoSlug) {
      try { ecossistemaMedicamento = await api.get<GraphResponse>(`/relacionados/medicamento/${encodeURIComponent(medicamentoSlug)}`); }
      catch (e) { if (id === seq.current) setAviso((atual) => atual || (e instanceof ApiError ? e.message : "Ecossistema clínico do medicamento temporariamente indisponível.")); }
      if (id !== seq.current) return;
    }
    if (!disease && !medicamentoSlug) {
      const termoNormalizado = norm(termo);
      const exatos = itens.filter((item) => norm(item.title) === termoNormalizado || norm(item.slug.replaceAll("-", " ")) === termoNormalizado);
      if (exatos.length === 1) {
        const entidade = graphEntity(exatos[0]);
        if (entidade) {
          try {
            const query = new URLSearchParams({ entity_type: entidade, slug: exatos[0].slug });
            ecossistemaEntidade = await api.get<GraphResponse>(`/relacionados/ecossistema?${query.toString()}`);
          } catch (e) {
            if (id === seq.current) setAviso((atual) => atual || (e instanceof ApiError ? e.message : "Ecossistema do item temporariamente indisponível."));
          }
          if (id !== seq.current) return;
        }
      }
    }
    const fontesRelacionadas: GraphResponse[] = [];
    if (itens.length > 0) {
      // Arestas diretas continuam prioritárias. O ecossistema da doença
      // complementa com tema estruturado e match contextual auditável.
      const candidatos: Res[] = [];
      const frentesVisitadas = new Set<string>();
      for (const item of itens) {
        const entidade = graphEntity(item);
        if (!entidade || frentesVisitadas.has(entidade)) continue;
        candidatos.push(item);
        frentesVisitadas.add(entidade);
        if (candidatos.length === 8) break;
      }
      const conexoes = await Promise.allSettled(candidatos.map((item) => {
        const query = new URLSearchParams({ entity_type: graphEntity(item) as string, slug: item.slug, limite_por_tipo: "6" });
        return api.get<GraphResponse>(`/grafo/relacionados?${query.toString()}`);
      }));
      if (id !== seq.current) return;
      fontesRelacionadas.push(...conexoes.flatMap((x) => x.status === "fulfilled" && x.value.total > 0 ? [x.value] : []));
      if (conexoes.length > 0 && conexoes.every((x) => x.status === "rejected")) {
        setAviso((atual) => atual || "Conteúdo encontrado; as conexões verificáveis estão temporariamente indisponíveis.");
      }
    }
    if (ecossistemaDoenca?.total) fontesRelacionadas.push(ecossistemaDoenca);
    if (ecossistemaMedicamento?.total) fontesRelacionadas.push(ecossistemaMedicamento);
    if (ecossistemaEntidade?.total) fontesRelacionadas.push(ecossistemaEntidade);
    setRel(mergeGraphGroups(fontesRelacionadas, itens));
    if (id === seq.current) setLoading(false);
  }

  async function carregarMais() {
    if (nextOffset == null || loadingMore || assunto.length < 2) return;
    const id = seq.current;
    setLoadingMore(true);
    try {
      const pagina = await api.get<SearchResponse>(`/search?q=${encodeURIComponent(assunto)}&limit=100&offset=${nextOffset}`);
      if (id !== seq.current) return;
      setRes((atuais) => {
        const mapa = new Map((atuais ?? []).map((item) => [`${item.frente || item.kind}:${item.slug}`, item]));
        pagina.results.forEach((item) => mapa.set(`${item.frente || item.kind}:${item.slug}`, item));
        return [...mapa.values()];
      });
      setNextOffset(pagina.next_offset ?? null);
    } catch (e) {
      if (id === seq.current) setAviso(e instanceof ApiError ? e.message : "Não foi possível carregar a próxima página.");
    } finally {
      if (id === seq.current) setLoadingMore(false);
    }
  }
  useEffect(() => { if (inicial.trim().length > 1) void buscar(inicial); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, []);

  const grupos = new Map<Secao, Res[]>();
  (res ?? []).filter((r) => !primaryDisease || r.frente !== "doenca" || r.slug !== primaryDisease.slug).forEach((r) => { const s = secao(r); grupos.set(s, [...(grupos.get(s) ?? []), r]); });
  const ordenados = [...grupos].sort((a, b) => primaryDisease ? ORDEM_DOENCA[a[0]] - ORDEM_DOENCA[b[0]] : Number(SECOES[a[0]][3]) - Number(SECOES[b[0]][3]));
  const timeline = (res ?? []).filter((r) => ["estudo", "evidencia"].includes(secao(r)) && r.ano).sort((a, b) => (b.ano ?? 0) - (a.ano ?? 0));

  return <main className="tct-page">
    <header className="cartao tct-hero"><p className="eyebrow">Tudo com Tudo</p><h1>{assunto ? `Tudo sobre ${assunto}` : "Um assunto, todas as conexões"}</h1><p>Conteúdo relacionado ao assunto, organizado por frente de conhecimento.</p>
      <form className="tct-search" role="search" onSubmit={(e) => { e.preventDefault(); void buscar(q); }}><input type="search" aria-label="Assunto" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Ex.: olmesartana, fibrilação atrial…" /><button className="botao" disabled={q.trim().length < 2 || loading}>{loading ? "Buscando…" : "Conectar"}</button></form>
    </header>
    {erro && <Erro mensagem={erro} />}{aviso && <p className="cartao" role="status">{aviso}</p>}{loading && <Carregando texto="Conectando o conhecimento…" />}
    {!loading && primaryDisease && <PainelDoenca disease={primaryDisease} />}
    {!loading && drug && <PainelDrug d={drug} />}
    {!loading && res && res.length > 0 && <section className="cartao">
      <header className="tct-head"><div><p className="eyebrow">{primaryDisease ? "Sequência clínica" : "Mapa do assunto"}</p><h2>{primaryDisease ? "Da definição à decisão" : "Conteúdo conectado"}</h2><p>{res.length}{total > res.length ? ` de ${total}` : ""} resultados por frente de conhecimento</p></div></header>
      <nav className="tct-nav" aria-label="Frentes de conhecimento">{ordenados.map(([s, xs]) => <a className="selo" href={`#secao-${s}`} key={s}>{SECOES[s][0]} · {porFrente[s] ?? xs.length}</a>)}</nav>
      <div className="grade grade--2 tct-grid">
        {ordenados.map(([s, xs]) => <section className="cartao tct-group" id={`secao-${s}`} key={s}><header><p className="eyebrow">{xs.length} resultado{xs.length > 1 ? "s" : ""}</p><h3>{SECOES[s][0]}</h3><p>{SECOES[s][1]}</p></header><div>{xs.map((r) => <Link className="tct-row" to={rota(r)} key={`${r.frente || r.kind}-${r.slug}`}><small>{r.theme || SECOES[s][0]} · {ROTULOS[r.frente || r.kind] ?? r.kind}{r.ano ? ` · ${r.ano}` : ""}</small><strong>{r.title}</strong>{r.snippet && <p><Snippet texto={r.snippet} /></p>}</Link>)}</div></section>)}
        {rel.map((g) => <section className="cartao tct-group" key={`grafo-${g.tipo}`}><header><p className="eyebrow">Conteúdo conectado</p><h3>{g.rotulo || REL_LABELS[g.tipo] || g.tipo}</h3>{g.rota_lista && <Link to={g.rota_lista}>Ver área →</Link>}</header><div>{g.itens.map((x) => <Link className="tct-row" to={x.rota} key={`${g.tipo}-${x.slug}`}><small>{x.context_only || x.relation_scope === "structured_clinical_topic" ? "Mesmo tema clínico" : x.relation_scope === "clinical_match" ? "Relação contextual determinística" : "Relação direta"}</small><strong>{x.titulo}</strong>{x.subtitulo && <p>{x.subtitulo}</p>}</Link>)}</div></section>)}
      </div>
      {nextOffset != null && <div style={{ display: "flex", justifyContent: "center", marginTop: "1rem" }}><button className="botao botao--secundario" type="button" disabled={loadingMore} onClick={() => void carregarMais()}>{loadingMore ? "Conectando mais conteúdo…" : `Carregar mais · ${Math.max(total - res.length, 0)} restantes`}</button></div>}
    </section>}
    {!loading && timeline.length > 0 && <section className="cartao tct-time"><p className="eyebrow">Timeline</p><h2>Estudos e evidências ao longo do tempo</h2><ol>{timeline.map((r) => <li key={`${r.kind}-${r.slug}`}><time>{r.ano}</time><Link to={rota(r)}><small>{SECOES[secao(r)][0]}</small><strong>{r.title}</strong></Link></li>)}</ol></section>}
    {!loading && res?.length === 0 && !drug && <Vazio titulo="Nada encontrado" acao="Tente o princípio ativo ou um sinônimo clínico." />}
  </main>;
}
