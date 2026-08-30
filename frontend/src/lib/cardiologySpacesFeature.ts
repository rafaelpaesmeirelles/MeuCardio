export function cardiologySpacesEnabled() {
  // Cardiology Spaces é a experiência canônica. O legado permanece como
  // rollback operacional explícito: definir a variável como "false" volta ao
  // Main OS anterior sem exigir novo build de código.
  return import.meta.env.VITE_CARDIOLOGY_SPACES_ENABLED !== "false";
}
