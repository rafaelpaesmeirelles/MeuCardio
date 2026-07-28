const BASE = import.meta.env.VITE_API_URL ?? "/api";
const TOKEN_KEY = "meucardio.token";

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
  // FormData fica de fora: quem define o Content-Type dela é o browser, que
  // precisa incluir o boundary do multipart. Forçar application/json aqui
  // quebraria todo upload de arquivo.
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${BASE}${path}`, { ...init, headers });
  if (res.status === 401) {
    token.clear();
    window.location.assign("/entrar");
    throw new ApiError(401, "Sessão expirada.");
  }
  // 402 = logado, porém sem assinatura vigente. Não limpa o token: a sessão
  // continua válida, só falta assinar.
  if (res.status === 402) {
    if (!window.location.pathname.startsWith("/assinatura")) {
      window.location.assign("/assinatura?status=necessaria");
    }
    throw new ApiError(402, "Assinatura necessária.");
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

  /** Envio de arquivo. Não define Content-Type de propósito: o browser precisa
   *  gerar o boundary do multipart sozinho. */
  upload: <T>(p: string, campo: string, arquivo: File) => {
    const form = new FormData();
    form.append(campo, arquivo);
    return request<T>(p, { method: "POST", body: form });
  },

  /** Baixa um arquivo protegido. Precisa existir porque a API autentica por
   *  header Bearer, não por cookie: um <a href="/api/..."> abriria a URL sem
   *  o token e tomaria 401. Aqui o fetch leva o header e devolve o conteúdo. */
  async blob(p: string): Promise<Blob> {
    const headers = new Headers();
    const t = token.get();
    if (t) headers.set("Authorization", `Bearer ${t}`);
    const res = await fetch(`${BASE}${p}`, { headers });
    if (res.status === 401) {
      token.clear();
      window.location.assign("/entrar");
      throw new ApiError(401, "Sessão expirada.");
    }
    if (!res.ok) {
      const detail = await res.json().catch(() => null);
      throw new ApiError(res.status, detail?.detail ?? "Não foi possível abrir o arquivo.");
    }
    return res.blob();
  },

  /** Igual ao `blob`, mas com corpo JSON. Existe porque a exportação em modo
   *  apresentação recebe a anotação do médico no corpo da requisição: ela pode
   *  ter algumas linhas, o que não cabe bem em query string, e não deve ficar
   *  registrada no log de acesso do servidor como uma URL ficaria. */
  async blobPost(p: string, corpo: unknown): Promise<Blob> {
    const headers = new Headers({ "Content-Type": "application/json" });
    const t = token.get();
    if (t) headers.set("Authorization", `Bearer ${t}`);
    const res = await fetch(`${BASE}${p}`, {
      method: "POST",
      headers,
      body: JSON.stringify(corpo),
    });
    if (res.status === 401) {
      token.clear();
      window.location.assign("/entrar");
      throw new ApiError(401, "Sessão expirada.");
    }
    if (!res.ok) {
      const detail = await res.json().catch(() => null);
      throw new ApiError(res.status, detail?.detail ?? "Não foi possível gerar o arquivo.");
    }
    return res.blob();
  },

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
  rqe: string | null;
  photo_url: string | null;
  specialty: string | null;
  council: string | null;
  profession: string | null;
  council_name: string | null;
  council_number: string | null;
  council_state: string | null;
  cpf_mascarado: string | null;
  birth_date: string | null;
  created_at: string;
};
