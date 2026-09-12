export type CalculatorField = {
  name: string; label: string; type: string; unit?: string | null;
  options: {value: string | number | boolean; label: string}[];
  min?: number | null; max?: number | null; required?: boolean;
  required_when?: Record<string, (string | number | boolean)[]> | null;
};

export function calculatorFieldRequired(field: CalculatorField, values: Record<string, unknown>) {
  return field.required_when
    ? Object.entries(field.required_when).some(([key, options]) => options.some(value => value === values[key]))
    : field.required !== false;
}

export function validateCalculatorFields(fields: CalculatorField[], values: Record<string, unknown>) {
  const errors: Record<string, string> = {};
  for (const field of fields) {
    const value = values[field.name];
    const missing = value === undefined || value === null || (typeof value === "string" && !value.trim());
    if (missing) {
      if (field.type === "boolean" && value === undefined) continue;
      if (calculatorFieldRequired(field, values)) errors[field.name] = "Preenchimento obrigatório.";
      continue;
    }
    if (field.type === "number") {
      const number = typeof value === "number" || typeof value === "string" ? Number(value) : NaN;
      if (!Number.isFinite(number)) errors[field.name] = "Informe um número finito.";
      else if (field.min != null && number < field.min) errors[field.name] = `Mínimo: ${field.min}${field.unit ? ` ${field.unit}` : ""}.`;
      else if (field.max != null && number > field.max) errors[field.name] = `Máximo: ${field.max}${field.unit ? ` ${field.unit}` : ""}.`;
    } else if (field.type === "boolean" && typeof value !== "boolean") {
      errors[field.name] = "Selecione sim ou não.";
    } else if (field.type === "select" && !field.options.some(option => option.value === value)) {
      errors[field.name] = "Selecione uma opção da lista.";
    }
  }
  return errors;
}
