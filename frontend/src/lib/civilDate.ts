/** Civil dates have no timezone. Instants must use a separate formatter. */
export function formatCivilDate(value: string | null | undefined): string {
  if (!value) return "—";
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (!match) return "—";
  const [, year, month, day] = match;
  const date = new Date(`${value}T12:00:00Z`);
  if (!Number.isFinite(date.getTime()) || date.toISOString().slice(0, 10) !== value) return "—";
  return `${day}/${month}/${year}`;
}
