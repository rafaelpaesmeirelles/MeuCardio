/** Cliente de API da "sessão email" (CorvIA Mail) — token PRÓPRIO, distinto
 * do token da conta Corvia em `lib/api.ts`. Decisão do Rafael em 30/07/2026:
 * a caixa de e-mail passou a ter senha própria, então o token que abre ela
 * também precisa ser outro — reutilizar `api.ts` faria um 401 daqui
 * redirecionar para `/entrar` (a conta Corvia) em vez de `/corvia-mail`
 * (a sessão certa), e um token roubado de um dos dois sistemas serviria
 * no outro. Ver `core/security.py` (`scope: "email"`) no backend. */
const BASE = import.meta.env.VITE_API_URL ?? "/api";
const TOKEN_KEY = "corviamail.token";

export const tokenEmail = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (v: string) => localStorage.setItem(TOKEN_KEY, v),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

export class ApiEmailError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const t = tokenEmail.get();
  if (t) headers.set("Authorization", `Bearer ${t}`);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${BASE}${path}`, { ...init, headers });
  if (res.status === 401) {
    tokenEmail.clear();
    throw new ApiEmailError(401, "Sessão da caixa de e-mail expirada.");
  }
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new ApiEmailError(res.status, detail?.detail ?? "Não foi possível concluir a solicitação.");
  }
  return res.status === 204 ? (undefined as T) : res.json();
}

export const apiEmail = {
  get: <T>(p: string) => request<T>(p),
  post: <T>(p: string, body?: unknown) =>
    request<T>(p, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(p: string) => request<T>(p, { method: "DELETE" }),

  async entrar(endereco: string, senha: string) {
    const dados = await request<{ access_token: string }>("/email/entrar", {
      method: "POST",
      body: JSON.stringify({ endereco, senha }),
    });
    tokenEmail.set(dados.access_token);
    return dados;
  },
};
