import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../lib/api";

type EditorialDocument = { slug: string; title: string; theme: string; kind?: string; study_type?: string; summary?: string | null };
type Page = { items: EditorialDocument[]; total: number; next_offset: number | null };

export default function EditorialDocumentList({ section, title, query: controlledQuery, theme, source = "library" }: {
  section: "diretriz" | "estudo"; title: string; query?: string; theme?: string; source?: "library" | "studies";
}) {
  const [localQuery, setQuery] = useState("");
  const query = controlledQuery ?? localQuery;
  const [items, setItems] = useState<EditorialDocument[]>([]);
  const [total, setTotal] = useState(0);
  const [next, setNext] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const seq = useRef(0), busy = useRef(false);

  async function load(offset: number, id: number, replace: boolean) {
    if (id !== seq.current || busy.current) return;
    busy.current = true; setLoading(true); setError("");
    try {
      const params = new URLSearchParams({ secao: section, limit: "50", offset: String(offset) });
      if (query.trim()) params.set("q", query.trim());
      if (theme) params.set("theme", theme);
      const page = await api.get<Page>(`${source === "library" ? "/library/documents" : "/studies"}?${params}`);
      if (id !== seq.current) return;
      setItems(current => [...new Map([...(replace ? [] : current), ...page.items].map(item => [item.slug, item])).values()]);
      setTotal(page.total); setNext(page.next_offset);
    } catch (e) {
      if (id === seq.current) setError(e instanceof ApiError ? e.message : "Não foi possível carregar os documentos. Tente novamente.");
    } finally {
      if (id === seq.current) { busy.current = false; setLoading(false); }
    }
  }

  useEffect(() => {
    const id = ++seq.current;
    busy.current = false; setItems([]); setTotal(0); setNext(null); setLoading(true); setError("");
    const timer = setTimeout(() => { void load(0, id, true); }, 200);
    return () => { clearTimeout(timer); ++seq.current; };
    // Each request captures the current filter; stale responses cannot replace it.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [section, query, theme, source]);

  return <section className="cartao" aria-label={title} aria-busy={loading}>
    <p className="eyebrow">{source === "library" ? "Biblioteca científica" : "Catálogo de estudos"}</p><h2>{title}</h2>
    {controlledQuery === undefined && <label>Buscar nesta coleção<input type="search" value={query} onChange={e => setQuery(e.target.value)} aria-label={`Buscar em ${title}`} /></label>}
    <p>{items.length} de {total} documentos carregados</p>
    {error && <p role="alert">{error}</p>}
    <div className="cc-literature-list">{items.map(item => <Link key={item.slug} to={`${source === "library" ? "/biblioteca" : "/estudos"}/${encodeURIComponent(item.slug)}`} className="cc-literature-row">
      <span className="cc-literature-row__body"><small>{item.kind || item.study_type} · {item.theme} · {source === "library" ? "Biblioteca" : "Catálogo de estudos"}</small><strong>{item.title}</strong>{item.summary && <span>{item.summary}</span>}</span>
    </Link>)}</div>
    {!loading && !error && total === 0 && <p>Nenhum documento encontrado nesta coleção.</p>}
    {loading && <p role="status">Carregando documentos…</p>}
    {!loading && (next !== null || error) && <button type="button" className="botao botao--secundario" onClick={() => void load(next ?? 0, seq.current, items.length === 0)}>{error ? "Tentar novamente" : "Carregar mais documentos"}</button>}
  </section>;
}
