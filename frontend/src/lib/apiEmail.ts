/** Cliente de API da "sessão email" (CorvIA Mail) — token PRÓPRIO, distinto
 * do token da conta Corvia em `lib/api.ts`. */
const BASE = import.meta.env.VITE_API_URL ?? "/api";
const TOKEN_KEY = "corviamail.token";
const RENEW_KEY = "corviamail.token.renewed_at";
const RENEW_INTERVAL_MS = 24 * 60 * 60 * 1000;
let renovando = false;

function storageDisponivel(): boolean {
  return typeof window !== "undefined";
}

export const tokenEmail = {
  get: () => {
    if (!storageDisponivel()) return null;
    return sessionStorage.getItem(TOKEN_KEY) ?? localStorage.getItem(TOKEN_KEY);
  },
  persistente: () => storageDisponivel() && Boolean(localStorage.getItem(TOKEN_KEY)),
  set: (v: string, persistir = true) => {
    if (!storageDisponivel()) return;
    localStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(TOKEN_KEY);
    (persistir ? localStorage : sessionStorage).setItem(TOKEN_KEY, v);
    if (persistir) localStorage.setItem(RENEW_KEY, String(Date.now()));
    else localStorage.removeItem(RENEW_KEY);
  },
  clear: () => {
    if (!storageDisponivel()) return;
    localStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(RENEW_KEY);
  },
};

export class ApiEmailError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function renovarSessaoPersistenteSeNecessario() {
  if (!tokenEmail.persistente() || renovando) return;
  const ultima = Number(localStorage.getItem(RENEW_KEY) || "0");
  if (Date.now() - ultima < RENEW_INTERVAL_MS) return;
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return;

  renovando = true;
  try {
    const res = await fetch(`${BASE}/email/renovar-sessao`, {
      method: "POST",
      cache: "no-store",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return;
    const dados = await res.json() as { access_token: string };
    tokenEmail.set(dados.access_token, true);
  } catch {
    // Renovação é oportunística; uma falha de rede não derruba a sessão atual.
  } finally {
    renovando = false;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const t = tokenEmail.get();
  if (t) headers.set("Authorization", `Bearer ${t}`);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${BASE}${path}`, { ...init, headers, cache: "no-store" });
  if (res.status === 401) {
    tokenEmail.clear();
    throw new ApiEmailError(401, "Sessão da caixa de e-mail expirada.");
  }
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new ApiEmailError(res.status, detail?.detail ?? "Não foi possível concluir a solicitação.");
  }
  void renovarSessaoPersistenteSeNecessario();
  return res.status === 204 ? (undefined as T) : res.json();
}

export const apiEmail = {
  get: <T>(p: string) => request<T>(p),
  post: <T>(p: string, body?: unknown) =>
    request<T>(p, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
  put: <T>(p: string, body?: unknown) =>
    request<T>(p, { method: "PUT", body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(p: string) => request<T>(p, { method: "DELETE" }),

  uploadAnexo: (arquivo: File) => {
    const form = new FormData();
    form.append("arquivo", arquivo);
    return request<{ file_id: string; nome: string }>("/email/mensagens/anexos", {
      method: "POST", body: form,
    });
  },

  verificarAssinaturaAnexo: (arquivo: File) => {
    const form = new FormData();
    form.append("arquivo", arquivo);
    return request<{
      assinado: boolean; intacta?: boolean; titular?: string; emissor?: string;
      assinado_em?: string | null; texto_comprovacao: string | null;
    }>("/email/mensagens/anexos/verificar-assinatura", { method: "POST", body: form });
  },

  async baixarAnexo(messageId: string, attachmentId: string, nome: string) {
    const headers = new Headers();
    const token = tokenEmail.get();
    if (token) headers.set("Authorization", `Bearer ${token}`);
    const caminho = `/email/mensagens/${encodeURIComponent(messageId)}/anexos/${encodeURIComponent(attachmentId)}?nome=${encodeURIComponent(nome)}`;
    const res = await fetch(`${BASE}${caminho}`, { headers, cache: "no-store" });
    if (res.status === 401) {
      tokenEmail.clear();
      throw new ApiEmailError(401, "Sessão da caixa de e-mail expirada.");
    }
    if (!res.ok) {
      const detail = await res.json().catch(() => null);
      throw new ApiEmailError(res.status, detail?.detail ?? "Não foi possível baixar o anexo.");
    }
    void renovarSessaoPersistenteSeNecessario();
    const url = URL.createObjectURL(await res.blob());
    const link = document.createElement("a");
    link.href = url;
    link.download = nome || "anexo";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  },

  async entrar(endereco: string, senha: string, permanecerConectado = false) {
    const res = await fetch(`${BASE}/email/entrar`, {
      method: "POST",
      cache: "no-store",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ endereco, senha, permanecer_conectado: permanecerConectado }),
    });
    if (!res.ok) {
      const detail = await res.json().catch(() => null);
      throw new ApiEmailError(res.status, detail?.detail ?? "Não foi possível entrar.");
    }
    const dados = (await res.json()) as { access_token: string };
    tokenEmail.set(dados.access_token, permanecerConectado);
    return dados;
  },
};
