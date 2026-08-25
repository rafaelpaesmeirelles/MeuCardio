import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro, Vazio } from "../components/Estado";

type Resultado = { slug: string; title: string; kind: string; frente?: string | null; theme: string; snippet: string; ano?: number | null };
type MedicamentoBusca = { slug: string; generic_name: string; drug_class: string; brand_names?: string[] };
type MedicamentoInsight = {
  slug: string; generic_name: string; drug_class: string; brand_names: string[];
  mechanism: string | null; presentations: string[]; dosing: Record<string, unknown>;
  renal_adjustment: string | null; hepatic_adjustment: string | null;
  contraindications: string[]; interactions: string[]; monitoring: string[];
  indications: string[]; adverse_effects: string[]; pregnancy: string | null; lactation: string | null;
  half_life_hours: number | null; half_life_note: string | null;
  duration_of_action_hours: number | null; duration_of_action_note: string | null;
  sbp_reduction_mmhg: number | null; dbp_reduction_mmhg: number | null;
  bp_evidence_source: string | null; review_status: string;
};
type ConfiguracaoFrente = { id: string; titulo: string; descricao: string; ordem: number; rota: string };
type ItemRelacionado = { slug: string; titulo: string; subtitulo: string | null; rota: string };
type GrupoRelacionado = { tipo: string; rotulo: string; rota_lista: string; itens: ItemRelacionado[] };
type RespostaRelacionados = { tema?: string; grupos: GrupoRelacionado[]; total: number };

const FRENTES: Record<string, ConfiguracaoFrente> = {
  visao_geral: { id: "visao_geral", titulo: "Visão geral e características", descricao: "Fundamentos, características e conteúdo de referência", ordem: 10, rota: "/biblioteca" },
  condutas: { id: "condutas", titulo: "Condutas e protocolos", descricao: "Manejo, tratamento e aplicação prática", ordem: 11, rota: "/biblioteca" },
  diretrizes: { id: "diretrizes", titulo: "Diretrizes e consensos", descricao: "Guidelines, consensos e posicionamentos", ordem: 12, rota: "/biblioteca" },
  fluxogramas: { id: "fluxogramas", titulo: "Fluxogramas", descricao: "Algoritmos e caminhos de decisão", ordem: 13, rota: "/biblioteca" },
  estudo: { id: "estudo", titulo: "Estudos", descricao: "Literatura original e trabalhos científicos", ordem: 20, rota: "/estudos" },
  evidencia: { id: "evidencia", titulo: "Evidências", descricao: "Recomendações, classes e níveis de evidência", ordem: 30, rota: "/evidencias" },
  exame: { id: "exame", titulo: "Exames", descricao: "Diagnóstico, indicação e interpretação", ordem: 40, rota: "/exames" },
  galeria: { id: "galeria", titulo: "Galeria clínica", descricao: "Imagens e achados relacionados", ordem: 50, rota: "/galeria" },
};
const RÓTULO_KIND: Record<string, string> = {
  documento: "Documento", estudo: "Estudo", evidencia: "Evidência", exame: "Exame",
  galeria: "Imagem", fluxograma: "Fluxograma", protocolo: "Protocolo",
};

function normalizar(valor: string) {
  return valor.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR").replace(/[^a-z0-9]+/g, " ").trim();
}

function idDaFrente(resultado: Resultado) {
  const valor = normalizar(resultado.frente || resultado.kind).replaceAll(" ", "_");
  if (["estudo", "estudos", "study"].includes(valor)) return "estudo";
  if (["evidencia", "evidencias", "evidence"].includes(valor)) return "evidencia";
  if (["exame", "exames", "lab_test", "lab_tests"].includes(valor)) return "exame";
  if (["galeria", "imagem", "imagens", "gallery"].includes(valor)) return "galeria";
  const texto = normalizar(`${resultado.kind} ${resultado.title}`);
  if (/\b(fluxograma|algoritmo|flowchart)\b/.test(texto)) return "fluxogramas";
  if (/\b(diretriz|diretrizes|guideline|guidelines|consenso|posicionamento)\b/.test(texto)) return "diretrizes";
  if (/\b(protocolo|conduta|manejo|tratamento|terapia|abordagem)\b/.test(texto)) return "condutas";
  return "visao_geral";
}

