import { Component, type ErrorInfo, type ReactNode } from "react";

type Props = { children: ReactNode };
type State = { falhou: boolean };

const CACHE_PREFIXOS = ["corvia-", "workbox-"];

async function recuperarAplicacao() {
  try {
    if ("caches" in window) {
      const nomes = await caches.keys();
      await Promise.all(
        nomes
          .filter((nome) => CACHE_PREFIXOS.some((prefixo) => nome.startsWith(prefixo)))
          .map((nome) => caches.delete(nome)),
      );
    }
    if ("serviceWorker" in navigator) {
      const registro = await navigator.serviceWorker.getRegistration();
      await registro?.update().catch(() => undefined);
    }
  } finally {
    const url = new URL(window.location.origin);
    url.searchParams.set("recuperacao", String(Date.now()));
    window.location.replace(url.toString());
  }
}

export default class AppErrorBoundary extends Component<Props, State> {
  state: State = { falhou: false };

  static getDerivedStateFromError(): State {
    return { falhou: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // Mantém evidência útil no console sem incluir perfil, credenciais ou
    // conteúdo clínico. O fallback abaixo impede que a raiz fique em branco.
    console.error("Falha ao renderizar a aplicação", error.name, info.componentStack);
  }

  render() {
    if (!this.state.falhou) return this.props.children;

    return (
      <main className="app-recovery" role="alert">
        <section className="app-recovery__card">
          <p className="eyebrow">Recuperação segura</p>
          <h1>Não foi possível abrir esta tela.</h1>
          <p>Sua sessão foi preservada. Atualize os arquivos do CorVIA e tente novamente.</p>
          <button type="button" className="botao" onClick={() => void recuperarAplicacao()}>
            Atualizar e continuar
          </button>
        </section>
      </main>
    );
  }
}
