const BASE = import.meta.env.VITE_API_URL ?? "/api";
const TOKEN_KEY = "cardiobene.token";

export const token = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (v: string) => localStorage.setItem(TOKEN_KEY, v),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const t = token.get();
  if (t) headers.set("Authorization", `Bearer ${t}`);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${BASE}${path}`, { ...init, headers });
  if (res.status === 401) {
    token.clear();
    window.location.assign("/entrar");
    throw new ApiError(401, "Sessão expirada.");
  }
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new ApiError(res.status, detail?.detail ?? "Não foi possível concluir a solicitação.");
  }
  return res.status === 204 ? (undefined as T) : res.json();
}

export const api = {
  get: <T>(p: string) => request<T>(p),
  post: <T>(p: string, body?: unknown) =>
    request<T>(p, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(p: string, body: unknown) =>
    request<T>(p, { method: "PATCH", body: JSON.stringify(body) }),
  put: <T>(p: string, body: unknown) =>
    request<T>(p, { method: "PUT", body: JSON.stringify(body) }),
  delete: <T>(p: string) => request<T>(p, { method: "DELETE" }),

  async login(email: string, password: string) {
    const form = new URLSearchParams({ username: email, password });
    const res = await fetch(`${BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });
    if (!res.ok) throw new ApiError(res.status, "E-mail ou senha incorretos.");
    const data = (await res.json()) as { access_token: string };
    token.set(data.access_token);
    return data;
  },
};

export type Usuario = {
  id: number;
  email: string;
  full_name: string;
  crm: string | null;
  role: string;
};