function rotaDoResultado(resultado: Resultado) {
  const frente = FRENTES[idDaFrente(resultado)] ?? FRENTES.visao_geral;
  return `${frente.rota}/${resultado.slug}`;
}

function SnippetDestacado({ snippet }: { snippet: string }) {
  const partes = snippet.split(/(<mark>|<\/mark>)/gi);
  let destacado = false;
  const nos: ReactNode[] = [];
  partes.forEach((parte, indice) => {
    if (/^<mark>$/i.test(parte)) { destacado = true; return; }
    if (/^<\/mark>$/i.test(parte)) { destacado = false; return; }
    if (parte) nos.push(destacado ? <mark key={indice}>{parte}</mark> : <span key={indice}>{parte}</span>);
  });
  return <>{nos}</>;
}

function textoEstruturado(valor: unknown): string {
  if (valor == null) return "";
  if (["string", "number", "boolean"].includes(typeof valor)) return String(valor);
  if (Array.isArray(valor)) return valor.map(textoEstruturado).filter(Boolean).join(" · ");
  if (typeof valor === "object") {
    return Object.entries(valor as Record<string, unknown>)
      .filter(([, item]) => textoEstruturado(item).trim())
      .map(([chave, item]) => `${chave.replaceAll("_", " ")}: ${textoEstruturado(item)}`).join("\n");
  }
  return String(valor);
}

function Lista({ itens, vazio = "Sem dado estruturado publicado." }: { itens: Array<string | null | undefined>; vazio?: string }) {
  const validos = itens.filter((item): item is string => Boolean(item?.trim()));
  if (!validos.length) return <p className="tct-muted">{vazio}</p>;
  return <ul>{validos.map((item, indice) => <li key={`${indice}-${item.slice(0, 32)}`}>{item}</li>)}</ul>;
}

function PainelMedicamento({ medicamento }: { medicamento: MedicamentoInsight }) {
  const dose = textoEstruturado(medicamento.dosing);
  const potencia = [
    medicamento.sbp_reduction_mmhg != null ? `PAS: ${medicamento.sbp_reduction_mmhg} mmHg` : null,
    medicamento.dbp_reduction_mmhg != null ? `PAD: ${medicamento.dbp_reduction_mmhg} mmHg` : null,
  ].filter((item): item is string => Boolean(item));

  return (
    <section className="tct-drug" aria-labelledby="tct-drug-title">
      <header className="tct-section-heading">
        <div><p className="eyebrow">Medicamento identificado</p><h2 id="tct-drug-title">{medicamento.generic_name}</h2><p>{medicamento.drug_class}</p></div>
        <Link to={`/medicamentos?slug=${encodeURIComponent(medicamento.slug)}`} className="tct-open-all">Abrir verbete completo <span aria-hidden="true">→</span></Link>
      </header>
      <nav className="tct-topic-nav" aria-label="Tópicos do medicamento">
        <a href="#caracteristicas">Características</a><a href="#posologia-potencia">Posologia e potência</a><a href="#indicacoes">Indicações</a><a href="#seguranca">Segurança</a>
      </nav>
      <div className="tct-drug-grid">
        <article id="caracteristicas" className="tct-topic-card">
          <p className="eyebrow">Características</p><h3>Perfil farmacológico</h3>
          <dl>
            <div><dt>Classe</dt><dd>{medicamento.drug_class}</dd></div>
            {medicamento.mechanism && <div><dt>Mecanismo</dt><dd>{medicamento.mechanism}</dd></div>}
            {medicamento.half_life_hours != null && <div><dt>Meia-vida</dt><dd>{medicamento.half_life_hours} h{medicamento.half_life_note ? ` · ${medicamento.half_life_note}` : ""}</dd></div>}
            {medicamento.duration_of_action_hours != null && <div><dt>Duração de ação</dt><dd>{medicamento.duration_of_action_hours} h{medicamento.duration_of_action_note ? ` · ${medicamento.duration_of_action_note}` : ""}</dd></div>}
            {medicamento.presentations.length > 0 && <div><dt>Apresentações</dt><dd>{medicamento.presentations.join(" · ")}</dd></div>}
          </dl>
        </article>
        <article id="posologia-potencia" className="tct-topic-card">
          <p className="eyebrow">Posologia e potência</p><h3>Dose e efeito publicados</h3>
          {dose ? <p className="tct-structured">{dose}</p> : <p className="tct-muted">Sem posologia estruturada publicada.</p>}
          {potencia.length > 0 && <div className="tct-potency">{potencia.map((item) => <strong key={item}>{item}</strong>)}</div>}
          {medicamento.bp_evidence_source && <p className="tct-source">Fonte da estimativa: {medicamento.bp_evidence_source}</p>}
        </article>
        <article id="indicacoes" className="tct-topic-card">
          <p className="eyebrow">Indicações</p><h3>Onde este medicamento se encaixa</h3><Lista itens={medicamento.indications} vazio="Sem indicação estruturada publicada." />
        </article>
        <article id="seguranca" className="tct-topic-card">
          <p className="eyebrow">Segurança e monitorização</p><h3>O que verificar</h3>
          <Lista itens={medicamento.monitoring} vazio="Sem monitorização estruturada publicada." />
          {(medicamento.renal_adjustment || medicamento.hepatic_adjustment) && <dl>
            {medicamento.renal_adjustment && <div><dt>Ajuste renal</dt><dd>{medicamento.renal_adjustment}</dd></div>}
            {medicamento.hepatic_adjustment && <div><dt>Ajuste hepático</dt><dd>{medicamento.hepatic_adjustment}</dd></div>}
          </dl>}
          {medicamento.contraindications.length > 0 && <details><summary>Contraindicações ({medicamento.contraindications.length})</summary><Lista itens={medicamento.contraindications} /></details>}
          {medicamento.interactions.length > 0 && <details><summary>Interações ({medicamento.interactions.length})</summary><Lista itens={medicamento.interactions} /></details>}
          {medicamento.adverse_effects.length > 0 && <details><summary>Efeitos adversos ({medicamento.adverse_effects.length})</summary><Lista itens={medicamento.adverse_effects} /></details>}
        </article>
      </div>
    </section>
  );
}

