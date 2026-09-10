// This snapshot is checked against the backend authority by the contract test.
import sections from "./documentEditorialTaxonomy.json";
export function documentSection(kind: string): string {
  return (sections as Record<string, string>)[kind.trim().toLowerCase()] ?? "geral";
}

export function studySection(kind: string): string {
  return documentSection(kind) === "diretriz" ? "diretriz" : "estudo";
}
