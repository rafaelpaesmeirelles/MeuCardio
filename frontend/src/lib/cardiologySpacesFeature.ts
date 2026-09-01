export function cardiologySpacesEnabled() {
  // Cardiology Spaces é a experiência canônica. O legado permanece como
  // rollback operacional explícito: definir a variável como "false" volta ao
  // Main OS anterior sem exigir novo build de código.
  return import.meta.env.VITE_CARDIOLOGY_SPACES_ENABLED !== "false";
}

/**
 * A conexão de novas contas Google permanece oculta enquanto a homologação é
 * concluída. A flag é deliberadamente opt-in: builds sem a variável não
 * oferecem o OAuth, mas continuam exibindo contas já vinculadas para que o
 * usuário possa revisar ou remover o vínculo.
 */
export function googleAccountConnectVisible() {
  return import.meta.env.VITE_GOOGLE_ACCOUNT_CONNECT_VISIBLE === "true";
}