export default function Busca() {
  const [params, setParams] = useSearchParams();
  const [q, setQ] = useState(params.get("q") ?? "");
  const [res, setRes] = useState<Resultado[] | null>(null);
  const [medicamento, setMedicamento] = useState<MedicamentoInsight | null>(null);
  const [relacionados, setRelacionados] = useState<RespostaRelacionados | null>(null);
  const [termoBuscado, setTermoBuscado] = useState(params.get("q")?.trim() ?? "");
  const [buscando, setBuscando] = useState(false);
  const [erro, setErro] = useState("");
  const [aviso, setAviso] = useState("");
  const [tipo, setTipo] = useState("");
  const buscaAtual = useRef(0);

  async function buscar(termoBruto: string) {
    const termo = termoBruto.trim();
    if (termo.length < 2) return;
    const idBusca = ++buscaAtual.current;
    setBuscando(true); setErro(""); setAviso(""); setMedicamento(null); setRelacionados(null); setTermoBuscado(termo);
    setParams({ q: termo }, { replace: true });

    const [resultadoBusca, resultadoMedicamentos] = await Promise.allSettled([
      api.get<{ results: Resultado[] }>(`/search?q=${encodeURIComponent(termo)}`),
      api.get<MedicamentoBusca[]>(`/drugs?q=${encodeURIComponent(termo)}`),
    ]);
    if (idBusca !== buscaAtual.current) return;
    if (resultadoBusca.status === "rejected") {
      const causa = resultadoBusca.reason;
      setRes(null); setErro(causa instanceof ApiError ? causa.message : "Não foi possível consultar o conteúdo agora."); setBuscando(false); return;
    }

    setRes(resultadoBusca.value.results); setTipo("");
    let encontrouMedicamentoForte = false;
    if (resultadoMedicamentos.status === "fulfilled") {
      const termoNormalizado = normalizar(termo);
      const fortes = resultadoMedicamentos.value.filter((item) => {
        const nome = normalizar(item.generic_name); const slug = normalizar(item.slug);
        return nome === termoNormalizado || slug === termoNormalizado || nome.startsWith(`${termoNormalizado} `);
      });
      if (fortes.length === 1) {
        encontrouMedicamentoForte = true;
        try {
          const insight = await api.get<MedicamentoInsight>(`/drug-insights/${fortes[0].slug}`);
          if (idBusca === buscaAtual.current) setMedicamento(insight);
        } catch (causa) {
          if (idBusca === buscaAtual.current) setAviso(causa instanceof ApiError ? causa.message : "O resumo farmacológico não pôde ser carregado.");
        }
      }
    } else setAviso("A busca geral foi concluída, mas o catálogo de medicamentos está temporariamente indisponível.");

    if (resultadoMedicamentos.status === "fulfilled" && !encontrouMedicamentoForte && resultadoBusca.value.results.length > 0) {
      const temas = resultadoBusca.value.results.map((item) => item.theme).filter((tema) => tema?.trim());
      const temaExato = temas.find((tema) => normalizar(tema) === normalizar(termo));
      // Só atravessa o ecossistema inteiro quando o próprio nome do tema é o
      // assunto pesquisado. Um termo específico pode aparecer em vários
      // documentos de um tema amplo (ex.: Noonan em Cardiologia pediátrica),
      // mas isso não autoriza misturar todo o tema amplo ao resultado.
      const temaCanonico = temaExato ?? null;
      if (temaCanonico) {
        try {
          const conexoes = await api.get<RespostaRelacionados>(`/relacionados?tema=${encodeURIComponent(temaCanonico)}`);
          if (idBusca === buscaAtual.current) setRelacionados(conexoes);
        } catch {
          // As conexões complementam a busca principal e não devem ocultá-la em caso de falha.
        }
      }
    }
    if (idBusca === buscaAtual.current) setBuscando(false);
  }

  useEffect(() => {
    const inicial = params.get("q");
    if (inicial && inicial.trim().length >= 2) void buscar(inicial);
    // A consulta inicial deve acontecer apenas na montagem; buscar() atualiza a URL.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const tipos = useMemo(() => Array.from(new Set((res ?? []).map((item) => item.kind))).sort(), [res]);
  const resultados = useMemo(() => tipo ? (res ?? []).filter((item) => item.kind === tipo) : (res ?? []), [res, tipo]);
  const grupos = useMemo(() => {
    const mapa = new Map<string, Resultado[]>();
    resultados.forEach((item) => { const frente = idDaFrente(item); mapa.set(frente, [...(mapa.get(frente) ?? []), item]); });
    return [...mapa.entries()].map(([id, itens]) => ({ config: FRENTES[id] ?? FRENTES.visao_geral, itens })).sort((a, b) => a.config.ordem - b.config.ordem);
  }, [resultados]);
  const gruposRelacionados = useMemo(() => {
    const jaCobertos = new Set(["documento", "fluxograma", "evidencia", "estudo", "exame", "galeria"]);
    return (relacionados?.grupos ?? []).filter((grupo) => grupo.itens.length > 0 && !jaCobertos.has(grupo.tipo));
  }, [relacionados]);
  const timeline = useMemo(() => resultados
    .filter((item) => ["estudo", "evidencia"].includes(idDaFrente(item)) && typeof item.ano === "number")
    .sort((a, b) => (b.ano ?? 0) - (a.ano ?? 0)), [resultados]);

  return (
    <main className="tct-page">
      <header className="tct-hero">
        <p className="eyebrow">Tudo com Tudo</p><h1>{termoBuscado ? `Tudo sobre ${termoBuscado}` : "Um assunto, todas as conexões"}</h1>
        <p>Pesquise uma condição, medicamento ou achado. A Corvia organiza cada resultado por frente clínica, sem misturar conteúdos diferentes em uma lista única.</p>
        <form className="tct-search" onSubmit={(evento) => { evento.preventDefault(); void buscar(q); }} role="search">
          <label htmlFor="tct-search-input">Qual assunto você quer conectar?</label>
          <div><input id="tct-search-input" type="search" value={q} onChange={(evento) => setQ(evento.target.value)} placeholder="Ex.: olmesartana, fibrilação atrial, miocardite…" autoComplete="off" /><button className="botao" type="submit" disabled={q.trim().length < 2 || buscando}>{buscando ? "Buscando…" : "Conectar"}</button></div>
        </form>
      </header>

      {erro && <Erro mensagem={erro} />}
      {aviso && <div className="tct-warning" role="status">{aviso}</div>}
      {buscando && <Carregando texto="Conectando áreas, estudos e evidências…" />}
      {!buscando && medicamento && <PainelMedicamento medicamento={medicamento} />}

      {!buscando && res !== null && (res.length > 0 || medicamento) && <section className="tct-results" aria-labelledby="tct-results-title">
        <header className="tct-section-heading">
          <div><p className="eyebrow">Mapa do assunto</p><h2 id="tct-results-title">Conteúdo conectado</h2><p>{res.length} resultado{res.length === 1 ? "" : "s"} distribuído{res.length === 1 ? "" : "s"} por área.</p></div>
          {tipos.length > 1 && <label className="tct-type-filter">Filtrar tipo<select value={tipo} onChange={(evento) => setTipo(evento.target.value)}><option value="">Todos ({res.length})</option>{tipos.map((item) => <option key={item} value={item}>{RÓTULO_KIND[item] ?? item} ({res.filter((resultado) => resultado.kind === item).length})</option>)}</select></label>}
        </header>
        {grupos.length > 1 && <nav className="tct-topic-nav" aria-label="Áreas encontradas">{grupos.map(({ config, itens }) => <a key={config.id} href={`#frente-${config.id}`}>{config.titulo} <span>{itens.length}</span></a>)}</nav>}
        <div className="tct-groups">{grupos.map(({ config, itens }) => <section className="tct-group" id={`frente-${config.id}`} key={config.id} aria-labelledby={`frente-${config.id}-titulo`}>
          <header><div><p className="eyebrow">{itens.length} resultado{itens.length === 1 ? "" : "s"}</p><h3 id={`frente-${config.id}-titulo`}>{config.titulo}</h3><p>{config.descricao}</p></div><Link to={`${config.rota}?q=${encodeURIComponent(q.trim())}`}>Ver toda a área <span aria-hidden="true">→</span></Link></header>
          <div className="tct-result-list">{itens.map((item) => <Link key={`${item.kind}-${item.slug}`} to={rotaDoResultado(item)} className="tct-result-card">
            <span className="tct-result-card__meta">{item.theme} · {RÓTULO_KIND[item.kind] ?? item.kind}{item.ano ? ` · ${item.ano}` : ""}</span><strong>{item.title}</strong>{item.snippet && <p><SnippetDestacado snippet={item.snippet} /></p>}<span className="tct-result-card__open" aria-hidden="true">Abrir →</span>
          </Link>)}</div>
        </section>)}{gruposRelacionados.map((grupo) => <section className="tct-group tct-group--ecosystem" key={`relacionado-${grupo.tipo}`}>
          <header><div><p className="eyebrow">Ecossistema conectado</p><h3>{grupo.rotulo}</h3><p>{grupo.itens.length} item{grupo.itens.length === 1 ? "" : "s"} do mesmo tema canônico.</p></div><Link to={grupo.rota_lista}>Ver toda a área <span aria-hidden="true">→</span></Link></header>
          <div className="tct-result-list">{grupo.itens.map((item) => <Link key={`${grupo.tipo}-${item.slug}`} to={item.rota} className="tct-result-card"><span className="tct-result-card__meta">{grupo.rotulo}</span><strong>{item.titulo}</strong>{item.subtitulo && <p>{item.subtitulo}</p>}<span className="tct-result-card__open" aria-hidden="true">Abrir →</span></Link>)}</div>
        </section>)}</div>
      </section>}

      {!buscando && timeline.length > 0 && <section className="tct-timeline" aria-labelledby="tct-timeline-title">
        <header><p className="eyebrow">Timeline</p><h2 id="tct-timeline-title">Estudos e evidências ao longo do tempo</h2><p>A evolução científica do assunto em ordem cronológica.</p></header>
        <ol>{timeline.map((item) => <li key={`timeline-${item.kind}-${item.slug}`}><time>{item.ano}</time><Link to={rotaDoResultado(item)}><small>{FRENTES[idDaFrente(item)].titulo}</small><strong>{item.title}</strong></Link></li>)}</ol>
      </section>}

      {!buscando && res !== null && res.length === 0 && !medicamento && <Vazio titulo="Nada encontrado" acao="Tente um termo mais curto, o princípio ativo ou um sinônimo clínico." />}
    </main>
  );
}
