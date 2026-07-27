import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, token, type Usuario } from "./api";

type Estado = {
  usuario: Usuario | null;
  carregando: boolean;
  entrar: (email: string, senha: string) => Promise<void>;
  sair: () => void;
  recarregar: () => void;
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

  // Usada depois de editar o perfil em /minha-conta, pra que o nome no
  // cabeçalho reflita a alteração sem exigir novo login.
  function recarregar() {
    if (!token.get()) return;
    api.get<Usuario>("/auth/me").then(setUsuario).catch(() => {});
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
