/** Only the subject itself can expand the query's graph automatically.
 * A neighbour of a search hit is not necessarily relevant to the user's query.
 */
export function searchIdentity(value: string): string {
  return value.normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
    .toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

export function exactSearchAnchors<T extends { title: string; slug: string }>(
  items: T[], query: string,
): T[] {
  const identity = searchIdentity(query);
  if (!identity) return [];
  return items.filter((item) => searchIdentity(item.title) === identity
    || searchIdentity(item.slug) === identity);
}
