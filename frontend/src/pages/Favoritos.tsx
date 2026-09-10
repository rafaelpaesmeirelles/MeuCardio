import { lazy, Suspense, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import { Carregando, Vazio } from "../components/Estado";
import { announceFavoriteChange, FAVORITES_CHANGED, favoriteInternalUrl, favoriteSearchText, favoriteTypeLabel, type Favorite } from "../lib/favorites";
import "../styles/favorites.css";

const ScientificReadingAccess = lazy(() => import("../components/ScientificReadingAccess"));

export default function Favoritos() {
  const { usuario } = useAuth();
  const userId = usuario?.id;
  const currentUser = useRef(userId);
  currentUser.current = userId;
  const [loaded, setLoaded] = useState<{ userId: number; items: Favorite[] } | null>(null);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [type, setType] = useState("");
  const [attempt, setAttempt] = useState(0);
  const [removing, setRemoving] = useState<Set<number>>(new Set());
  const pending = useRef(new Set<number>());
  const active = useRef(true);
  const loadSequence = useRef(0);

  useEffect(() => {
    active.current = true;
    return () => { active.current = false; };
  }, []);
  useEffect(() => {
    setQuery(""); setType(""); setRemoving(new Set()); pending.current = new Set();
  }, [userId]);
  useEffect(() => {
    const sequence = ++loadSequence.current;
    let valid = true;
    setError("");
    if (!userId) { setLoaded(null); return; }
    api.get<Favorite[]>("/favorites").then(items => {
      if (valid && active.current && sequence === loadSequence.current && currentUser.current === userId) setLoaded({ userId, items });
    }).catch(() => { if (valid && active.current && currentUser.current === userId) setError("Não foi possível carregar seus favoritos."); });
    return () => { valid = false; };
  }, [userId, attempt]);
  useEffect(() => {
    const changed = (event: Event) => {
      if ((event as CustomEvent<{ userId: number }>).detail?.userId === userId) setAttempt(value => value + 1);
    };
    window.addEventListener(FAVORITES_CHANGED, changed);
    return () => window.removeEventListener(FAVORITES_CHANGED, changed);
  }, [userId]);

  async function remover(item: Favorite) {
    if (!userId || pending.current.has(item.id)) return;
    pending.current.add(item.id); setRemoving(new Set(pending.current)); setError("");
    loadSequence.current++;
    try {
      await api.delete(`/favorites/by-id/${item.id}`);
      if (!active.current || currentUser.current !== userId) return;
      loadSequence.current++;
      setLoaded(value => value?.userId === userId ? { userId, items: value.items.filter(entry => entry.id !== item.id) } : value);
      announceFavoriteChange(userId);
    } catch {
      if (active.current && currentUser.current === userId) setError("Não foi possível remover o favorito. Ele continua salvo; tente novamente.");
    } finally {
      if (active.current && currentUser.current === userId) { pending.current.delete(item.id); setRemoving(new Set(pending.current)); }
    }
  }

  const items = loaded?.userId === userId ? loaded?.items ?? null : null;
  const types = [...new Set((items ?? []).map(item => item.item_type))].sort((a, b) => (favoriteTypeLabel[a] ?? a).localeCompare(favoriteTypeLabel[b] ?? b, "pt-BR"));
  const term = favoriteSearchText(query.trim());
  const filtered = (items ?? []).filter(item => (!type || item.item_type === type) && (!term || favoriteSearchText([item.title, item.meta, favoriteTypeLabel[item.item_type] ?? item.item_type].filter(Boolean).join(" ")).includes(term)));
  if (!userId) return null;
  return <section className="favorites-page">
    <p className="eyebrow">Sua coleção no CorVIA</p>
    <h1>Meus Favoritos</h1>
    <p>Reúna conteúdos e funções para retomar quando precisar. As versões científicas disponíveis acompanham cada fonte.</p>
    {error && <p role="alert">{error} <button className="botao botao--secundario" type="button" onClick={() => setAttempt(value => value + 1)}>Tentar novamente</button></p>}
    {items === null ? !error && <Carregando /> : !items.length ? <Vazio titulo="Nenhum favorito ainda" acao="Use Favoritar nos conteúdos e nas funções do CorVIA para reunir seus acessos aqui." /> : <>
      <div className="favorites-page__filters">
        <label>Buscar nos favoritos<input type="search" value={query} onChange={event => setQuery(event.target.value)} placeholder="Título, tema ou categoria" /></label>
        <label>Categoria<select value={type} onChange={event => setType(event.target.value)}><option value="">Todas as categorias</option>{types.map(value => <option value={value} key={value}>{favoriteTypeLabel[value] ?? value}</option>)}</select></label>
      </div>
      <p role="status">{filtered.length} de {items.length} favoritos</p>
      {!filtered.length && <Vazio titulo="Nenhum favorito encontrado" acao="Altere a busca ou a categoria para ver os demais itens salvos." />}
      <div className="favorites-page__items">{filtered.map(item => {
        const url = item.available ? favoriteInternalUrl(item.url) : null;
        const readable = item.available && item.item_type !== "documento_cientifico_privado" && item.reading;
        return <article className="cartao favorites-page__item" key={item.id}>
          <div className="favorites-page__item-header"><div>
            <p className="eyebrow">{favoriteTypeLabel[item.item_type] ?? item.item_type}{item.meta ? ` · ${item.meta}` : ""}</p>
            <h2>{url ? <Link to={url}>{item.title}</Link> : item.title || "Conteúdo indisponível"}</h2>
            {!item.available && <p>{item.unavailable_reason || "Este conteúdo não está disponível atualmente. Você pode remover o favorito."}</p>}
            {item.item_type === "documento_cientifico_privado" && item.available && <p>Abra o documento privado para consultar o original e as versões em português disponíveis.</p>}
          </div><button className="botao botao--secundario" type="button" disabled={removing.has(item.id)} onClick={() => void remover(item)} aria-label={`Remover dos favoritos: ${item.title || "conteúdo indisponível"}`}>{removing.has(item.id) ? "Removendo…" : "Remover"}</button></div>
          {item.available && item.item_type === "documento_cientifico_privado" && item.private_reading && Number.isSafeInteger(item.private_reading.document_id) && item.private_reading.document_id > 0 && <nav className="favorites-page__private-reading" aria-label="Leitura do seu documento privado">
            <Link className="botao botao--secundario" to={`/documentos-cientificos-ia?document=${item.private_reading.document_id}&leitura=resumo`}>Resumo em português</Link>
            <Link className="botao botao--secundario" to={`/documentos-cientificos-ia?document=${item.private_reading.document_id}&leitura=traduzido`}>Tradução em português</Link>
            <Link className="botao botao--secundario" to={`/documentos-cientificos-ia?document=${item.private_reading.document_id}&leitura=original`}>Original</Link>
          </nav>}
          {readable && <Suspense fallback={<p role="status">Carregando opções de leitura…</p>}><ScientificReadingAccess entityType={readable.entity_type} slug={readable.slug} lazy /></Suspense>}
        </article>;
      })}</div>
    </>}
  </section>;
}
