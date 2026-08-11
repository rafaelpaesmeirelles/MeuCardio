import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { Carregando, SeloRevisao, Vazio } from "../components/Estado";
import TudoSobreEsteTema from "../components/TudoSobreEsteTema";
import GrafoRelacionados from "../components/GrafoRelacionados";

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

type Serie = { label: string; value: number; detail?: string };

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
  return GRUPOS_AMPLOS.find(([, pistas]) => pistas.some((pista) => normalizada.includes(pista)))?.[0]
    ?? "Outros";
}

function dinheiro(valor: number | null) {
  return valor == null ? "—" : valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function textoEstruturado(valor: unknown): string {
  if (valor == null) return "—";
  if (typeof valor === "string" || typeof valor === "number" || typeof valor === "boolean") return String(valor);
  if (Array.isArray(valor)) return valor.map(textoEstruturado).join(" · ");
  if (typeof valor === "object") {
    return Object.entries(valor as Record<string, unknown>)
      .map(([chave, item]) => `${chave.replaceAll("_", " ")}: ${textoEstruturado(item)}`)
      .join(" · ");
  }
  return String(valor);
}

function Lista({ itens }: { itens: string[] }) {
  if (!itens.length) return <p style={{ color: "var(--texto-secundario)" }}>Sem dado estruturado publicado.</p>;
  return <ul>{itens.map((item, indice) => <li key={`${indice}-${item}`}>{item}</li>)}</ul>;
}

function Grafico({ titulo, series, unidade }: { titulo: string; series: Serie[]; unidade: string }) {
  if (series.length === 0) return null;
  const maximo = Math.max(...series.map((serie) => Math.abs(serie.value)), 1);
  return (
    <section className="cartao">
      <h3>{titulo}</h3>
      <div style={{ display: "grid", gap: "0.55rem" }}>
        {series.map((serie) => (
          <div key={serie.label}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 8, fontSize: "0.84rem" }}>
              <span>{serie.label}</span>
              <strong>{serie.value.toLocaleString("pt-BR")} {unidade}</strong>
            </div>
            <div style={{ height: 12, background: "var(--fundo)", borderRadius: 999, overflow: "hidden", marginTop: 3 }}>
              <span
                aria-hidden="true"
                style={{ display: "block", height: "100%", width: `${Math.max(4, Math.abs(serie.value) / maximo * 100)}%`, background: "var(--acento)" }}
              />
            </div>
            {serie.detail && <small style={{ color: "var(--texto-secundario)" }}>{serie.detail}</small>}
          </div>
        ))}
      </div>
    </section>
  );
}

