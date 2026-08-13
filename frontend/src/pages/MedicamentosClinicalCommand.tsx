import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import Icone from "../components/Icone";
import { api, ApiError } from "../lib/api";
import { Carregando, SeloRevisao } from "../components/Estado";
import DicaContextual from "../components/DicaContextual";
import GrafoRelacionados from "../components/GrafoRelacionados";
import TudoSobreEsteTema from "../components/TudoSobreEsteTema";
import ClinicalText from "../components/ClinicalText";
import {
  ClinicalContextLink,
  ClinicalEmpty,
  ClinicalMetric,
  ClinicalPageHeader,
  ClinicalSection,
} from "../components/ClinicalCommandPrimitives";

type Item = {
  slug: string;
  generic_name: string;
  drug_class: string;
  review_status: string;
};

type ApresentacaoCmed = {
  brand_name: string;
  manufacturer: string;
  presentation: string;
  ggrem: string;
  hospital_only: boolean;
  pmc: number | null;
  pmc_label: string | null;
};

type Insight = {
  slug: string;
  generic_name: string;
  drug_class: string;
  brand_names: string[];
  mechanism: string | null;
  presentations: string[];
  commercial_presentations: Record<string, unknown>[];
  dosing: Record<string, unknown>;
  renal_adjustment: string | null;
  hepatic_adjustment: string | null;
  contraindications: string[];
  interactions: string[];
  monitoring: string[];
  indications: string[];
  adverse_effects: string[];
  pregnancy: string | null;
  lactation: string | null;
  notes: Record<string, unknown>;
  half_life_hours: number | null;
  half_life_note: string | null;
  duration_of_action_hours: number | null;
  duration_of_action_note: string | null;
  duration_of_action_source: string | null;
  sbp_reduction_mmhg: number | null;
  dbp_reduction_mmhg: number | null;
  bp_evidence_source: string | null;
  references: string[];
  review_status: string;
  cmed: {
    published_at: string | null;
    uf: string | null;
    presentations: ApresentacaoCmed[];
    average_pmc: number | null;
    average_label: string;
  };
};

type Comparacao = { uf: string | null; drugs: Insight[]; warnings: string[] };

const GRUPOS_AMPLOS: [string, string[]][] = [
  ["Antagonista mineralocorticoide", ["mineralocorticoide", "poupador de potássio"]],
  ["IECA", ["enzima conversora de angiotensina"]],
  ["BRA", ["receptor de angiotensina ii", "bra/ara"]],
  ["ARNI", ["neprilisina"]],
  ["Betabloqueador", ["betabloqueador"]],
  ["Bloqueador de canal de cálcio", ["canal de cálcio"]],
  ["Diurético", ["diurético", "diuretico"]],
  ["Antiarrítmico", ["antiarrítmico", "antiarritmico"]],
  ["Anticoagulante", ["anticoagulante", "inibidor direto do fator", "antagonista da vitamina k"]],
  ["Antiagregante", ["antiagregante", "antiplaquetário", "antiplaquetario"]],
  ["Hipolipemiante", ["estatina", "pcsk9", "hipolipemiante", "colesterol"]],
  ["Vasodilatador/antianginoso", ["nitrato", "vasodilatador", "antianginoso"]],
  ["iSGLT2", ["sglt2", "cotransportador sódio-glicose"]],
];

function grupoAmplo(classe: string) {
  const normalizada = classe.toLocaleLowerCase("pt-BR");
  return GRUPOS_AMPLOS.find(([, pistas]) => pistas.some((pista) => normalizada.includes(pista)))?.[0] ?? "Outros";
}

