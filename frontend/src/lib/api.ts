import { clearLegacyClinicalCaches } from "./clinicalCache";
const BASE = import.meta.env.VITE_API_URL ?? "/api";
const LEGACY_TOKEN_KEY = "meucardio.token";

function removerTokenLegado() {
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(LEGACY_TOKEN_KEY);
  }
}
removerTokenLegado();

/** Resolve arquivos públicos do backend tanto no site quanto no app nativo.
 * No site, /fotos e /logos são servidos pelo mesmo domínio. Quando VITE_API_URL
 * aponta para uma origem absoluta (Capacitor, homologação ou API separada), a
 * imagem precisa usar essa origem em vez de `capacitor://localhost`. */
export function assetUrl(path: string | null | undefined): string | undefined {
  if (!path) return undefined;
  if (/^(?:https?:|data:|blob:)/i.test(path)) return path;
  if (/^https?:\/\//i.test(BASE)) return new URL(path, BASE).toString();
  return path;
}

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
  message?: unknown;
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
  const erro = textoPermitido(detail.erro) ?? textoPermitido(detail.message);
  if (erro) partes.push(erro);
  const campos = mensagensDeLista(detail.campos);
  if (campos.length) partes.push(`Campos pendentes: ${campos.join(", ")}.`);
  partes.push(...mensagensDeLista(detail.bloqueios));
  partes.push(...mensagensDeLista(detail.itens));
  const unicas = [...new Set(partes.map((parte) => parte.trim()).filter(Boolean))];
  return unicas.length ? unicas.join(" ") : fallback;
}

const CAMPOS_VALIDACAO: Record<string, string> = {
  full_name: "Nome completo", email: "E-mail", role: "Perfil", birth_date: "Data de nascimento",
  cpf: "CPF", profession: "Profissão", council_name: "Conselho", council_number: "Número do conselho",
  council_state: "UF do conselho", council_name_other: "Nome do outro conselho",
  council_state_other: "Estado/região do outro conselho", specialty: "Especialidade", rqe: "RQE",
  professional_title: "Título profissional", workplace_name: "Local de trabalho",
  workplace_department: "Setor / unidade", workplace_role: "Cargo / função",
  workplace_notes: "Observações profissionais", tipo_acesso: "Tipo de acesso",
  home_state: "UF residencial", practice_state: "UF profissional", password: "Senha",
};
const MENSAGENS_VALIDACAO_SEGURAS = new Set([
  "Informe nome completo.", "E-mail inválido.", "UF inválida.",
  "Estado inválido — use a sigla (ex.: SP).", "Forma de tratamento inválida.",
  "Conselho profissional inválido.", "Tipo de acesso inválido.",
  "Perfil inválido para conta gerenciada. Administrador não pode ser definido aqui.",
  'Para conselho "Outro", informe qual é o conselho e o estado/região.',
]);

function mensagemValidacao(detail: unknown[], fallback: string): string {
  const mensagens = detail.flatMap((item) => {
    if (!item || typeof item !== "object") return [];
    const { loc, msg } = item as { loc?: unknown; msg?: unknown };
    if (!Array.isArray(loc) || typeof msg !== "string") return [];
    // Neither arbitrary location keys nor validator messages are safe to echo:
    // custom Pydantic validators may embed input, secrets or patient details.
    const chave = [...loc].reverse().find((campo) => typeof campo === "string" && Object.hasOwn(CAMPOS_VALIDACAO, campo));
    const rotulo = typeof chave === "string" ? CAMPOS_VALIDACAO[chave] : "Campo informado";
    const texto = msg.replace(/^Value error, /, "").trim();
    let explicacao = MENSAGENS_VALIDACAO_SEGURAS.has(texto) ? texto : "Valor inválido. Revise este campo.";
    if (texto === "Field required") explicacao = "Campo obrigatório.";
    const limite = /^String should have at (least|most) (\d{1,6}) characters$/.exec(texto);
    if (limite) explicacao = `Informe ${limite[1] === "least" ? "pelo menos" : "no máximo"} ${limite[2]} caracteres.`;
    return [`${rotulo}: ${explicacao}`];
  });
  return [...new Set(mensagens)].join(" ") || fallback;
}

