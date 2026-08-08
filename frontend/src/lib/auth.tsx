import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, type Usuario } from "./api";

type Estado = {
  usuario: Usuario | null;
  carregando: boolean;
  entrar: (email: string, senha: string) => Promise<void>;
  sair: () => Promise<void>;
  recarregar: () => void;
};

const Ctx = createContext<Estado | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    // O cookie é HttpOnly: o cliente não tenta "ver" se existe. A fonte da
    // verdade é sempre /auth/me, que responde 200 ou 401. `silencioso401`
    // é essencial aqui: esta chamada roda ao abrir QUALQUER página, inclusive
    // as públicas (/solicitar-acesso, /produto, /corvia-mail...), e 401 é o
    // resultado normal para visitante anônimo — não uma sessão expirada que
    // deva expulsar o usuário de volta para /entrar.
    api
      .get<Usuario>("/auth/me", { silencioso401: true })
      .then(setUsuario)
      .catch(() => setUsuario(null))
      .finally(() => setCarregando(false));
  }, []);

  async function entrar(email: string, senha: string) {
    await api.login(email, senha);
    // Navegação completa (não `setUsuario` + troca de rota via React
    // Router) — pedido do Rafael, 07/08/2026: todo novo login precisa
    // garantir bundle e conteúdo atuais, e a forma mais simples e sem
    // custo de UX de garantir isso é uma recarga real de página logo
    // aqui, num momento em que o usuário já espera uma transição de tela.
    // O cookie de sessão (HttpOnly) já foi gravado por `api.login()`, então
    // a próxima carga de `/` autentica normalmente via `/auth/me` no
    // `AuthProvider` acima.
    window.location.href = "/";
  }

  async function sair() {
    await api.logout();
    setUsuario(null);
  }

  // Usada depois de editar o perfil em /minha-conta, pra que o nome no
  // cabeçalho reflita a alteração sem exigir novo login.
  function recarregar() {
    api.get<Usuario>("/auth/me").then(setUsuario).catch(() => setUsuario(null));
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
