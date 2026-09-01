export const RESERVED_SMOKE_TEST_MARKER = "[SMOKE-TEST]";

const RESERVED_SMOKE_TEST_IDENTITY_FIELDS = [
  "title",
  "patient_name",
  "label",
  "service_name",
  "appointment_type",
] as const;

/**
 * Reconhece somente o marcador reservado no início de um campo de identidade.
 * Menções no meio do texto, notas e campos aninhados permanecem dados legítimos.
 */
export function hasReservedSmokeTestMarker(value: unknown): boolean {
  return typeof value === "string"
    && value.trimStart().startsWith(RESERVED_SMOKE_TEST_MARKER);
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