function ResumoFarmaco({ drug }: { drug: Insight }) {
  return (
    <article id={`medicamento-${drug.slug}`} style={{ scrollMarginTop: "1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "start", flexWrap: "wrap" }}>
        <div>
          <p className="eyebrow">{drug.drug_class}</p>
          <h2>{drug.generic_name}</h2>
        </div>
        <SeloRevisao status={drug.review_status} />
      </div>

      <div className="grade grade--3">
        <div className="cartao"><p className="eyebrow">Meia-vida</p><strong>{drug.half_life_hours == null ? "—" : `${drug.half_life_hours} h`}</strong><p>{drug.half_life_note}</p></div>
        <div className="cartao"><p className="eyebrow">Tempo de ação</p><strong>{drug.duration_of_action_hours == null ? "—" : `${drug.duration_of_action_hours} h`}</strong><p>{drug.duration_of_action_note}</p></div>
        <div className="cartao"><p className="eyebrow">PMC médio de referência</p><strong>{dinheiro(drug.cmed.average_pmc)}</strong><p style={{ fontSize: "0.78rem" }}>{drug.cmed.average_label}</p></div>
      </div>

      {(drug.sbp_reduction_mmhg != null || drug.dbp_reduction_mmhg != null) && (
        <section className="cartao" style={{ marginTop: "0.8rem" }}>
          <p className="eyebrow">Potência anti-hipertensiva publicada</p>
          <p>
            PAS: <strong>{drug.sbp_reduction_mmhg ?? "—"} mmHg</strong> · PAD:{" "}
            <strong>{drug.dbp_reduction_mmhg ?? "—"} mmHg</strong>
          </p>
          {drug.bp_evidence_source && <small>{drug.bp_evidence_source}</small>}
        </section>
      )}

      <div className="grade grade--2" style={{ marginTop: "0.8rem" }}>
        <section className="cartao"><p className="eyebrow">Mecanismo</p><p>{drug.mechanism || "Sem dado publicado."}</p></section>
        <section className="cartao"><p className="eyebrow">Dose e administração</p><p>{textoEstruturado(drug.dosing)}</p></section>
        <section className="cartao"><p className="eyebrow">Indicações</p><Lista itens={drug.indications} /></section>
        <section className="cartao"><p className="eyebrow">Monitorização</p><Lista itens={drug.monitoring} /></section>
        <section className="cartao"><p className="eyebrow">Ajuste renal</p><p>{drug.renal_adjustment || "Sem dado publicado."}</p></section>
        <section className="cartao"><p className="eyebrow">Ajuste hepático</p><p>{drug.hepatic_adjustment || "Sem dado publicado."}</p></section>
        <section className="cartao"><p className="eyebrow">Contraindicações</p><Lista itens={drug.contraindications} /></section>
        <section className="cartao"><p className="eyebrow">Efeitos adversos</p><Lista itens={drug.adverse_effects} /></section>
      </div>

      <section className="cartao" style={{ marginTop: "0.8rem" }}>
        <p className="eyebrow">Marcas e apresentações comerciais — CMED</p>
        {drug.cmed.presentations.length === 0 ? (
          <p>Não há apresentação vinculada à lista CMED atual.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.84rem" }}>
              <thead><tr><th>Produto</th><th>Laboratório</th><th>Apresentação</th><th>PMC</th></tr></thead>
              <tbody>
                {drug.cmed.presentations.map((item) => (
                  <tr key={`${item.ggrem}-${item.presentation}`}>
                    <td>{item.brand_name}</td><td>{item.manufacturer}</td><td>{item.presentation}</td><td>{dinheiro(item.pmc)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <p className="eyebrow" style={{ marginTop: "0.5rem" }}>
          Lista {drug.cmed.published_at ?? "não importada"} · UF {drug.cmed.uf ?? "não definida"}. PMC é teto regulatório, não preço final.
        </p>
      </section>

      {drug.references.length > 0 && (
        <section className="cartao" style={{ marginTop: "0.8rem" }}><p className="eyebrow">Fontes</p><Lista itens={drug.references} /></section>
      )}

      {/* Medicamentos não têm campo de tema próprio no banco — a convenção do
       * projeto (ver CLAUDE.md e app/services/related_content.py) é que a
       * frente de Farmacologia inteira entra no cruzamento sob o tema
       * "Farmacologia", junto dos documentos/evidências/estudos desse tema. */}
      <TudoSobreEsteTema tema="Farmacologia" excluirTipo="medicamento" excluirSlug={drug.slug} />

      <GrafoRelacionados entityType="medicamento" slug={drug.slug} />
    </article>
  );
}

export default function Medicamentos() {
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
    api.get<Item[]>("/drugs").then(setLista).catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar."));
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
      requestAnimationFrame(() => document.getElementById(`medicamento-${slug}`)?.scrollIntoView({ behavior: "smooth" }));
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível abrir o medicamento.");
    } finally { setCarregando(false); }
  }

  // Chegada por link direto do painel "Tudo sobre este tema" de outra página
  // (`/medicamentos?slug=...`) — abre o verbete sozinho, sem exigir que o
  // médico procure o remédio de novo na lista.
  useEffect(() => {
    const slugPedido = searchParams.get("slug");
    if (slugPedido) visualizar(slugPedido);
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
      setComparacao(await api.post<Comparacao>("/drug-insights/compare", { slugs: selecionados }));
      requestAnimationFrame(() => document.getElementById("comparacao-medicamentos")?.scrollIntoView({ behavior: "smooth" }));
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível comparar.");
    } finally { setCarregando(false); }
  }

  if (!lista && !erro) return <Carregando />;

  const pas = comparacao?.drugs.flatMap((drug) => drug.sbp_reduction_mmhg == null ? [] : [{ label: `${drug.generic_name} — PAS`, value: drug.sbp_reduction_mmhg, detail: drug.bp_evidence_source ?? undefined }]) ?? [];
  const pad = comparacao?.drugs.flatMap((drug) => drug.dbp_reduction_mmhg == null ? [] : [{ label: `${drug.generic_name} — PAD`, value: drug.dbp_reduction_mmhg }]) ?? [];
  const meiasVidas = comparacao?.drugs.flatMap((drug) => drug.half_life_hours == null ? [] : [{ label: drug.generic_name, value: drug.half_life_hours, detail: drug.half_life_note ?? undefined }]) ?? [];
  const duracoes = comparacao?.drugs.flatMap((drug) => drug.duration_of_action_hours == null ? [] : [{ label: drug.generic_name, value: drug.duration_of_action_hours, detail: drug.duration_of_action_note ?? undefined }]) ?? [];

  return (
    <>
      <p className="eyebrow">Farmacologia</p>
      <h1>Medicamentos</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "70ch" }}>
        Clique em um medicamento e escolha entre visualizar o verbete completo ou adicioná-lo a uma comparação de até quatro opções.
      </p>

      <div className="grade grade--2" style={{ marginTop: "0.8rem" }}>
        <div><label>Buscar</label><input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Nome genérico ou classe" /></div>
        <div><label>Grupo terapêutico</label><select value={grupo} onChange={(e) => setGrupo(e.target.value)}><option value="">Todos</option>{grupos.map((item) => <option key={item}>{item}</option>)}</select></div>
      </div>

      {selecionados.length > 0 && (
        <div className="cartao" style={{ margin: "0.9rem 0", position: "sticky", top: 8, zIndex: 4 }}>
          <strong>Comparação: {selecionados.length}/4</strong>
          <p style={{ margin: "0.3rem 0" }}>{selecionados.map((slug) => lista?.find((item) => item.slug === slug)?.generic_name ?? slug).join(" · ")}</p>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button className="botao" onClick={comparar} disabled={selecionados.length < 2 || carregando}>Comparar selecionados</button>
            <button className="botao botao--secundario" onClick={() => { setSelecionados([]); setComparacao(null); }}>Limpar</button>
          </div>
        </div>
      )}

      {erro && <p role="alert" style={{ color: "var(--alerta)" }}>{erro}</p>}
      {filtrados.length === 0 ? <Vazio titulo="Nenhum medicamento encontrado" /> : (
        <div className="grade grade--3" style={{ marginTop: "1rem" }}>
          {filtrados.map((item) => {
            const expandido = aberto === item.slug;
            const marcado = selecionados.includes(item.slug);
            return (
              <article key={item.slug} className="cartao" style={{ borderLeft: marcado ? "4px solid var(--acento)" : undefined }}>
                <button type="button" onClick={() => setAberto(expandido ? null : item.slug)} style={{ display: "block", width: "100%", textAlign: "left", border: 0, background: "transparent", padding: 0, cursor: "pointer", color: "inherit" }} aria-expanded={expandido}>
                  <p className="eyebrow">{grupoAmplo(item.drug_class)}</p>
                  <h3>{item.generic_name}</h3>
                  <p style={{ color: "var(--texto-secundario)", fontSize: "0.82rem" }}>{item.drug_class}</p>
                  <SeloRevisao status={item.review_status} />
                </button>
                {expandido && (
                  <div style={{ display: "grid", gap: 8, marginTop: "0.8rem", borderTop: "1px solid var(--linha)", paddingTop: "0.7rem" }}>
                    <button className="botao" onClick={() => visualizar(item.slug)}>Visualizar</button>
                    <button className="botao botao--secundario" onClick={() => alternarComparacao(item.slug)}>
                      {marcado ? "Remover da comparação" : "Comparar"}
                    </button>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}

      {carregando && <Carregando texto="Carregando dados farmacológicos…" />}
      {detalhe && <div style={{ marginTop: "2rem" }}><ResumoFarmaco drug={detalhe} /></div>}

      {comparacao && (
        <section id="comparacao-medicamentos" style={{ marginTop: "2rem", scrollMarginTop: "1rem" }}>
          <p className="eyebrow">Comparação</p>
          <h2>{comparacao.drugs.map((drug) => drug.generic_name).join(" × ")}</h2>
          <div className="grade grade--3">
            <Grafico titulo="Redução média de PAS" series={pas} unidade="mmHg" />
            <Grafico titulo="Redução média de PAD" series={pad} unidade="mmHg" />
            <Grafico titulo="Meia-vida" series={meiasVidas} unidade="h" />
            <Grafico titulo="Tempo de ação" series={duracoes} unidade="h" />
          </div>

          <div style={{ overflowX: "auto", marginTop: "1rem" }}>
            <table style={{ width: "100%", minWidth: 760, borderCollapse: "collapse" }}>
              <thead><tr><th>Medicamento</th><th>Classe</th><th>Marcas</th><th>PMC médio</th><th>Ajuste renal</th><th>Monitorização</th></tr></thead>
              <tbody>{comparacao.drugs.map((drug) => <tr key={drug.slug}><td><strong>{drug.generic_name}</strong></td><td>{drug.drug_class}</td><td>{drug.cmed.presentations.slice(0, 6).map((item) => item.brand_name).filter((nome, indice, listaNomes) => listaNomes.indexOf(nome) === indice).join(", ") || drug.brand_names.join(", ") || "—"}</td><td>{dinheiro(drug.cmed.average_pmc)}</td><td>{drug.renal_adjustment || "—"}</td><td>{drug.monitoring.join("; ") || "—"}</td></tr>)}</tbody>
            </table>
          </div>

          <div className="cartao" style={{ marginTop: "1rem" }}><p className="eyebrow">Limitações</p><Lista itens={comparacao.warnings} /></div>
        </section>
      )}
    </>
  );
}
