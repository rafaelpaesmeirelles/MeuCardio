import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Carregando, Erro } from "../components/Estado";
import { api } from "../lib/api";

type Disease = {
  slug: string;
  name: string;
  aliases: string[];
  area: string;
  category: string;
  subtype?: string | null;
  cyanosis_class?: string | null;
  prevalence_rank: number;
  completeness: string;
  summary: string;
  tags: string[];
  has_assistant: boolean;
};

type Response = {
  items: Disease[];
  page: number;
  page_size: number;
  total: number;
  has_more: boolean;
};

type DiseaseFacet = { id: string; count: number };
type DiseaseFacetsResponse = { areas: DiseaseFacet[]; categories: DiseaseFacet[] };

type Tab = "catalogo" | "assistentes" | "areas" | "congenitas" | "fetal" | "pediatrica" | "oncologia" | "gestacao" | "outros";

const AREA_LABELS: Record<string, string> = {
  geral: "Cardiologia do adulto",
  cardiopediatria: "Cardiologia pediátrica e congênita",
  cardiogeriatria: "Cardiogeriatria",
  cardiooncologia: "Cardio-oncologia",
  gravidez: "Cardiologia na gestação e puerpério",
};

const CATEGORY_LABELS: Record<string, string> = {
  arritmia: "Arritmias",
  antitromboticos: "Antitrombóticos",
  aortopatia: "Aortopatias",
  cardiomiopatia: "Cardiomiopatias",
  cardiopatia_adquirida: "Cardiopatias adquiridas",
  cardiopatia_congenita: "Cardiopatias congênitas",
  cardiologia_fetal: "Cardiologia fetal",
  circulacao_pulmonar: "Circulação e hipertensão pulmonar",
  doenca_coronariana: "Doença coronariana",
  doenca_inflamatoria: "Doenças inflamatórias",
  doenca_miocardica: "Doenças do miocárdio",
  doenca_prevalente: "Doenças prevalentes",
  hipertensao: "Hipertensão",
  hipertensao_na_gestacao: "Hipertensão na gestação",
  insuficiencia_cardiaca: "Insuficiência cardíaca",
  pericardio: "Doenças do pericárdio",
  prevencao: "Prevenção cardiovascular",
  tromboembolismo: "Tromboembolismo",
  valvopatia: "Valvopatias",
  valvopatia_e_anticoagulacao: "Valvopatias e anticoagulação",
};

const TAB_LABELS: Record<Tab, string> = {
  catalogo: "Catálogo",
  assistentes: "Assistentes por doença",
  areas: "Assistentes por áreas da Cardiologia",
  congenitas: "Cardiopatias congênitas",
  fetal: "Cardiologia fetal",
  pediatrica: "Cardiologia pediátrica",
  oncologia: "Cardio-Oncologia",
  gestacao: "Gestação e puerpério",
  outros: "Outros",
};

function labelArea(area: string) {
  return AREA_LABELS[area] ?? area.replaceAll("_", " ").replace(/^./, (letter) => letter.toUpperCase());
}

function labelCategory(category: string) {
  return CATEGORY_LABELS[category] ?? category.replaceAll("_", " ").replace(/^./, (letter) => letter.toUpperCase());
}

function labelCyanosis(value?: string | null) {
  if (value === "cianotica") return "Cianótica";
  if (value === "acianotica") return "Acianótica";
  return null;
}

