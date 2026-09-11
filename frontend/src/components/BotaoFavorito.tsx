import { useEffect, useRef, useState } from "react";
import "../styles/favorite-control.css";
import { api, READ_TIMEOUT_MS } from "../lib/api";
import { useAuth } from "../lib/auth";
import { announceFavoriteChange, FAVORITES_CHANGED } from "../lib/favorites";

type FavoriteStatus = { favorited: boolean; favorite_id: number | null; available: boolean };

export default function BotaoFavorito({ itemType, itemId, itemSlug, label, className = "" }: {
  itemType: string; itemId?: number; itemSlug?: string; label?: string; className?: string;
}) {
  const { usuario } = useAuth();
  const userId = usuario?.id;
  const identity = `${userId ?? ""}/${itemType}/${itemSlug ?? itemId ?? ""}`;
  const identityRef = useRef(identity);
  identityRef.current = identity;
  const requestSequence = useRef(0);
  const active = useRef(true);
  useEffect(() => { active.current = true; return () => { active.current = false; }; }, []);
  const mutationIdentity = useRef<string | null>(null);
  const [resolved, setResolved] = useState<{ identity: string; value: FavoriteStatus } | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  const validTarget = Boolean(itemSlug) || (typeof itemId === "number" && Number.isSafeInteger(itemId) && itemId > 0);

  useEffect(() => {
    const sequence = ++requestSequence.current;
    let active = true;
    setResolved(null); setError(""); setBusy(false); mutationIdentity.current = null;
    if (!userId || !validTarget) return;
    const controller = new AbortController();
    const query = new URLSearchParams({ item_type: itemType });
    if (itemSlug) query.set("item_slug", itemSlug);
    else query.set("item_id", String(itemId));
    api.get<FavoriteStatus>(`/favorites/status?${query}`, { signal: controller.signal, timeoutMs: READ_TIMEOUT_MS }).then(value => {
      if (active && sequence === requestSequence.current && identityRef.current === identity) setResolved({ identity, value });
    }).catch(() => {
      if (active && sequence === requestSequence.current && identityRef.current === identity) setError("Não foi possível consultar este favorito.");
    });
    return () => { active = false; controller.abort(); };
  }, [identity, userId, itemType, itemId, itemSlug, validTarget, attempt]);

  useEffect(() => {
    const changed = (event: Event) => {
      if ((event as CustomEvent<{ userId: number }>).detail?.userId === userId && mutationIdentity.current !== identityRef.current) {
        setAttempt(value => value + 1);
      }
    };
    window.addEventListener(FAVORITES_CHANGED, changed);
    return () => window.removeEventListener(FAVORITES_CHANGED, changed);
  }, [userId]);

  const status = resolved?.identity === identity ? resolved.value : null;
  async function alternar() {
    if (!userId || !status || mutationIdentity.current === identity || (!status.available && !status.favorited)) return;
    mutationIdentity.current = identity; setBusy(true); setError("");
    requestSequence.current++;
    try {
      let next: FavoriteStatus;
      if (status.favorited) {
        if (status.favorite_id == null) throw new Error("missing favorite identity");
        await api.delete(`/favorites/by-id/${status.favorite_id}`);
        next = { ...status, favorited: false, favorite_id: null };
      } else {
        const saved = await api.post<{ id: number }>("/favorites", { item_type: itemType, ...(itemSlug ? { item_slug: itemSlug } : { item_id: itemId }) });
        next = { ...status, favorited: true, favorite_id: saved.id };
      }
      if (!active.current || identityRef.current !== identity) return;
      setResolved({ identity, value: next });
      announceFavoriteChange(userId);
    } catch {
      if (active.current && identityRef.current === identity) setError("Não foi possível atualizar o favorito. Tente novamente.");
    } finally {
      if (active.current && identityRef.current === identity) { mutationIdentity.current = null; setBusy(false); }
    }
  }
  if (!userId || !validTarget) return null;
  return <span className={`favorite-control ${className}`}>
    <button className="botao botao--secundario" type="button" onClick={() => void alternar()}
      disabled={busy || !status || (!status.available && !status.favorited)}
      aria-pressed={status?.favorited ?? false} aria-busy={busy || (!status && !error)}
      aria-label={label ? `${status?.favorited ? "Remover dos favoritos" : "Favoritar"}: ${label}` : undefined}
      style={{ padding: "0.35rem 0.75rem", fontSize: "0.86rem", minHeight: 44 }}>
      {busy ? "Salvando…" : !status ? error ? "Favorito não consultado" : "Consultando favorito…" : status.favorited ? "★ Favoritado" : "☆ Favoritar"}
    </button>
    {status && !status.available && !status.favorited && <small>Conteúdo indisponível para salvar.</small>}
    {error && <span role="alert">{error}{!status && <button type="button" className="botao botao--secundario" onClick={() => setAttempt(value => value + 1)}>Tentar novamente</button>}</span>}
  </span>;
}
