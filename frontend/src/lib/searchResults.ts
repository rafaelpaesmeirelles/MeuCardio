export type ClinicalRole = "direct" | "conditional" | "comparison" | "mention";
export type MatchReason = { source: string; description: string };
export type SearchResult = {
  slug: string; title: string; kind: string; frente?: string; secao?: string;
  theme: string | null; snippet: string; ano?: number; rank?: number;
  relation_type?: string | null; context_only?: boolean;
  clinical_role?: ClinicalRole; clinical_context?: string | null;
  match_reasons?: MatchReason[]; relevance_order?: number;
  // A duplicate may carry another qualification. Keep every supplied meaning.
  clinical_contexts?: string[]; clinical_roles?: ClinicalRole[]; relation_types?: string[];
};

export function resultIdentity(item: Pick<SearchResult, "frente" | "kind" | "slug">): string {
  return `${item.frente || "documento"}:${item.slug}`;
}

export function mergeSearchResults(current: SearchResult[], incoming: SearchResult[]): SearchResult[] {
  const merged = new Map<string, SearchResult>();
  for (const item of [...current, ...incoming]) {
    const key = resultIdentity(item), previous = merged.get(key);
    const contexts = [...new Set([
      ...(previous?.clinical_contexts ?? []), previous?.clinical_context,
      ...(item.clinical_contexts ?? []), item.clinical_context,
    ].filter((value): value is string => Boolean(value?.trim())))];
    const roles = [...new Set([
      ...(previous?.clinical_roles ?? []), previous?.clinical_role,
      ...(item.clinical_roles ?? []), item.clinical_role,
    ].filter((value): value is ClinicalRole => Boolean(value)))];
    const relations = [...new Set([
      ...(previous?.relation_types ?? []), previous?.relation_type,
      ...(item.relation_types ?? []), item.relation_type,
    ].filter((value): value is string => Boolean(value)))];
    const reasons = new Map<string, MatchReason>();
    for (const reason of [...(previous?.match_reasons ?? []), ...(item.match_reasons ?? [])]) {
      reasons.set(JSON.stringify([reason.source, reason.description]), reason);
    }
    merged.set(key, {
      ...previous, ...item,
      relevance_order: previous?.relevance_order ?? item.relevance_order,
      context_only: Boolean(previous?.context_only || item.context_only),
      clinical_contexts: contexts, clinical_roles: roles, relation_types: relations,
      match_reasons: [...reasons.values()],
    });
  }
  // The backend owns relevance. Stable sort only restores its absolute order
  // when pages overlap; legacy responses without that field retain API order.
  const results = [...merged.values()];
  return results.every((item) => Number.isFinite(item.relevance_order))
    ? results.sort((a, b) => a.relevance_order! - b.relevance_order!) : results;
}
