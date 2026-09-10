export const FAVORITES_CHANGED = "corvia:favorites-changed";
export const favoriteTypeLabel: Record<string, string> = {
  publicacao_original: "Publicações originais",
  documento: "Biblioteca", fluxograma: "Fluxogramas", medicamento: "Medicamentos", imagem: "Galeria",
  exame: "Exames", evidencia: "Evidências", estudo: "Estudos", diretriz: "Diretrizes e consensos",
  descoberta: "CorVIA Intelligence", doenca: "Guia de doenças", triagem: "Triagem de sintomas",
  calculadora: "Calculadoras", caso_clinico: "Casos clínicos", trilha: "Trilhas", emergencia: "Emergências",
  material_paciente: "Material para o paciente", checklist: "Checklists", funcao: "Funções do CorVIA",
  documento_cientifico_privado: "Minha biblioteca privada",
};
export type Favorite = {
  id: number; item_type: string; item_id: number | null; item_slug: string | null;
  title: string; url: string | null; meta: string | null; available: boolean;
  unavailable_reason?: string | null; private_reading?: { document_id: number } | null; reading: { entity_type: string; slug: string } | null;
};
export function favoriteSearchText(value: string): string {
  return value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR");
}
export function favoriteInternalUrl(value: string | null): string | null {
  if (!value || !value.startsWith("/") || value.startsWith("//") || /[\\\u0000-\u0020]/.test(value)) return null;
  try {
    const parsed = new URL(value, "https://corvia.invalid");
    return parsed.origin === "https://corvia.invalid" && !parsed.pathname.startsWith("/api/") ? value : null;
  } catch { return null; }
}
export function announceFavoriteChange(userId: number) {
  window.dispatchEvent(new CustomEvent(FAVORITES_CHANGED, { detail: { userId } }));
}
