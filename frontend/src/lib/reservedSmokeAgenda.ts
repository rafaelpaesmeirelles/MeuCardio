export const RESERVED_SMOKE_TEST_MARKER = "[SMOKE-TEST]";

// Variante histórica confirmada em produção (incidente `[SMOKE-TESTE] Bloco C`,
// 19/08/2026): três rotinas de trabalho criadas manualmente com o literal em
// português ("TESTE"), nunca corrigidas pela migration nem pelo filtro porque
// nenhum dos dois reconhecia essa grafia. Mantido como um segundo literal
// exato — não um regex/prefixo genérico — para não esconder conteúdo legítimo
// que apenas contenha a palavra "teste".
const RESERVED_SMOKE_TEST_MARKER_HISTORICO = "[SMOKE-TESTE]";

const RESERVED_SMOKE_TEST_IDENTITY_FIELDS = [
  "title",
  "patient_name",
  "label",
  "service_name",
  "appointment_type",
] as const;

/**
 * Reconhece o marcador reservado (e a variante histórica confirmada) somente
 * no início de um campo de identidade. Menções no meio do texto, notas e
 * campos aninhados permanecem dados legítimos.
 */
export function hasReservedSmokeTestMarker(value: unknown): boolean {
  if (typeof value !== "string") return false;
  const trimmed = value.trimStart();
  return trimmed.startsWith(RESERVED_SMOKE_TEST_MARKER)
    || trimmed.startsWith(RESERVED_SMOKE_TEST_MARKER_HISTORICO);
}

export function isReservedSmokeTestRecord(value: unknown): boolean {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const record = value as Record<string, unknown>;
  return RESERVED_SMOKE_TEST_IDENTITY_FIELDS.some((field) => hasReservedSmokeTestMarker(record[field]));
}

export function withoutReservedSmokeTestRecords<T>(items: readonly T[]): T[] {
  return items.filter((item) => !isReservedSmokeTestRecord(item));
}

export function withoutReservedSmokeTestRecord<T>(item: T | null | undefined): T | null {
  return item == null || isReservedSmokeTestRecord(item) ? null : item;
}
