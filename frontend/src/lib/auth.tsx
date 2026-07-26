import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, token, type Usuario } from "./api";

type Estado = {
  usuario: Usuario | null;
  carregando: boolean;
  entrar: (email: string, senha: string) => Promise<void>;
  sair: () => void;
};

const Ctx = createContext<Estado | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    if (!token.get()) {
      setCarregando(false);
      return;
    }
    api
      .get<Usuario>("/auth/me")
      .then(setUsuario)
      .catch(() => token.clear())
      .finally(() => setCarregando(false));
  }, []);

  async function entrar(email: string, senha: string) {
    await api.login(email, senha);
    setUsuario(await api.get<Usuario>("/auth/me"));
  }

  function sair() {
    token.clear();
    setUsuario(null);
  }

  return <Ctx.Provider value={{ usuario, carregando, entrar, sair }}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAuth precisa estar dentro de AuthProvider");
  return ctx;
}
