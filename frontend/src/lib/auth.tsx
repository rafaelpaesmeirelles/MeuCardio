import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, type Usuario } from "./api";

const BASE = import.meta.env.VITE_API_URL ?? "/api";
const INVESTOR_TOUR_SESSION_KEY = "corvia:cardiology-spaces:investor-tour-session:v1";

type Estado = {
  usuario: Usuario | null;
  carregando: boolean;
  entrar: (email: string, senha: string, permanecerConectado?: boolean) => Promise<void>;
  sair: () => Promise<void>;
  recarregar: () => Promise<void>;
};

const Ctx = createContext<Estado | null>(null);

async function mensagemLogin(res: Response): Promise<string> {
  const body = await res.json().catch(() => null);
  const detail = body?.detail;
  const detailText = typeof detail === "string" && detail.trim() ? detail.trim() : "";
  if (res.status === 401 || res.status === 403) {
    return detailText || "E-mail ou senha incorretos.";
  }
  if (res.status === 429) {
    return "Muitas tentativas de acesso. Aguarde alguns instantes e tente novamente.";
  }
  if (res.status >= 500) {
    return "O acesso ao CorVIA está temporariamente indisponível. Tente novamente em instantes.";
  }
  return detailText || "Não foi possível concluir o acesso. Revise os dados e tente novamente.";
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    let ativo = true;
    void (async () => {
      try {
        const status = await api.get<{ authenticated: boolean }>("/auth/session-status");
        const perfil = status.authenticated
          ? await api.get<Usuario>("/auth/me", { silencioso401: true })
          : null;
        if (ativo) setUsuario(perfil);
      } catch {
        if (ativo) setUsuario(null);
      } finally {
        if (ativo) setCarregando(false);
      }
    })();
    return () => { ativo = false; };
  }, []);

  async function entrar(email: string, senha: string, permanecerConectado = true) {
    const form = new URLSearchParams({
      username: email,
      password: senha,
      permanecer_conectado: String(permanecerConectado),
    });
    let res: Response;
    try {
      res = await fetch(`${BASE}/auth/sessao`, {
        method: "POST",
        credentials: "include",
        cache: "no-store",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: form,
      });
    } catch {
      throw new Error("Não foi possível conectar ao CorVIA. Verifique sua conexão e tente novamente.");
    }
    if (!res.ok) throw new Error(await mensagemLogin(res));

    // Não recarregue o documento depois do login. Em Safari/Chrome no iOS, uma
    // navegação completa pode ser atendida pelo shell antigo do service worker
    // enquanto os chunks correspondentes já não existem mais, deixando a tela
    // branca. A sessão já foi gravada em cookie HttpOnly; ler o perfil e
    // atualizar o contexto é suficiente para o App encaminhar o primeiro
    // acesso a /minha-conta, KYC ou tour.
    const perfil = await api.get<Usuario>("/auth/me");
    // O perfil Investidor deve receber o tour a cada novo login. O marcador é
    // mantido apenas durante a sessão atual para impedir loop entre páginas.
    if (perfil.investidor) window.sessionStorage.removeItem(INVESTOR_TOUR_SESSION_KEY);
    setUsuario(perfil);
  }

  async function sair() {
    try {
      await api.logout();
    } finally {
      // Do not leave the previous user's clinical UI open after a network error.
      setUsuario(null);
      window.sessionStorage.removeItem(INVESTOR_TOUR_SESSION_KEY);
    }
  }

  async function recarregar() {
    try {
      setUsuario(await api.get<Usuario>("/auth/me"));
    } catch {
      setUsuario(null);
    }
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
