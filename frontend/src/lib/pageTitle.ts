import { findClinicalRoute } from "./clinicalRouteRegistry";

const publicTitles: Record<string, string> = {
  "/": "Início", "/entrar": "Entrar", "/produto": "Conheça o CorVIA",
  "/solicitar-acesso": "Solicitar acesso", "/esqueci-senha": "Recuperar acesso",
  "/redefinir-senha": "Redefinir senha", "/ativar-conta": "Ativar conta",
  "/privacidade": "Privacidade", "/termos": "Termos de uso", "/excluir-conta": "Excluir conta",
};

export function pageTitle(pathname: string): string {
  const path = pathname.replace(/\/+$/, "") || "/";
  const title = /^\/validar(?:\/|$)/.test(path) ? "Validar documento"
    : publicTitles[path] || findClinicalRoute(path)?.name || "Página não encontrada";
  // Route names never contain a patient's identity or the value of a search.
  return `${title} · CorVIA`;
}
