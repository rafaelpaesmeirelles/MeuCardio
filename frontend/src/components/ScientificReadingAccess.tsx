import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "../lib/api";
import "../styles/scientific-reading-access.css";

type ReadingText = { status: string; text?: string | null; origin?: string };
type ReadingArtifact = { status: string; url?: string | null; media_type?: string | null; reason?: string | null; coverage?: { scope?: string; figures?: string; supplements?: string }; notice?: string | null };
type ReadingSource = {
  key: string; title?: string; doi?: string | null; url?: string | null;
  original: ReadingArtifact; translation_pt: ReadingArtifact; summary_pt: ReadingText;
  license_url?: string | null; authors?: string | string[] | null; journal?: string | null; year?: number | null; attribution?: string | null;
};
type ScientificReading = {
  entity_type: string; slug: string; summary_pt: ReadingText; sources: ReadingSource[];
};

function externalUrl(value?: string | null): string | undefined {
  if (!value) return undefined;
  try { const url = new URL(value); return /^(https?:)$/.test(url.protocol) ? url.href : undefined; }
  catch { return undefined; }
}
function safeScientificSlug(value: unknown): value is string {
  return typeof value === "string" && Boolean(value) && !/[\\/?#%]/.test(value) && ![".", ".."].includes(value);
}
function artifactPath(value: string | null | undefined, entityType: string, slug: string | undefined, key: string | undefined, variant: "original" | "translation"): string | undefined {
  if (!value || !safeScientificSlug(slug) || !key || !/^[a-z_]+$/.test(entityType) || !/^[a-zA-Z0-9_-]+$/.test(key) || /[\\/?#]/.test(slug) || [".", ".."].includes(slug)) return undefined;
  const expected = `/scientific-reading/${entityType}/${encodeURIComponent(slug)}/sources/${key}/${variant}`;
  return value === expected || value === `/api${expected}` ? expected : undefined;
}
function statusText(artifact: { status: string; reason?: string | null }): string {
  if (artifact.status === "available") return "Disponível";
  if (["pending", "processing", "queued"].includes(artifact.status)) return "Em processamento";
  if (artifact.status === "blocked_license") return "A autorização da fonte para disponibilizar a tradução integral ainda não foi confirmada.";
  return artifact.reason || "Ainda não disponível para esta fonte.";
}

/** Published scientific sources only. GET is read-only; opening a reader never starts paid work. */
export default function ScientificReadingAccess({ entityType, slug, lazy = false }: {
  entityType: string; slug: string | undefined; lazy?: boolean;
}) {
  const identity = `${entityType}/${slug ?? ""}`;
  const [opened, setOpened] = useState(!lazy);
  const [attempt, setAttempt] = useState(0);
  const [data, setData] = useState<ScientificReading | null>(null);
  const [loadedIdentity, setLoadedIdentity] = useState("");
  const [error, setError] = useState("");
  const [sourceKey, setSourceKey] = useState("");
  const [reading, setReading] = useState<{ title: string; text: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const generation = useRef(0);
  const currentIdentity = useRef(identity);
  currentIdentity.current = identity;

  useEffect(() => {
    setOpened(!lazy); setData(null); setLoadedIdentity(""); setSourceKey(""); setReading(null); setError(""); setBusy(false);
  }, [identity, lazy]);
  useEffect(() => {
    const sequence = ++generation.current;
    if (!opened || !slug) return;
    let active = true;
    setError("");
    api.get<ScientificReading>(`/scientific-reading/${encodeURIComponent(entityType)}/${encodeURIComponent(slug)}`)
      .then(result => {
        if (!active || sequence !== generation.current || currentIdentity.current !== identity) return;
        // Aliases may resolve to a canonical published slug. Trust only the
        // identity returned by this request, within the requested entity type.
        if (result.entity_type !== entityType || !safeScientificSlug(result.slug)) throw new Error("Invalid scientific reading identity");
        setData(result); setLoadedIdentity(identity); setSourceKey(result.sources[0]?.key ?? "");
      })
      .catch(() => { if (active && currentIdentity.current === identity) setError("Não foi possível consultar as opções de leitura. O conteúdo abaixo continua disponível."); });
    return () => { active = false; };
  }, [opened, entityType, slug, identity, attempt]);

  const current = loadedIdentity === identity ? data : null;

  async function openArtifact(artifact: ReadingArtifact, translation: boolean) {
    const path = artifactPath(artifact.url, entityType, current?.slug, sourceKey, translation ? "translation" : "original");
    if (!path || busy) return;
    const requestIdentity = identity;
    const requestGeneration = generation.current;
    setBusy(true); setError("");
    try {
      const blob = await api.blob(path);
      if (requestIdentity !== currentIdentity.current || requestGeneration !== generation.current) return;
      if (translation) {
        const text = await blob.text();
        if (requestIdentity === currentIdentity.current && requestGeneration === generation.current) {
          setReading({ title: "Tradução integral em português", text });
        }
      } else {
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        const extension = /pdf/.test(artifact.media_type ?? blob.type) ? "pdf" : /xml/.test(artifact.media_type ?? blob.type) ? "xml" : "txt";
        link.download = `${current?.slug}-original.${extension}`;
        link.click();
        window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
      }
    } catch { if (requestIdentity === currentIdentity.current) setError("Não foi possível abrir o arquivo. Tente novamente."); }
    finally { if (requestIdentity === currentIdentity.current && requestGeneration === generation.current) setBusy(false); }
  }

  if (!slug) return null;
  const source = current?.sources.find(item => item.key === sourceKey);
  const originalExternal = externalUrl(source?.original.url ?? source?.url);
  const originalStored = source?.original.status === "available" && artifactPath(source.original.url, entityType, current?.slug, source.key, "original");
  const translationReady = source?.translation_pt.status === "available" && artifactPath(source.translation_pt.url, entityType, current?.slug, source.key, "translation");
  return <section className="scientific-reading-access cartao" aria-label="Leitura científica: resumo, tradução integral e original">
    <h2>Leitura científica</h2>
    {!opened ? <button className="btn" type="button" onClick={() => setOpened(true)}>Resumo em português · Tradução integral · Original</button> : <>
      {!current && !error && <p role="status">Consultando versões disponíveis…</p>}
      {current && <>
        {current.summary_pt.status === "available" && current.summary_pt.text && <button className="btn" type="button" onClick={() => setReading({ title: "Resumo editorial CorVIA em português", text: current.summary_pt.text! })}>Resumo editorial CorVIA em português</button>}
        {current.sources.length > 1 && <label>Fonte científica<select value={sourceKey} onChange={event => { setSourceKey(event.target.value); setReading(null); generation.current++; setBusy(false); }}>
          {current.sources.map((item, index) => <option value={item.key} key={item.key}>{item.title || item.doi || `Fonte ${index + 1}: ${item.url || item.key}`}</option>)}
        </select></label>}
        {source ? <div className="scientific-reading-access__source">
          <p className="scientific-reading-access__reference">{source.title || source.doi || source.url || "Fonte científica"}</p>
          {(source.authors || source.journal || source.year) && <p>{[Array.isArray(source.authors) ? source.authors.join(", ") : source.authors, source.journal, source.year].filter(Boolean).join(" · ")}</p>}
          <div className="scientific-reading-access__options">
            <div><button className="btn" type="button" disabled={source.summary_pt.status !== "available" || !source.summary_pt.text} onClick={() => setReading({ title: "Resumo da fonte em português", text: source.summary_pt.text! })}>Resumo em português</button><small>{statusText(source.summary_pt)}</small></div>
            <div><button className="btn" type="button" disabled={!translationReady || busy} onClick={() => void openArtifact(source.translation_pt, true)}>Tradução integral em português</button><small>{statusText(source.translation_pt)}</small></div>
            <div>{originalStored ? <button className="btn" type="button" disabled={busy} onClick={() => void openArtifact(source.original, false)}>Baixar original{source.original.media_type?.includes("xml") ? " (XML)" : ""}</button>
              : originalExternal ? <a className="btn" href={originalExternal} target="_blank" rel="noopener noreferrer">Original na fonte ↗</a>
                : <button className="btn" disabled type="button">Original</button>}
              <small>{originalStored ? "Arquivo disponível no CorVIA" : originalExternal ? "Acesso no site da publicação" : statusText(source.original)}</small></div>
          </div>
          {source.attribution && <p>{source.attribution}</p>}
          {(source.doi || source.title) && <p><Link to={`/busca?modo=tudo-com-tudo&q=${encodeURIComponent(source.doi || source.title || "")}`}>Relações no Tudo com Tudo</Link></p>}
          {translationReady && <p className="scientific-reading-access__coverage">{source.translation_pt.notice || "Tradução assistida por IA do texto do artigo. Consulte também a publicação original."}{source.translation_pt.coverage?.figures === "captions_only" && " Inclui as legendas; as figuras permanecem na publicação original."}{source.translation_pt.coverage?.supplements === "not_included" && " Materiais suplementares não estão incluídos."}</p>}
          {externalUrl(source.license_url) && <a href={externalUrl(source.license_url)} target="_blank" rel="noopener noreferrer">Licença da fonte ↗</a>}
        </div> : <p>Nenhuma fonte externa identificada neste conteúdo. O texto editorial em português permanece disponível nesta página.</p>}
      </>}
      {busy && <p role="status">Abrindo arquivo…</p>}
      {reading && current && <article className="scientific-reading-access__reader"><h3>{reading.title}</h3><button className="btn" type="button" onClick={() => setReading(null)}>Fechar leitura</button><div><Markdown remarkPlugins={[remarkGfm]}>{reading.text}</Markdown></div></article>}
    </>}
    {error && <p role="alert">{error} <button className="btn" type="button" onClick={() => setAttempt(value => value + 1)}>Tentar novamente</button></p>}
  </section>;
}
