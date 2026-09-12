const KEY = "corvia:login-return:v1";

/** Accept only an in-app destination, never a login/token loop or an external URL. */
export function safeLoginReturn(value: unknown): string | null {
  if (typeof value !== "string" || !value.startsWith("/") || value.startsWith("//")
      || /[\\\u0000-\u001f\u007f]/.test(value) || value.length > 4096) return null;
  try {
    const url = new URL(value, "https://corvia.invalid");
    if (url.origin !== "https://corvia.invalid"
        || /^\/(?:entrar|solicitar-acesso|esqueci-senha|ativar-conta|redefinir-senha)(?:\/|$)/i.test(url.pathname)
        || (url.pathname === "/" && !url.search && !url.hash)) return null;
    return url.pathname + url.search + url.hash;
  } catch { return null; }
}

export function saveLoginReturn(value: string) {
  const path = safeLoginReturn(value);
  if (!path) return;
  try { window.sessionStorage.setItem(KEY, path); } catch { /* Storage may be unavailable. */ }
}

export function readLoginReturn(): string | null {
  try { return safeLoginReturn(window.sessionStorage.getItem(KEY)); } catch { return null; }
}

export function clearLoginReturn() {
  try { window.sessionStorage.removeItem(KEY); } catch { /* Logout must still work. */ }
}
