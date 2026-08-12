import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, type Usuario } from "./api";

const BASE = import.meta.env.VITE_API_URL ?? "/api";
const COMMAND_HISTORY_KEY = "corvia:command-history:v1";
const COMMAND_HISTORY_OWNER_KEY = "corvia:command-history-owner:v1";
const COMMAND_HISTORY_SESSION_KEY = "corvia:command-history-session:v1";
const ASSISTANT_ENTRY_KEYS = [
  "corvia:assistant-entry-mode:v1",
  "corvia:assistant-entry-question:v1",
  "corvia:assistant-entry-at:v1",
] as const;

type Estado = {
  usuario: Usuario | null;
  carregando: boolean;
  entrar: (email: string, senha: string, permanecerConectado?: boolean) => Promise<void>;
  sair: () => Promise<void>;
  recarregar: () => void;
};

const Ctx = createContext<Estado | null>(null);

async function mensagemLogin(res: Response): Promise<string> {
  const body = await res.json().catch(() => null);
  const detail = body?.detail;
  return typeof detail === "string" && detail.trim() ? detail : "E-mail ou senha incorretos.";
}

/**
 * A Home usa um pequeno histórico local para “continuar de onde parei”. Como
 * o médico pode digitar contexto clínico, ele recebe duas barreiras extras:
 *
 * 1. nunca atravessa troca de conta no mesmo navegador;
 * 2. nunca atravessa uma nova sessão do navegador. O payload continua em
 *    localStorage apenas para sobreviver a reload/PWA refresh dentro da mesma
 *    sessão; um marcador em sessionStorage o invalida quando a sessão termina.
 *
 * O owner contém somente o id interno do usuário, nunca nome/e-mail/paciente.
 */
function vincularContextoLocal(usuario: Usuario) {
  try {
    const novoOwner = String(usuario.id);
    const ownerAtual = window.localStorage.getItem(COMMAND_HISTORY_OWNER_KEY);
    const sessaoAtual = window.sessionStorage.getItem(COMMAND_HISTORY_SESSION_KEY);
    const mudouConta = ownerAtual !== novoOwner;
    const novaSessaoDoBrowser = sessaoAtual !== novoOwner;

    if (mudouConta || novaSessaoDoBrowser) {
      window.localStorage.removeItem(COMMAND_HISTORY_KEY);
      ASSISTANT_ENTRY_KEYS.forEach((chave) => window.sessionStorage.removeItem(chave));
    }

    window.localStorage.setItem(COMMAND_HISTORY_OWNER_KEY, novoOwner);
    window.sessionStorage.setItem(COMMAND_HISTORY_SESSION_KEY, novoOwner);
  } catch {
    // Armazenamento local é opcional; a autenticação nunca depende dele.
  }
}

function limparContextoLocal() {
  try {
    window.localStorage.removeItem(COMMAND_HISTORY_KEY);
    window.localStorage.removeItem(COMMAND_HISTORY_OWNER_KEY);
    window.sessionStorage.removeItem(COMMAND_HISTORY_SESSION_KEY);
    ASSISTANT_ENTRY_KEYS.forEach((chave) => window.sessionStorage.removeItem(chave));
  } catch {
    // Nada a fazer quando o browser bloqueia storage.
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    api
      .get<Usuario>("/auth/me", { silencioso401: true })
      .then((autenticado) => {
        vincularContextoLocal(autenticado);
        setUsuario(autenticado);
      })
      .catch(() => {
        limparContextoLocal();
        setUsuario(null);
      })
      .finally(() => setCarregando(false));
  }, []);

  async function entrar(email: string, senha: string, permanecerConectado = true) {
    const form = new URLSearchParams({
      username: email,
      password: senha,
      permanecer_conectado: String(permanecerConectado),
    });
    const res = await fetch(`${BASE}/auth/sessao`, {
      method: "POST",
      credentials: "include",
      cache: "no-store",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });
    if (!res.ok) throw new Error(await mensagemLogin(res));

    // Login é um ponto seguro para uma recarga completa. O parâmetro único
    // evita reaproveitamento do documento HTML por caches intermediários; o
    // Caddy e o service worker também revalidam o shell. O AuthProvider da
    // nova página vincula/limpa o contexto local antes de expor a sessão.
    window.location.replace(`/?login=${Date.now()}`);
  }

  async function sair() {
    try {
      await api.logout();
    } finally {
      limparContextoLocal();
      setUsuario(null);
    }
  }

  function recarregar() {
    api.get<Usuario>("/auth/me")
      .then((autenticado) => {
        vincularContextoLocal(autenticado);
        setUsuario(autenticado);
      })
      .catch(() => {
        limparContextoLocal();
        setUsuario(null);
      });
  }

  return (
    <Ctx.Provider value={{ usuario, carregando, entrar, sair, recarregar }}>{children}</Ctx.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAuth precisa estar dentro de AuthProvider");
  return ctx;
}
