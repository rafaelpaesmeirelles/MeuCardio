import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, type Usuario } from "./api";

const BASE = import.meta.env.VITE_API_URL ?? "/api";

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
  return typeof detail === "string" && detail.trim() ? detail : "E-mail ou senha incorretos.";
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    api
      .get<Usuario>("/auth/me", { silencioso401: true })
      .then(setUsuario)
      .catch(() => setUsuario(null))
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

    // Não recarregue o documento depois do login. Em Safari/Chrome no iOS, uma
    // navegação completa pode ser atendida pelo shell antigo do service worker
    // enquanto os chunks correspondentes já não existem mais, deixando a tela
    // branca. A sessão já foi gravada em cookie HttpOnly; ler o perfil e
    // atualizar o contexto é suficiente para o App encaminhar o primeiro
    // acesso a /minha-conta, KYC ou tour.
    const perfil = await api.get<Usuario>("/auth/me");
    setUsuario(perfil);
  }

  async function sair() {
    await api.logout();
    setUsuario(null);
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
