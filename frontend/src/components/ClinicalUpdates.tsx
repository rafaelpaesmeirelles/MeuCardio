import type { CSSProperties } from "react";

export type ClinicalUpdate = {
  guideline: { org: string; title: string; year: number | null };
  target_section?: string | null;
  change_summary?: string | null;
  recommendation?: string | null;
  source_url?: string | null;
};

export default function ClinicalUpdates({
  updates,
  style,
}: {
  updates?: ClinicalUpdate[];
  style?: CSSProperties;
}) {
  if (!updates?.length) return null;
  return (
    <section className="cartao" style={{ marginTop: "0.8rem", ...style }}>
      <p className="eyebrow">CorVIA Intelligence</p>
      <h2>Atualizações científicas vigentes</h2>
      <div style={{ display: "grid", gap: "0.8rem" }}>
        {updates.map((update, index) => (
          <article key={`${update.guideline.org}-${update.guideline.year}-${index}`}>
            <strong>{update.change_summary || update.guideline.title}</strong>
            {update.recommendation && <p>{update.recommendation}</p>}
            <small>
              {update.guideline.org}
              {update.guideline.year ? ` · ${update.guideline.year}` : ""}
              {update.target_section ? ` · ${update.target_section}` : ""}
              {` · ${update.guideline.title}`}
            </small>
            {update.source_url && (
              <div>
                <a href={update.source_url} target="_blank" rel="noopener noreferrer">
                  Conferir fonte oficial ↗
                </a>
              </div>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
