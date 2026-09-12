const VITAL_LABELS: Record<string, string> = {
  pa_sistolica: "PA sistólica", pa_diastolica: "PA diastólica", fc: "Frequência cardíaca",
  fr: "Frequência respiratória", temperatura: "Temperatura", spo2: "SpO₂",
};

export function parseVitalSigns(values: Record<string, string>): Record<string, number> {
  const result: Record<string, number> = {};
  for (const [key, label] of Object.entries(VITAL_LABELS)) {
    const raw = values[key]?.trim();
    if (!raw) continue;
    const value = Number(raw.replace(",", "."));
    if (!/^[+-]?\d+(?:[.,]\d+)?$/.test(raw) || !Number.isFinite(value) || value < 0 || (key === "spo2" && value > 100)) {
      throw new Error(`${label}: informe um número válido${key === "spo2" ? " entre 0 e 100" : " não negativo"}.`);
    }
    result[key] = value;
  }
  return result;
}

export function incompletePrescription(items: Array<{drug_name?: string; presentation?: string; posology?: string}>): boolean {
  return !items.length || items.some(item => !item.drug_name?.trim() || !item.presentation?.trim() || !item.posology?.trim());
}