function dinheiro(valor: number | null) {
  return valor == null ? "—" : valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function rotuloCampo(chave: string) {
  return chave.replaceAll("_", " ").replace(/\b\w/g, (letra) => letra.toLocaleUpperCase("pt-BR"));
}

function textoEstruturado(valor: unknown): string {
  if (valor == null) return "";
  if (["string", "number", "boolean"].includes(typeof valor)) return String(valor);
  if (Array.isArray(valor)) return valor.map(textoEstruturado).filter(Boolean).join("\n\n");
  if (typeof valor === "object") {
    return Object.entries(valor as Record<string, unknown>)
      .filter(([, item]) => item != null && textoEstruturado(item).trim())
      .map(([chave, item]) => `**${rotuloCampo(chave)}:** ${textoEstruturado(item)}`)
      .join("\n\n");
  }
  return String(valor);
}

function ListaClinica({ itens, vazio = "Sem dado estruturado publicado." }: { itens: string[]; vazio?: string }) {
  if (!itens.length) return <p>{vazio}</p>;
  return <ul className="cc-clinical-list">{itens.map((item, indice) => <li key={`${indice}-${item.slice(0, 32)}`}><ClinicalText compact>{item}</ClinicalText></li>)}</ul>;
}

function MiniBar({ value, max }: { value: number; max: number }) {
  return <div className="cc-mini-bar" aria-hidden="true"><span style={{ width: `${Math.max(4, Math.abs(value) / Math.max(max, 1) * 100)}%` }} /></div>;
}

function ComparacaoMedicamentos({ comparacao }: { comparacao: Comparacao }) {
  const maxPas = Math.max(...comparacao.drugs.map((d) => Math.abs(d.sbp_reduction_mmhg ?? 0)), 1);
  const maxMeiaVida = Math.max(...comparacao.drugs.map((d) => Math.abs(d.half_life_hours ?? 0)), 1);
  return (
    <ClinicalSection eyebrow="Comparação clínica" title={comparacao.drugs.map((drug) => drug.generic_name).join(" × ")} description="Compare propriedades publicadas lado a lado. Use o contexto clínico do paciente antes de qualquer decisão terapêutica.">
      <div className="cc-compare-grid">
        {comparacao.drugs.map((drug) => <article className="cc-compare-card" key={drug.slug}>
          <div className="cc-compare-card__head"><div><p className="eyebrow">{grupoAmplo(drug.drug_class)}</p><h3>{drug.generic_name}</h3></div><SeloRevisao status={drug.review_status} /></div>
          <dl>
            <div><dt>Classe</dt><dd>{drug.drug_class}</dd></div>
            <div><dt>Meia-vida</dt><dd>{drug.half_life_hours == null ? "—" : `${drug.half_life_hours} h`} {drug.half_life_hours != null && <MiniBar value={drug.half_life_hours} max={maxMeiaVida} />}</dd></div>
            <div><dt>PAS publicada</dt><dd>{drug.sbp_reduction_mmhg == null ? "—" : `${drug.sbp_reduction_mmhg} mmHg`} {drug.sbp_reduction_mmhg != null && <MiniBar value={drug.sbp_reduction_mmhg} max={maxPas} />}</dd></div>
            <div><dt>PMC médio</dt><dd>{dinheiro(drug.cmed.average_pmc)}</dd></div>
            <div><dt>Ajuste renal</dt><dd><ClinicalText compact>{drug.renal_adjustment}</ClinicalText></dd></div>
          </dl>
        </article>)}
      </div>
      {comparacao.warnings.length > 0 && <div className="cc-compare-warnings"><p className="eyebrow">Limitações</p><ListaClinica itens={comparacao.warnings} /></div>}
    </ClinicalSection>
  );
}

function DetalheMedicamento({ drug, onClose }: { drug: Insight; onClose: () => void }) {
  const marcas = Array.from(new Set([
    ...drug.brand_names,
    ...drug.cmed.presentations.map((p) => p.brand_name),
  ].filter(Boolean)));
  const indicacaoPrincipal = drug.indications[0] || "Consulte as indicações revisadas deste medicamento.";
  const referenciaPrincipal = drug.references[0] || drug.bp_evidence_source || "Fontes revisadas disponíveis no verbete completo.";

  function irPara(id: string) {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  return (
    <div id={`medicamento-${drug.slug}`} className="mc-command">
      <header className="mc-command__header">
        <button type="button" className="mc-command__back" onClick={onClose} aria-label="Voltar ao catálogo"><Icone nome="chevron" /></button>
        <div className="mc-command__identity">
          <h1>{drug.generic_name}</h1>
          <p>{marcas.slice(0, 3).join(" · ") || drug.drug_class}</p>
        </div>
        <div className="mc-command__actions">
          <Link to="/receituario" className="mc-command__prescribe"><Icone nome="prescricao" /> Prescrever</Link>
          <Link to="/favoritos" className="mc-command__favorite" aria-label="Abrir favoritos"><Icone nome="favorito" /></Link>
        </div>
      </header>

      <nav className="mc-command__tabs" aria-label="Seções do medicamento">
        <button className="is-active" type="button" onClick={() => irPara("mc-overview")}>Visão geral</button>
        <button type="button" onClick={() => irPara("mc-dose")}>Doses</button>
        <button type="button" onClick={() => irPara("mc-indications")}>Indicações</button>
        <button type="button" onClick={() => irPara("mc-evidence")}>Evidências</button>
        <button type="button" onClick={() => irPara("mc-interactions")}>Interações</button>
        <button type="button" onClick={() => irPara("mc-more")}>Mais</button>
      </nav>

      <section id="mc-overview" className="mc-command__grid">
        <article className="mc-command__primary">
          <div className="mc-command__primary-block">
            <small>Indicação principal</small>
            <strong>{indicacaoPrincipal}</strong>
            <ClinicalText compact>{drug.mechanism}</ClinicalText>
          </div>
          <div id="mc-dose" className="mc-command__primary-block mc-command__primary-block--dose">
            <small>Dose usual</small>
            <ClinicalText>{textoEstruturado(drug.dosing)}</ClinicalText>
          </div>
          <div id="mc-evidence" className="mc-command__primary-block mc-command__primary-block--evidence">
            <small>Evidência principal</small>
            <strong>{referenciaPrincipal}</strong>
            <p>Fontes e dados completos permanecem disponíveis abaixo.</p>
          </div>
        </article>

        <aside className="mc-command__intelligence" aria-label="Inteligência CorVIA">
          <header><span>✦</span><strong>Inteligência CorVIA</strong></header>
          <section id="mc-interactions">
            <small>Interações relevantes</small>
            {drug.interactions.length ? drug.interactions.slice(0, 3).map((item, indice) => <div className="mc-command__intel-item" key={`${indice}-${item.slice(0, 20)}`}><i /><ClinicalText compact>{item}</ClinicalText></div>) : <p>Sem interação estruturada publicada.</p>}
          </section>
          <section id="mc-indications">
            <small>Condições relacionadas</small>
            {drug.indications.slice(0, 4).map((item, indice) => <Link to="/doencas" className="mc-command__condition" key={`${indice}-${item.slice(0, 20)}`}><i /><span>{item}</span></Link>)}
          </section>
        </aside>
      </section>

      <section id="mc-more" className="mc-command__facts">
        <article><small>Classe</small><strong>{drug.drug_class}</strong></article>
        <article><small>Meia-vida</small><strong>{drug.half_life_hours == null ? "—" : `${drug.half_life_hours} h`}</strong><span>{drug.half_life_note || "Parâmetro farmacocinético"}</span></article>
        <article><small>Tempo de ação</small><strong>{drug.duration_of_action_hours == null ? "—" : `${drug.duration_of_action_hours} h`}</strong><span>{drug.duration_of_action_note || "Quando estruturado"}</span></article>
        <article><small>PMC médio</small><strong>{dinheiro(drug.cmed.average_pmc)}</strong><span>Teto regulatório de referência</span></article>
      </section>

      <div className="cc-detail-grid mc-command__details">
        <article className="cc-detail-card"><p className="eyebrow">Indicações</p><ListaClinica itens={drug.indications} /></article>
        <article className="cc-detail-card"><p className="eyebrow">Monitorização</p><ListaClinica itens={drug.monitoring} /></article>
        <article className="cc-detail-card"><p className="eyebrow">Ajuste renal</p><ClinicalText>{drug.renal_adjustment}</ClinicalText></article>
        <article className="cc-detail-card"><p className="eyebrow">Ajuste hepático</p><ClinicalText>{drug.hepatic_adjustment}</ClinicalText></article>
        <article className="cc-detail-card"><p className="eyebrow">Contraindicações</p><ListaClinica itens={drug.contraindications} /></article>
        <article className="cc-detail-card"><p className="eyebrow">Efeitos adversos</p><ListaClinica itens={drug.adverse_effects} /></article>
        <article className="cc-detail-card"><p className="eyebrow">Gestação e lactação</p><ClinicalText>{[drug.pregnancy && `**Gestação:** ${drug.pregnancy}`, drug.lactation && `**Lactação:** ${drug.lactation}`].filter(Boolean).join("\n\n")}</ClinicalText></article>
        <article className="cc-detail-card"><p className="eyebrow">Interações completas</p><ListaClinica itens={drug.interactions} /></article>
      </div>

      {(drug.sbp_reduction_mmhg != null || drug.dbp_reduction_mmhg != null) && <ClinicalSection eyebrow="Efeito hemodinâmico" title="Potência anti-hipertensiva publicada">
        <div className="cc-metrics"><ClinicalMetric label="PAS" value={drug.sbp_reduction_mmhg == null ? "—" : `${drug.sbp_reduction_mmhg} mmHg`} /><ClinicalMetric label="PAD" value={drug.dbp_reduction_mmhg == null ? "—" : `${drug.dbp_reduction_mmhg} mmHg`} /></div>
        {drug.bp_evidence_source && <div className="cc-source-note"><ClinicalText compact>{drug.bp_evidence_source}</ClinicalText></div>}
      </ClinicalSection>}

      <ClinicalSection eyebrow="Apresentações" title="CMED" description="PMC é teto regulatório e não representa necessariamente o preço final ao paciente.">
        {drug.cmed.presentations.length === 0 ? <ClinicalEmpty title="Sem apresentação CMED vinculada" /> : <div className="cc-table-wrap"><table><thead><tr><th>Produto</th><th>Laboratório</th><th>Apresentação</th><th>PMC</th></tr></thead><tbody>{drug.cmed.presentations.map((item) => <tr key={`${item.ggrem}-${item.presentation}`}><td><strong>{item.brand_name}</strong></td><td>{item.manufacturer}</td><td>{item.presentation}</td><td>{dinheiro(item.pmc)}</td></tr>)}</tbody></table></div>}
      </ClinicalSection>

      {drug.references.length > 0 && <ClinicalSection eyebrow="Proveniência" title="Fontes do verbete"><ListaClinica itens={drug.references} /></ClinicalSection>}

      <ClinicalSection eyebrow="Conhecimento conectado" title="Da farmacologia à decisão" description="Continue pelo contexto que você precisa resolver agora.">
        <div className="cc-context-grid">
          <ClinicalContextLink to="/interacoes" icon="medicamento" title="Interações" detail="Segurança medicamentosa" />
          <ClinicalContextLink to="/evidencias" icon="evidencia" title="Evidências" detail="Recomendações relacionadas" />
          <ClinicalContextLink to="/estudos" icon="evidencia" title="Estudos" detail="Literatura original" />
          <ClinicalContextLink to="/receituario" icon="prescricao" title="Prescrição" detail="Levar para uma ação clínica" />
          <ClinicalContextLink to="/doencas" icon="doencas" title="Condições" detail="Contexto de uso" />
          <ClinicalContextLink to="/assistente" icon="assistente" title="Assistente Clínica" detail="Discutir o contexto" />
        </div>
      </ClinicalSection>

      <TudoSobreEsteTema tema="Farmacologia" excluirTipo="medicamento" excluirSlug={drug.slug} />
      <GrafoRelacionados entityType="medicamento" slug={drug.slug} />
    </div>
  );
}

export default function MedicamentosClinicalCommand() {
  const [searchParams] = useSearchParams();
  const [lista, setLista] = useState<Item[] | null>(null);
  const [busca, setBusca] = useState("");
  const [grupo, setGrupo] = useState("");
  const [aberto, setAberto] = useState<string | null>(null);
  const [selecionados, setSelecionados] = useState<string[]>([]);
  const [detalhe, setDetalhe] = useState<Insight | null>(null);
  const [comparacao, setComparacao] = useState<Comparacao | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.get<Item[]>("/drugs").then(setLista).catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar os medicamentos."));
  }, []);

  const grupos = useMemo(() => {
    const valores = new Set((lista ?? []).map((item) => grupoAmplo(item.drug_class)));
    return [...valores].sort((a, b) => a.localeCompare(b, "pt-BR"));
  }, [lista]);

  const filtrados = useMemo(() => {
    const termo = busca.trim().toLocaleLowerCase("pt-BR");
    return (lista ?? []).filter((item) => {
      const pertence = !grupo || grupoAmplo(item.drug_class) === grupo;
      const casa = !termo || `${item.generic_name} ${item.drug_class}`.toLocaleLowerCase("pt-BR").includes(termo);
      return pertence && casa;
    });
  }, [lista, busca, grupo]);

  async function visualizar(slug: string) {
    setCarregando(true); setErro(""); setComparacao(null);
    try {
      const resposta = await api.get<Insight>(`/drug-insights/${slug}`);
      setDetalhe(resposta);
      requestAnimationFrame(() => document.getElementById(`medicamento-${slug}`)?.scrollIntoView({ behavior: "smooth", block: "start" }));
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível abrir o medicamento.");
    } finally { setCarregando(false); }
  }

  useEffect(() => {
    const slug = searchParams.get("slug");
    if (slug) void visualizar(slug);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  function alternarComparacao(slug: string) {
    setSelecionados((atuais) => {
      if (atuais.includes(slug)) return atuais.filter((item) => item !== slug);
      if (atuais.length >= 4) return atuais;
      return [...atuais, slug];
    });
    setComparacao(null);
  }

  async function comparar() {
    if (selecionados.length < 2) return;
    setCarregando(true); setErro(""); setDetalhe(null);
    try {
      const resposta = await api.post<Comparacao>("/drug-insights/compare", { slugs: selecionados });
      setComparacao(resposta);
      requestAnimationFrame(() => document.getElementById("comparacao-medicamentos")?.scrollIntoView({ behavior: "smooth", block: "start" }));
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível comparar os medicamentos.");
    } finally { setCarregando(false); }
  }

  if (!lista && !erro) return <Carregando texto="Abrindo farmacologia…" />;

  if (detalhe) {
    return <div className="cc-page cc-drugs-page cc-drugs-page--detail">{erro && <div className="cc-inline-alert" role="alert">{erro}</div>}<DetalheMedicamento drug={detalhe} onClose={() => setDetalhe(null)} />{carregando && <Carregando texto="Conectando dados farmacológicos…" />}</div>;
  }

  return (
    <div className="cc-page cc-drugs-page">
      <ClinicalPageHeader
        eyebrow="Farmacologia clínica"
        title="Medicamentos"
        description="Pesquise, compare e atravesse do fármaco para segurança, evidência, condição clínica e ação — sem perder o contexto."
        icon="medicamento"
        actions={[{ to: "/interacoes", label: "Interações", icon: "medicamento" }, { to: "/receituario", label: "Prescrever", icon: "prescricao", tone: "primary" }]}
        meta={lista ? <><span className="selo">{lista.length} revisados</span><span className="selo">CMED vinculada</span></> : undefined}
      />

      <DicaContextual id="medicamentos" titulo="O verbete é um ponto de partida">Abra um fármaco e continue para evidências, condições, exames, estudos ou prescrição a partir do mesmo contexto.</DicaContextual>

      <ClinicalSection eyebrow="Encontrar" title="Qual medicamento você precisa agora?">
        <div className="cc-filterbar">
          <div className="cc-filterbar__field"><label htmlFor="cc-drug-search">Nome genérico ou classe</label><input id="cc-drug-search" value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Ex.: sacubitril, apixabana, betabloqueador…" autoComplete="off" /></div>
          <div className="cc-filterbar__field"><label htmlFor="cc-drug-group">Grupo terapêutico</label><select id="cc-drug-group" value={grupo} onChange={(e) => setGrupo(e.target.value)}><option value="">Todos os grupos</option>{grupos.map((item) => <option key={item}>{item}</option>)}</select></div>
          <div className="cc-filterbar__result">{filtrados.length} resultado{filtrados.length === 1 ? "" : "s"}</div>
        </div>
      </ClinicalSection>

      {selecionados.length > 0 && <div className="cc-sticky-selection"><div className="cc-sticky-selection__copy"><strong>Comparação · {selecionados.length}/4 selecionados</strong><small>{selecionados.map((slug) => lista?.find((item) => item.slug === slug)?.generic_name ?? slug).join(" · ")}</small></div><div className="cc-sticky-selection__actions"><button className="botao" type="button" onClick={() => void comparar()} disabled={selecionados.length < 2 || carregando}>Comparar</button><button className="botao botao--secundario" type="button" onClick={() => { setSelecionados([]); setComparacao(null); }}>Limpar</button></div></div>}

      {erro && <div className="cc-inline-alert" role="alert">{erro}</div>}

      <ClinicalSection eyebrow="Catálogo" title="Farmacologia revisada" description="Toque em um medicamento para abrir as ações sem perder a visão do catálogo.">
        {filtrados.length === 0 ? <ClinicalEmpty title="Nenhum medicamento encontrado" description="Tente outro nome, classe ou remova o filtro terapêutico." /> : <div className="cc-card-grid">{filtrados.map((item) => {
          const expandido = aberto === item.slug; const marcado = selecionados.includes(item.slug);
          return <article key={item.slug} className={`cc-entity-card${marcado ? " is-selected" : ""}`}><button className="cc-entity-card__main" type="button" onClick={() => setAberto(expandido ? null : item.slug)} aria-expanded={expandido}><p className="eyebrow">{grupoAmplo(item.drug_class)}</p><h3>{item.generic_name}</h3><p>{item.drug_class}</p><SeloRevisao status={item.review_status} /></button>{expandido && <div className="cc-entity-card__actions"><button className="botao" type="button" onClick={() => void visualizar(item.slug)}>Abrir verbete</button><button className="botao botao--secundario" type="button" onClick={() => alternarComparacao(item.slug)}>{marcado ? "Remover" : "Comparar"}</button></div>}</article>;
        })}</div>}
      </ClinicalSection>

      {carregando && <Carregando texto="Conectando dados farmacológicos…" />}
      {comparacao && <div id="comparacao-medicamentos"><ComparacaoMedicamentos comparacao={comparacao} /></div>}

      <ClinicalSection eyebrow="Atalhos" title="Continuar o fluxo">
        <div className="cc-context-grid"><ClinicalContextLink to="/interacoes" icon="medicamento" title="Interações medicamentosas" detail="Cruzar combinações" /><ClinicalContextLink to="/receituario" icon="prescricao" title="Prescrição" detail="Preparar uma receita" /><ClinicalContextLink to="/evidencias" icon="evidencia" title="Evidências" detail="Ver recomendações" /></div>
        <p className="cc-footnote">Para preço de mercado, diferencie sempre o valor comercial do teto regulatório CMED.</p>
        <Link to="/busca" className="cc-text-link">Explorar todo o conhecimento conectado →</Link>
      </ClinicalSection>
    </div>
  );
}
