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

type Tab = "catalogo" | "assistentes" | "congenitas" | "fetal";

const AREAS = [
  ["", "Todas as áreas"],
  ["cardiopediatria", "Cardiopediatria"],
  ["cardiogeriatria", "Cardiogeriatria"],
  ["cardiooncologia", "Cardio-oncologia"],
  ["gravidez", "Cardiologia na gravidez"],
] as const;

const TAB_LABELS: Record<Tab, string> = {
  catalogo: "Catálogo",
  assistentes: "Assistentes por doença",
  congenitas: "Cardiopatias congênitas",
  fetal: "Cardiologia fetal",
};

function labelArea(area: string) {
  return AREAS.find(([value]) => value === area)?.[1] ?? area;
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
  const [cyanosis, setCyanosis] = useState(params.get("cyanosis") || "");
  const [items, setItems] = useState<Disease[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const filters = useMemo(() => {
    const result: Record<string, string> = { page_size: "60", page: String(page) };
    if (q.trim()) result.q = q.trim();
    if (area) result.area = area;
    if (tab === "assistentes") result.assistant_only = "true";
    if (tab === "congenitas") result.category = "cardiopatia_congenita";
    if (tab === "fetal") result.category = "cardiologia_fetal";
    if (cyanosis && tab === "congenitas") result.cyanosis_class = cyanosis;
    return result;
  }, [q, area, tab, cyanosis, page]);

  useEffect(() => {
    setLoading(true);
    setError("");
    const search = new URLSearchParams(filters).toString();
    api.get<Response>(`/specialty-guides/diseases?${search}`)
      .then((response) => {
        setItems((previous) => page === 1 ? response.items : [...previous, ...response.items]);
        setHasMore(response.has_more);
        setTotal(response.total);
      })
      .catch((cause) => setError(cause.message))
      .finally(() => setLoading(false));
  }, [filters, page]);

  function changeTab(next: Tab) {
    setPage(1);
    setItems([]);
    setCyanosis("");
    const nextParams = new URLSearchParams();
    nextParams.set("tab", next);
    if (q.trim()) nextParams.set("q", q.trim());
    if (area) nextParams.set("area", area);
    setParams(nextParams);
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
            className="painel__tema"
            onClick={() => changeTab(value)}
            aria-selected={tab === value}
            style={tab === value ? { borderColor: "var(--acento)", fontWeight: 700 } : undefined}
          >
            {TAB_LABELS[value]}
          </button>
        ))}
      </div>

      <section className="cartao" style={{ marginTop: "1rem" }}>
        <div style={{ display: "grid", gridTemplateColumns: "minmax(15rem, 2fr) minmax(12rem, 1fr)", gap: "0.7rem" }}>
          <label>
            <strong>Pesquisar</strong>
            <input
              value={q}
              onChange={(event) => updateSearch(event.target.value)}
              placeholder="Nome, sigla, sinônimo, sintoma ou tema…"
              style={{ marginTop: "0.35rem" }}
            />
          </label>
          <label>
            <strong>Área</strong>
            <select
              value={area}
              onChange={(event) => { setArea(event.target.value); setPage(1); setItems([]); }}
              style={{ marginTop: "0.35rem" }}
            >
              {AREAS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
        </div>

        {tab === "congenitas" && (
          <div className="painel__temas" style={{ marginTop: "0.8rem" }}>
            {["", "acianotica", "cianotica"].map((value) => (
              <button
                key={value || "todas"}
                className="painel__tema"
                onClick={() => { setCyanosis(value); setPage(1); setItems([]); }}
                style={cyanosis === value ? { borderColor: "var(--acento)" } : undefined}
              >
                {value ? labelCyanosis(value) : "Todas"}
              </button>
            ))}
          </div>
        )}
      </section>

      <p style={{ marginTop: "1rem", color: "var(--texto-secundario)" }}>
        {total} {total === 1 ? "tema encontrado" : "temas encontrados"}
      </p>

      {error && <Erro mensagem={error} />}
      {loading && page === 1 ? <Carregando /> : (
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
      )}

      {hasMore && (
        <button className="botao botao--secundario" style={{ marginTop: "1rem" }} onClick={() => setPage((value) => value + 1)} disabled={loading}>
          {loading ? "Carregando…" : "Carregar mais"}
        </button>
      )}
    </>
  );
}