export default function GuiaDoencas() {
  const [params, setParams] = useSearchParams();
  const tab = (params.get("tab") as Tab) || "catalogo";
  const [q, setQ] = useState(params.get("q") || "");
  const [area, setArea] = useState(params.get("area") || "");
  const [category, setCategory] = useState(params.get("category") || "");
  const [cyanosis, setCyanosis] = useState(params.get("cyanosis") || "");
  const [items, setItems] = useState<Disease[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [diseaseFacets, setDiseaseFacets] = useState<DiseaseFacetsResponse>({ areas: [], categories: [] });

  useEffect(() => {
    api.get<DiseaseFacetsResponse>("/specialty-guides/disease-facets")
      .then(setDiseaseFacets)
      .catch(() => setDiseaseFacets({ areas: [], categories: [] }));
  }, []);

  const filters = useMemo(() => {
    const result: Record<string, string> = { page_size: "60", page: String(page) };
    if (q.trim()) result.q = q.trim();
    if (area) result.area = area;
    if (category) result.category = category;
    if (tab === "assistentes") result.assistant_only = "true";
    if (tab === "congenitas") result.category = "cardiopatia_congenita";
    if (tab === "fetal") result.category = "cardiologia_fetal";
    if (tab === "pediatrica") result.area = "cardiopediatria";
    if (tab === "oncologia") result.area = "cardiooncologia";
    if (tab === "gestacao") result.area = "gravidez";
    if (tab === "outros") result.area = "cardiogeriatria";
    if (cyanosis && tab === "congenitas") result.cyanosis_class = cyanosis;
    return result;
  }, [q, area, category, tab, cyanosis, page]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    const search = new URLSearchParams(filters).toString();
    api.get<Response>(`/specialty-guides/diseases?${search}`)
      .then((response) => {
        if (!active) return;
        setItems((previous) => page === 1 ? response.items : [...previous, ...response.items]);
        setHasMore(response.has_more);
        setTotal(response.total);
      })
      .catch((cause) => { if (active) setError(cause.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [filters, page]);

  function changeTab(next: Tab) {
    setPage(1);
    setItems([]);
    setCyanosis("");
    setCategory("");
    if (!["catalogo", "assistentes"].includes(next)) setArea("");
    const nextParams = new URLSearchParams();
    nextParams.set("tab", next);
    if (q.trim()) nextParams.set("q", q.trim());
    if (["catalogo", "assistentes"].includes(next) && area) nextParams.set("area", area);
    setParams(nextParams);
  }

  function abrirArea(areaSelecionada: string) {
    setPage(1);
    setItems([]);
    setArea(areaSelecionada);
    setCategory("");
    setParams({ tab: "catalogo", area: areaSelecionada });
  }

  function abrirCategoria(categorySelecionada: string) {
    setPage(1);
    setItems([]);
    setArea("");
    setCategory(categorySelecionada);
    setParams({ tab: "catalogo", category: categorySelecionada });
  }

  function updateSearch(value: string) {
    setQ(value);
    setPage(1);
    setItems([]);
  }

  return (
    <>
      <p className="eyebrow">Conhecimento clínico estruturado</p>
      <h1>Guia de Doenças</h1>
      <p style={{ maxWidth: "75ch", color: "var(--texto-secundario)" }}>
        Consulte doenças por área, prevalência, anatomia e sintomas. Os assistentes
        organizam dados, red flags, exames e fluxos, mas não substituem avaliação clínica.
      </p>

      <div className="painel__temas" style={{ marginTop: "1rem" }} role="tablist">
        {(Object.keys(TAB_LABELS) as Tab[]).map((value) => (
          <button
            key={value}
            type="button"
            role="tab"
            className="painel__tema"
            onClick={() => changeTab(value)}
            aria-selected={tab === value}
            style={tab === value ? { borderColor: "var(--acento)", fontWeight: 700 } : undefined}
          >
            {TAB_LABELS[value]}
          </button>
        ))}
      </div>

      {tab === "areas" && (
        <section className="guia-areas" aria-labelledby="assistentes-areas-titulo">
          <div className="guia-areas__topo">
            <div>
              <p className="eyebrow">Navegação especializada</p>
              <h2 id="assistentes-areas-titulo">Áreas disponíveis no Guia de Doenças</h2>
            </div>
            <p>São exibidas somente áreas que possuem verbetes publicados; a contagem vem diretamente do catálogo.</p>
          </div>
          <div className="guia-areas__grade">
            {diseaseFacets.areas.map((item) => (
              <article className="cartao guia-area" key={item.id}>
                <span className="guia-area__marca" aria-hidden="true">{labelArea(item.id).slice(0, 2).toUpperCase()}</span>
                <div><h3>{labelArea(item.id)}</h3><p>{item.count.toLocaleString("pt-BR")} verbetes publicados.</p></div>
                <button className="botao botao--secundario" type="button" onClick={() => abrirArea(item.id)}>Abrir área</button>
              </article>
            ))}
          </div>
          <div className="guia-areas__topo" style={{ marginTop: "1rem" }}>
            <div><p className="eyebrow">Subáreas e grupos clínicos</p><h2>Todos os grupos com conteúdo</h2></div>
          </div>
          <div className="painel__temas">
            {diseaseFacets.categories.map((item) => (
              <button className="painel__tema" type="button" key={item.id} onClick={() => abrirCategoria(item.id)}>
                {labelCategory(item.id)} ({item.count.toLocaleString("pt-BR")})
              </button>
            ))}
          </div>
        </section>
      )}

      {tab === "outros" && (
        <section className="cartao guia-outros">
          <div>
            <p className="eyebrow">Acervo cardiológico completo</p>
            <h2>Demais áreas e patologias</h2>
            <p>Além dos guias especializados em Cardio-Geriatria abaixo, a biblioteca reúne arritmias, doença coronariana, insuficiência cardíaca, valvopatias, hipertensão, prevenção, aorta, doença vascular, pericárdio, endocardite e outras coleções.</p>
          </div>
          <Link className="botao" to="/biblioteca#documentos">Ver todas as áreas e conteúdos</Link>
        </section>
      )}

      {tab !== "areas" && <section className="cartao" style={{ marginTop: "1rem" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 15rem), 1fr))", gap: "0.7rem" }}>
          {!["pediatrica", "oncologia", "gestacao", "outros"].includes(tab) && <label>
            <strong>Pesquisar</strong>
            <input
              value={q}
              onChange={(event) => updateSearch(event.target.value)}
              placeholder="Nome, sigla, sinônimo, sintoma ou tema…"
              style={{ marginTop: "0.35rem" }}
            />
          </label>}
          <label>
            <strong>População / contexto</strong>
            <select
              value={area}
              onChange={(event) => { setArea(event.target.value); setPage(1); setItems([]); }}
              style={{ marginTop: "0.35rem" }}
            >
              <option value="">Todos</option>
              {diseaseFacets.areas.map((item) => <option key={item.id} value={item.id}>{labelArea(item.id)} ({item.count})</option>)}
            </select>
          </label>
          <label>
            <strong>Área clínica</strong>
            <select
              value={category}
              onChange={(event) => { setCategory(event.target.value); setPage(1); setItems([]); }}
              style={{ marginTop: "0.35rem" }}
            >
              <option value="">Todas</option>
              {diseaseFacets.categories.map((item) => <option key={item.id} value={item.id}>{labelCategory(item.id)} ({item.count})</option>)}
            </select>
          </label>
        </div>

        {tab === "congenitas" && (
          <div className="painel__temas" style={{ marginTop: "0.8rem" }}>
            {["", "acianotica", "cianotica"].map((value) => (
              <button
                key={value || "todas"}
                type="button"
                className="painel__tema"
                onClick={() => { setCyanosis(value); setPage(1); setItems([]); }}
                style={cyanosis === value ? { borderColor: "var(--acento)" } : undefined}
              >
                {value ? labelCyanosis(value) : "Todas"}
              </button>
            ))}
          </div>
        )}
      </section>}

      {tab !== "areas" && <p style={{ marginTop: "1rem", color: "var(--texto-secundario)" }}>
        {total} {total === 1 ? "tema encontrado" : "temas encontrados"}
      </p>}

      {tab !== "areas" && error && <Erro mensagem={error} />}
      {tab !== "areas" && (loading && page === 1 ? <Carregando /> : (
        <div style={{ display: "grid", gap: "0.8rem" }}>
          {items.map((item) => (
            <article key={item.slug} className="cartao painel__funcao">
              <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", alignItems: "flex-start" }}>
                <div>
                  <p className="eyebrow">{labelArea(item.area)} · {item.category.replaceAll("_", " ")}</p>
                  <h2 style={{ margin: "0.15rem 0 0.35rem" }}>{item.name}</h2>
                </div>
                <div className="painel__temas" style={{ justifyContent: "flex-end" }}>
                  {labelCyanosis(item.cyanosis_class) && <span className="painel__tema">{labelCyanosis(item.cyanosis_class)}</span>}
                  {item.has_assistant && <span className="painel__tema">Assistente disponível</span>}
                </div>
              </div>
              <p>{item.summary}</p>
              {item.aliases.length > 0 && (
                <p style={{ fontSize: "0.82rem", color: "var(--texto-secundario)" }}>
                  Também encontrado como: {item.aliases.join(", ")}
                </p>
              )}
              <div style={{ marginTop: "0.7rem" }}>
                <Link className="botao" to={`/doencas/${item.slug}${item.has_assistant && tab === "assistentes" ? "?modo=assistente" : ""}`}>
                  {item.has_assistant && tab === "assistentes" ? "Abrir assistente" : "Visualizar"}
                </Link>
              </div>
            </article>
          ))}
          {!items.length && !loading && <p className="cartao">Nenhum conteúdo corresponde aos filtros.</p>}
        </div>
      ))}

      {tab !== "areas" && hasMore && (
        <button className="botao botao--secundario" style={{ marginTop: "1rem" }} onClick={() => setPage((value) => value + 1)} disabled={loading}>
          {loading ? "Carregando…" : "Carregar mais"}
        </button>
      )}
    </>
  );
}
