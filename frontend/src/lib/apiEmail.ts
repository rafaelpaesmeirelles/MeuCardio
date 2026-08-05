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
  // FormData fica de fora: o browser precisa gerar o boundary do multipart
  // sozinho (mesma regra de lib/api.ts) — usado no upload de anexo.
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
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
  put: <T>(p: string, body?: unknown) =>
    request<T>(p, { method: "PUT", body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(p: string) => request<T>(p, { method: "DELETE" }),

  /** Upload de anexo, em duas etapas — o Mail360 exige subir o arquivo
   *  primeiro e só depois referenciar o `file_id` no envio da mensagem. */
  uploadAnexo: (arquivo: File) => {
    const form = new FormData();
    form.append("arquivo", arquivo);
    return request<{ file_id: string; nome: string }>("/email/mensagens/anexos", {
      method: "POST", body: form,
    });
  },

  async baixarAnexo(messageId: string, attachmentId: string, nome: string) {
    const headers = new Headers();
    const token = tokenEmail.get();
    if (token) headers.set("Authorization", `Bearer ${token}`);
    const caminho = `/email/mensagens/${encodeURIComponent(messageId)}/anexos/${encodeURIComponent(attachmentId)}?nome=${encodeURIComponent(nome)}`;
    const res = await fetch(`${BASE}${caminho}`, { headers });
    if (res.status === 401) {
      tokenEmail.clear();
      throw new ApiEmailError(401, "Sessão da caixa de e-mail expirada.");
    }
    if (!res.ok) {
      const detail = await res.json().catch(() => null);
      throw new ApiEmailError(res.status, detail?.detail ?? "Não foi possível baixar o anexo.");
    }
    const url = URL.createObjectURL(await res.blob());
    const link = document.createElement("a");
    link.href = url;
    link.download = nome || "anexo";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  },

  /** Fora de `request()` de propósito: login nunca tem token prévio pra
   *  expirar, então um 401 aqui é sempre "endereço ou senha incorretos" (ou,
   *  no caso mais comum de quem nunca ativou a caixa, "conta inexistente")
   *  — nunca "sessão expirada". Roteado pelo `request()` genérico, a
   *  mensagem real do backend (`detail`) era descartada e trocada por
   *  "Sessão da caixa de e-mail expirada", que confunde quem está entrando
   *  pela primeira vez tanto quanto quem de fato só errou a senha. */
  async entrar(endereco: string, senha: string) {
    const res = await fetch(`${BASE}/email/entrar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ endereco, senha }),
    });
    if (!res.ok) {
      const detail = await res.json().catch(() => null);
      throw new ApiEmailError(res.status, detail?.detail ?? "Não foi possível entrar.");
    }
    const dados = (await res.json()) as { access_token: string };
    tokenEmail.set(dados.access_token);
    return dados;
  },
};