async function erroDaResposta(res: Response, fallback: string): Promise<ApiError> {
  const payload = await res.json().catch(() => null);
  const detail = payload?.detail;
  let message = fallback;
  if (typeof detail === "string" && detail.trim()) {
    message = detail.trim();
  } else if (Array.isArray(detail)) {
    message = mensagemValidacao(detail, fallback);
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

async function request<T>(
  path: string,
  init: RequestInit = {},
  opcoes: { silencioso401?: boolean } = {},
): Promise<T> {
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
    // `silencioso401` existe para a checagem de sessão do AuthProvider
    // (`GET /auth/me` ao abrir qualquer página) — 401 ali é o resultado
    // NORMAL e esperado pra visitante anônimo em página pública
    // (/solicitar-acesso, /produto, /corvia-mail, /esqueci-senha...), não
    // uma sessão que expirou. Sem este flag, o redirecionamento genérico
    // abaixo disparava por trás de QUALQUER visitante sem cookie, alguns
    // segundos depois da página pública já ter renderizado — jogando o
    // médico de volta para /entrar no meio do cadastro (achado do Rafael,
    // 08/08/2026: "página de cadastro... não adaptada", na real o usuário
    // via a tela certa por um instante e era redirecionado pouco depois).
    if (!opcoes.silencioso401) redirecionarSessaoExpirada();
    throw new ApiError(401, "Sessão expirada.");
  }
  if (res.status === 402) {
    if (!window.location.pathname.startsWith("/tour")) {
      window.location.assign("/tour?origem=assinatura&modo=quick");
    }
    throw new ApiError(402, "Assinatura necessária.");
  }
  if (!res.ok) throw await erroDaResposta(res, "Não foi possível concluir a solicitação.");
  return res.status === 204 ? (undefined as T) : res.json();
}

// Contrato de paginação compartilhado pelas frentes científicas com listagem
// paginada (documentos, evidências, estudos, exames, guia de doenças,
// medicamentos — ver auditoria de 02/09/2026, Parte G/H).
export type PaginaDe<T> = {
  total: number;
  limit: number;
  offset: number;
  next_offset: number | null;
  has_more: boolean;
  items: T[];
};

/**
 * Percorre todas as páginas de um endpoint paginado e devolve a lista
 * completa. Usar apenas onde a tela genuinamente precisa do catálogo inteiro
 * (dropdown/busca client-side) — não para telas com paginação visual própria,
 * que devem consumir uma página por vez.
 */
export async function todasAsPaginas<T>(caminho: string): Promise<T[]> {
  const itens: T[] = [];
  let offset = 0;
  for (;;) {
    const separador = caminho.includes("?") ? "&" : "?";
    const pagina = await api.get<PaginaDe<T>>(`${caminho}${separador}offset=${offset}`);
    itens.push(...pagina.items);
    if (!pagina.has_more || pagina.next_offset == null) break;
    offset = pagina.next_offset;
  }
  return itens;
}

export const READ_TIMEOUT_MS = 15_000;
export type GetOptions = { silencioso401?: boolean; signal?: AbortSignal; timeoutMs?: number };

async function get<T>(path: string, options: GetOptions = {}): Promise<T> {
  // Opt-in only: long-running AI, writes, uploads and streams keep their
  // existing semantics. Aborting a read never grants access or fabricates data.
  if (options.timeoutMs === undefined) return request<T>(path, { signal: options.signal }, options);
  if (!Number.isFinite(options.timeoutMs) || options.timeoutMs <= 0) throw new Error("Prazo de consulta inválido.");
  const controller = new AbortController();
  let timedOut = false;
  const abort = () => controller.abort();
  if (options.signal?.aborted) abort();
  else options.signal?.addEventListener("abort", abort, { once: true });
  const timer = setTimeout(() => { timedOut = true; controller.abort(); }, options.timeoutMs);
  try {
    return await request<T>(path, { signal: controller.signal }, options);
  } catch (error) {
    if (timedOut) throw new ApiError(504, "A consulta demorou mais que o esperado. Tente novamente.");
    throw error;
  } finally {
    clearTimeout(timer);
    options.signal?.removeEventListener("abort", abort);
  }
}

export const api = {
  get,
  post: <T>(p: string, body?: unknown) =>
    request<T>(p, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) }),
  patch: <T>(p: string, body: unknown) =>
    request<T>(p, { method: "PATCH", body: JSON.stringify(body) }),
  put: <T>(p: string, body: unknown) =>
    request<T>(p, { method: "PUT", body: JSON.stringify(body) }),
  delete: <T>(p: string, body?: unknown) =>
    request<T>(p, { method: "DELETE", body: body === undefined ? undefined : JSON.stringify(body) }),

  upload: <T>(p: string, campo: string, arquivo: File, camposExtras?: Record<string, string>) => {
    const form = new FormData();
    form.append(campo, arquivo);
    for (const [chave, valor] of Object.entries(camposExtras ?? {})) form.append(chave, valor);
    return request<T>(p, { method: "POST", body: form });
  },

  // Vários arquivos num só multipart — usado pelo KYC (Trabalho 11/12), que
  // recebe até 6 campos de arquivo numa submissão só. `arquivos` com valor
  // `undefined`/`null` é simplesmente omitido (campo opcional do formulário
  // do backend, ex.: documento pessoal como PDF em vez de par de fotos).
  uploadMultiplo: <T>(p: string, arquivos: Record<string, File | null | undefined>) => {
    const form = new FormData();
    for (const [campo, arquivo] of Object.entries(arquivos)) {
      if (arquivo) form.append(campo, arquivo);
    }
    return request<T>(p, { method: "POST", body: form });
  },

  uploadFormulario: <T>(
    p: string,
    arquivos: Array<{ campo: string; arquivo: File }>,
    campos: Record<string, string>,
  ) => {
    const form = new FormData();
    for (const { campo, arquivo } of arquivos) form.append(campo, arquivo);
    for (const [chave, valor] of Object.entries(campos)) form.append(chave, valor);
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

  async stream(
    p: string,
    body: unknown,
    aoReceberEvento: (evento: any) => void,
    signal?: AbortSignal,
  ): Promise<void> {
    const res = await fetch(`${BASE}${p}`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal,
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
      try {
        await clearLegacyClinicalCaches();
      } catch {
        // Local logout must still complete when Cache Storage is unavailable.
        console.warn("Não foi possível limpar o cache clínico legado.");
      }
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
  council_name_other: string | null;
  council_state_other: string | null;
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
  profile_completion_missing_fields?: string[];
  boas_vindas_pendente: boolean;
  assinatura_metodo_preferido: string | null;
  kyc_required: boolean;
  onboarding_pendente: boolean;
  // Issue #52 — só para contexto de UX (rótulo, mensagem do tour, banner de
  // modo demonstração no CorvIA Mail). Nunca usar como gate de acesso no
  // frontend: a decisão real é sempre do backend.
  convidado: boolean;
  investidor: boolean;
  socio: boolean;
  product_access: boolean;
};
