import { useEffect, useRef, useState, type ReactNode } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro, Vazio } from "../components/Estado";

type Res = { slug: string; title: string; kind: string; frente?: string; theme: string; snippet: string; ano?: number };
type Drug = { slug: string; generic_name: string; drug_class: string; brand_names?: string[] };
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
  match_score?: number; match_threshold?: number;
};
type Rel = { tipo: string; rotulo: string; rota_lista: string; itens: RelItem[] };

const SECOES = {
  geral: ["Visão geral e características", "Fundamentos e conteúdo de referência", "/biblioteca", 10],
  conduta: ["Condutas e protocolos", "Manejo, tratamento e aplicação prática", "/biblioteca", 11],
  diretriz: ["Diretrizes e consensos", "Guidelines, consensos e posicionamentos", "/biblioteca", 12],
  fluxo: ["Fluxogramas", "Algoritmos e caminhos de decisão", "/biblioteca", 13],
  estudo: ["Estudos", "Literatura original e trabalhos científicos", "/estudos", 20],
  evidencia: ["Evidências", "Recomendações e níveis de evidência", "/evidencias", 30],
  exame: ["Exames", "Diagnóstico, indicação e interpretação", "/exames", 40],
  galeria: ["Galeria clínica", "Imagens e achados relacionados", "/galeria", 50],
} as const;
type Secao = keyof typeof SECOES;
const ROTULOS: Record<string, string> = { documento: "Documento", estudo: "Estudo", evidencia: "Evidência", exame: "Exame", galeria: "Imagem", fluxograma: "Fluxograma", protocolo: "Protocolo" };
const norm = (s: string) => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
function secao(r: Res): Secao {
  const f = norm(r.frente || r.kind);
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
const rota = (r: Res) => `${SECOES[secao(r)][2]}/${r.slug}`;

function origemContextual(item: RelItem): { rotulo: string; detalhe: string; cor: string } {
  if (item.provenance_type === "editorial" || item.confidence === "explicit") {
    const revisada = item.review_status === "revisado";
    const origem = item.provenance_type === "imported" ? " de fonte importada" : item.provenance_type === "editorial" ? " editorial" : "";
    return {
      rotulo: revisada ? "Curada e revisada" : "Curada · revisão pendente",
      detalhe: `Relação explícita${origem} ${revisada ? "e revisada" : "ainda pendente de revisão"}.`,
      cor: revisada ? "#63dfc1" : "#8fdac8",
    };
  }
  if (item.provenance_type && ["structured_metadata", "imported", "derived"].includes(item.provenance_type)) {
    return { rotulo: "Estruturada", detalhe: "Correspondência sustentada por metadado ou regra estruturada.", cor: "#76b7ff" };
  }
  return {
    rotulo: "Inferida por contexto",
    detalhe: "Correspondência automática por assunto e taxonomia; não equivale a vínculo clínico curado.",
    cor: "#d7a5ff",
  };
}

function scoreContextual(item: RelItem): string {
  const partes: string[] = [];
  if (typeof item.relevance_score === "number") {
    partes.push(`pertinência ${Math.round(Math.min(1, Math.max(0, item.relevance_score)) * 100)}%`);
  }
  if (typeof item.match_score === "number" && typeof item.match_threshold === "number") {
    partes.push(`sinal ${item.match_score} · mínimo ${item.match_threshold}`);
  }
  return partes.join(" · ");
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

export default function Busca() {
  const [params, setParams] = useSearchParams();
  const inicial = params.get("q") ?? "";
  const [q, setQ] = useState(inicial), [assunto, setAssunto] = useState(inicial.trim());
  const [res, setRes] = useState<Res[] | null>(null), [drug, setDrug] = useState<Insight | null>(null), [rel, setRel] = useState<Rel[]>([]);
  const [loading, setLoading] = useState(false), [erro, setErro] = useState(""), [aviso, setAviso] = useState("");
  const seq = useRef(0);

  async function buscar(valor: string) {
    const termo = valor.trim(); if (termo.length < 2) return;
    const id = ++seq.current;
    setLoading(true); setErro(""); setAviso(""); setDrug(null); setRel([]); setAssunto(termo); setParams({ q: termo }, { replace: true });
    const [s, ds] = await Promise.allSettled([api.get<{ results: Res[] }>(`/search?q=${encodeURIComponent(termo)}`), api.get<Drug[]>(`/drugs?q=${encodeURIComponent(termo)}`)]);
    if (id !== seq.current) return;
    if (s.status === "rejected") { setRes(null); setErro(s.reason instanceof ApiError ? s.reason.message : "Não foi possível consultar o conteúdo."); setLoading(false); return; }
    const itens = s.value.results; setRes(itens);
    let medicamentoForte = false;
    if (ds.status === "rejected") setAviso("Conteúdo carregado; catálogo de medicamentos indisponível.");
    else {
      const n = norm(termo), fortes = ds.value.filter((d) => norm(d.generic_name) === n || norm(d.slug) === n || norm(d.generic_name).startsWith(`${n} `) || d.brand_names?.some((marca) => norm(marca) === n));
      if (fortes.length === 1) {
        medicamentoForte = true;
        try { const d = await api.get<Insight>(`/drug-insights/${fortes[0].slug}`); if (id === seq.current) setDrug(d); }
        catch (e) { if (id === seq.current) setAviso(e instanceof ApiError ? e.message : "Resumo farmacológico indisponível."); }
      }
    }
    if (!medicamentoForte) {
      const n = norm(termo), tema = itens.map((x) => x.theme).find((x) => norm(x) === n);
      const chavesTextuais = new Set(itens.flatMap((x) => [
        `${x.kind === "fluxograma" ? "fluxograma" : (x.frente || x.kind)}:${x.slug}`,
        `rota:${rota(x)}`,
      ]));
      if (tema) try {
        const query = new URLSearchParams({ tema, assunto: termo });
        const x = await api.get<{ grupos: Rel[] }>(`/relacionados?${query.toString()}`);
        if (id === seq.current) setRel(x.grupos
          .map((g) => ({
            ...g,
            itens: g.itens.filter((item) => (
              !chavesTextuais.has(`${g.tipo}:${item.slug}`) && !chavesTextuais.has(`rota:${item.rota}`)
            )),
          }))
          .filter((g) => g.itens.length > 0));
      } catch { /* complemento opcional */ }
    }
    if (id === seq.current) setLoading(false);
  }
  useEffect(() => { if (inicial.trim().length > 1) void buscar(inicial); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, []);

  const grupos = new Map<Secao, Res[]>();
  (res ?? []).forEach((r) => { const s = secao(r); grupos.set(s, [...(grupos.get(s) ?? []), r]); });
  const ordenados = [...grupos].sort((a, b) => Number(SECOES[a[0]][3]) - Number(SECOES[b[0]][3]));
  const timeline = (res ?? []).filter((r) => ["estudo", "evidencia"].includes(secao(r)) && r.ano).sort((a, b) => (b.ano ?? 0) - (a.ano ?? 0));

  return <main className="tct-page">
    <header className="cartao tct-hero"><p className="eyebrow">Tudo com Tudo · busca textual</p><h1>{assunto ? `Resultados para ${assunto}` : "Pesquisar em todo o conhecimento"}</h1><p>A pesquisa full-text localiza termos em títulos e textos publicados. Um resultado textual não é, por si só, uma conexão clínica.</p>
      <form className="tct-search" role="search" onSubmit={(e) => { e.preventDefault(); void buscar(q); }}><input type="search" aria-label="Assunto" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Ex.: olmesartana, fibrilação atrial…" /><button className="botao" disabled={q.trim().length < 2 || loading}>{loading ? "Buscando…" : "Pesquisar"}</button></form>
    </header>
    {erro && <Erro mensagem={erro} />}{aviso && <p className="cartao" role="status">{aviso}</p>}{loading && <Carregando texto="Pesquisando o conhecimento…" />}
    {!loading && drug && <PainelDrug d={drug} />}
    {!loading && res && res.length > 0 && <section className="cartao" data-search-mode="full-text">
      <header className="tct-head"><div><p className="eyebrow">Busca textual</p><h2>Correspondências encontradas</h2><p>{res.length} resultados recuperados por termos, organizados por frente de conhecimento</p></div></header>
      <p role="note" style={{ margin: "0.55rem 0", padding: "0.65rem 0.75rem", color: "var(--texto-secundario)", background: "rgba(var(--space-rgb), .045)", border: "1px solid rgba(var(--space-rgb), .13)", borderRadius: "9px", fontSize: "0.78rem" }}>
        Use estes resultados para localizar conteúdo. Relações clínicas curadas ou estruturadas são identificadas explicitamente quando há proveniência disponível; similaridade textual isolada não recebe esse selo.
      </p>
      <nav className="tct-nav" aria-label="Frentes de conhecimento">{ordenados.map(([s, xs]) => <a className="selo" href={`#secao-${s}`} key={s}>{SECOES[s][0]} · {xs.length}</a>)}</nav>
      <div className="grade grade--2 tct-grid">
        {ordenados.map(([s, xs]) => <section className="cartao tct-group" id={`secao-${s}`} key={s}><header><p className="eyebrow">{xs.length} correspondência{xs.length > 1 ? "s" : ""} textual{xs.length > 1 ? "is" : ""}</p><h3>{SECOES[s][0]}</h3><p>{SECOES[s][1]}</p></header><div>{xs.map((r) => <Link className="tct-row" to={rota(r)} key={`${r.kind}-${r.slug}`}><small>Busca textual · {r.theme} · {ROTULOS[r.kind] ?? r.kind}{r.ano ? ` · ${r.ano}` : ""}</small><strong>{r.title}</strong>{r.snippet && <p><Snippet texto={r.snippet} /></p>}</Link>)}</div></section>)}
        {rel.map((g) => <section className="cartao tct-group" data-relationship-surface="contextual-inference" key={g.tipo}><header><p className="eyebrow">Associação contextual</p><h3>{g.rotulo}</h3><p>Seleção automática por assunto e taxonomia; não equivale, isoladamente, a relação clínica curada.</p><Link to={g.rota_lista}>Ver área →</Link></header><div>{g.itens.map((x) => { const origem = origemContextual(x); const score = scoreContextual(x); return <Link className="tct-row" to={x.rota} key={x.slug} title={origem.detalhe}><small style={{ color: origem.cor }}>{origem.rotulo}{score ? ` · ${score}` : ""}</small><strong>{x.titulo}</strong>{x.subtitulo && <p>{x.subtitulo}</p>}</Link>; })}</div></section>)}
      </div>
    </section>}
    {!loading && timeline.length > 0 && <section className="cartao tct-time"><p className="eyebrow">Timeline da busca</p><h2>Estudos e evidências localizados ao longo do tempo</h2><ol>{timeline.map((r) => <li key={`${r.kind}-${r.slug}`}><time>{r.ano}</time><Link to={rota(r)}><small>{SECOES[secao(r)][0]}</small><strong>{r.title}</strong></Link></li>)}</ol></section>}
    {!loading && res?.length === 0 && !drug && <Vazio titulo="Nada encontrado" acao="Tente o princípio ativo ou um sinônimo clínico." />}
  </main>;
}
