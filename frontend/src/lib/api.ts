const BASE = import.meta.env.VITE_API_URL ?? "/api";
const LEGACY_TOKEN_KEY = "meucardio.token";

function removerTokenLegado() {
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(LEGACY_TOKEN_KEY);
  }
}
removerTokenLegado();

export const token = {
  get: () => "cookie-session",
  set: (_valor?: string) => removerTokenLegado(),
  clear: () => removerTokenLegado(),
};

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

type DetalheEstruturado = {
  erro?: unknown;
  campos?: unknown;
  bloqueios?: unknown;
  itens?: unknown;
};

function textoPermitido(valor: unknown): string | null {
  if (typeof valor !== "string") return null;
  const texto = valor.trim();
  return texto || null;
}

function mensagensDeLista(valor: unknown): string[] {
  if (!Array.isArray(valor)) return [];
  return valor.flatMap((entrada) => {
    const direta = textoPermitido(entrada);
    if (direta) return [direta];
    if (!entrada || typeof entrada !== "object") return [];
    const objeto = entrada as Record<string, unknown>;
    const mensagem =
      textoPermitido(objeto.erro) ??
      textoPermitido(objeto.mensagem) ??
      textoPermitido(objeto.motivo);
    const campo = textoPermitido(objeto.campo);
    const indice = typeof objeto.indice === "number" ? `Item ${objeto.indice}` : null;
    if (mensagem && (campo || indice)) return [`${campo ?? indice}: ${mensagem}`];
    return mensagem ? [mensagem] : campo ? [`Verifique: ${campo}`] : [];
  });
}

function mensagemEstruturada(detail: DetalheEstruturado, fallback: string): string {
  const partes: string[] = [];
  const erro = textoPermitido(detail.erro);
  if (erro) partes.push(erro);
  const campos = mensagensDeLista(detail.campos);
  if (campos.length) partes.push(`Campos pendentes: ${campos.join(", ")}.`);
  partes.push(...mensagensDeLista(detail.bloqueios));
  partes.push(...mensagensDeLista(detail.itens));
  const unicas = [...new Set(partes.map((parte) => parte.trim()).filter(Boolean))];
  return unicas.length ? unicas.join(" ") : fallback;
}

async function erroDaResposta(res: Response, fallback: string): Promise<ApiError> {
  const payload = await res.json().catch(() => null);
  const detail = payload?.detail;
  let message = fallback;
  if (typeof detail === "string" && detail.trim()) {
    message = detail.trim();
  } else if (detail && typeof detail === "object") {
    message = mensagemEstruturada(detail as DetalheEstruturado, fallback);
  }
  return new ApiError(res.status, message);
}

function redirecionarSessaoExpirada() {
  removerTokenLegado();
  if (!window.location.pathname.startsWith("/entrar")) {
    window.location.assign("/entrar");
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });
  if (res.status === 401) {
    redirecionarSessaoExpirada();
    throw new ApiError(401, "Sessão expirada.");
  }
  if (res.status === 402) {
    if (!window.location.pathname.startsWith("/assinatura")) {
      window.location.assign("/assinatura?status=necessaria");
    }
    throw new ApiError(402, "Assinatura necessária.");
  }
  if (!res.ok) throw await erroDaResposta(res, "Não foi possível concluir a solicitação.");
  return res.status === 204 ? (undefined as T) : res.json();
}

export const api = {
  get: <T>(p: string) => request<T>(p),
  post: <T>(p: string, body?: unknown) =>
    request<T>(p, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) }),
  patch: <T>(p: string, body: unknown) =>
    request<T>(p, { method: "PATCH", body: JSON.stringify(body) }),
  put: <T>(p: string, body: unknown) =>
    request<T>(p, { method: "PUT", body: JSON.stringify(body) }),
  delete: <T>(p: string, body?: unknown) =>
    request<T>(p, { method: "DELETE", body: body === undefined ? undefined : JSON.stringify(body) }),

  upload: <T>(p: string, campo: string, arquivo: File) => {
    const form = new FormData();
    form.append(campo, arquivo);
    return request<T>(p, { method: "POST", body: form });
  },

  async blob(p: string, init: RequestInit = {}): Promise<Blob> {
    const headers = new Headers(init.headers);
    if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
    const res = await fetch(`${BASE}${p}`, {
      ...init,
      headers,
      credentials: "include",
    });
    if (res.status === 401) {
      redirecionarSessaoExpirada();
      throw new ApiError(401, "Sessão expirada.");
    }
    if (!res.ok) throw await erroDaResposta(res, "Não foi possível abrir o arquivo.");
    return res.blob();
  },

  async blobPost(p: string, corpo: unknown): Promise<Blob> {
    const res = await fetch(`${BASE}${p}`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(corpo),
    });
    if (res.status === 401) {
      redirecionarSessaoExpirada();
      throw new ApiError(401, "Sessão expirada.");
    }
    if (!res.ok) throw await erroDaResposta(res, "Não foi possível gerar o arquivo.");
    return res.blob();
  },

  async stream(p: string, body: unknown, aoReceberEvento: (evento: any) => void): Promise<void> {
    const res = await fetch(`${BASE}${p}`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (res.status === 401) {
      redirecionarSessaoExpirada();
      throw new ApiError(401, "Sessão expirada.");
    }
    if (!res.ok || !res.body) {
      throw await erroDaResposta(res, "Não foi possível consultar o assistente.");
    }

    const processarEvento = (parte: string) => {
      const linha = parte.split("\n").find((l) => l.startsWith("data: "));
      if (!linha) return;
      aoReceberEvento(JSON.parse(linha.slice(6)));
    };

    const leitor = res.body.getReader();
    const decodificador = new TextDecoder();
    let restante = "";
    while (true) {
      const { done, value } = await leitor.read();
      if (done) break;
      restante += decodificador.decode(value, { stream: true });
      const partes = restante.split("\n\n");
      restante = partes.pop() ?? "";
      partes.forEach(processarEvento);
    }
    if (restante.trim()) processarEvento(restante);
  },

  async login(email: string, password: string) {
    const form = new URLSearchParams({ username: email, password });
    const res = await fetch(`${BASE}/auth/sessao`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });
    if (!res.ok) throw await erroDaResposta(res, "E-mail ou senha incorretos.");
    removerTokenLegado();
    return res.json() as Promise<{ authenticated: boolean }>;
  },

  async logout() {
    try {
      await fetch(`${BASE}/auth/sair`, {
        method: "POST",
        credentials: "include",
      });
    } finally {
      removerTokenLegado();
    }
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
  home_street: string | null;
  home_number: string | null;
  home_complement: string | null;
  home_neighborhood: string | null;
  home_city: string | null;
  home_state: string | null;
  home_zip: string | null;
  practice_street: string | null;
  practice_number: string | null;
  practice_complement: string | null;
  practice_neighborhood: string | null;
  practice_city: string | null;
  practice_state: string | null;
  practice_zip: string | null;
  practice_phone: string | null;
  document_logo_url: string | null;
  document_logo_dark_background: boolean;
  professional_title: string | null;
  workplace_name: string | null;
  workplace_department: string | null;
  workplace_role: string | null;
  workplace_notes: string | null;
  include_workplace_on_documents: boolean;
  profile_completion_required: boolean;
  boas_vindas_pendente: boolean;
  assinatura_metodo_preferido: string | null;
};
