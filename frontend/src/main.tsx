import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { AuthProvider } from "./lib/auth";
import { liberarRecargaPendente, verificarVersaoAtual } from "./lib/freshness";
import "./styles/tokens.css";
import "./styles/shell.css";
import "./styles/clinical-command-center.css";
import "./styles/clinical-command-launch-polish.css";
import "./styles/clinical-command-accessibility.css";
import "./styles/produto.css";
import "./styles/tour.css";

const ASSISTANT_ENTRY_MODE_KEY = "corvia:assistant-entry-mode:v1";
const ASSISTANT_ENTRY_QUESTION_KEY = "corvia:assistant-entry-question:v1";
const ASSISTANT_ENTRY_AT_KEY = "corvia:assistant-entry-at:v1";

let swRecargaPendente = false;
function tentarRecarregarPorNovoSW() {
  const ultimaRecargaEm = Number(sessionStorage.getItem("sw-recarregado-em") || "0");
  if (Date.now() - ultimaRecargaEm < 5000) return;
  if ((window as unknown as { __streamAtivo?: boolean }).__streamAtivo) {
    swRecargaPendente = true;
    return;
  }
  sessionStorage.setItem("sw-recarregado-em", String(Date.now()));
  window.location.reload();
}

async function verificarAtualizacaoCompleta(forcar = false) {
  await verificarVersaoAtual(forcar);
  if (!("serviceWorker" in navigator)) return;
  navigator.serviceWorker.getRegistration().then((registro) => registro?.update()).catch(() => undefined);
}

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.addEventListener("controllerchange", tentarRecarregarPorNovoSW);
}

(window as unknown as { __streamEncerrado: () => void }).__streamEncerrado = () => {
  liberarRecargaPendente();
  if (swRecargaPendente) {
    swRecargaPendente = false;
    tentarRecarregarPorNovoSW();
  }
};

void verificarAtualizacaoCompleta(true);
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") void verificarAtualizacaoCompleta(true);
});
window.addEventListener("pageshow", () => void verificarAtualizacaoCompleta(true));

// Qualquer interação relevante também consulta a versão, limitada internamente
// a uma chamada a cada 5 segundos. Assim uma aba aberta por horas percebe um
// deploy mesmo sem mudança de rota, sem transformar cada clique em tráfego.
document.addEventListener("click", () => void verificarAtualizacaoCompleta(false), { capture: true });
document.addEventListener("keydown", () => void verificarAtualizacaoCompleta(false), { capture: true });

/**
 * A Home possui duas entradas que devem manter intenção ao abrir o Assistente:
 * 1) o CTA explícito do rail de Assistente Pessoal; 2) uma pergunta digitada
 * na Clinical Command Bar que o classificador encaminha ao Assistente Clínica.
 * O hint dura poucos segundos e fica em sessionStorage, então não atravessa
 * navegador/sessão e não é confundido com histórico permanente.
 */
document.addEventListener("click", (evento) => {
  const alvo = evento.target instanceof Element ? evento.target : null;
  if (!alvo?.closest(".rail-primary--assistant")) return;
  try {
    sessionStorage.setItem(ASSISTANT_ENTRY_MODE_KEY, "pessoal");
    sessionStorage.removeItem(ASSISTANT_ENTRY_QUESTION_KEY);
    sessionStorage.setItem(ASSISTANT_ENTRY_AT_KEY, String(Date.now()));
  } catch {
    // Hint de navegação é opcional; a tela do Assistente continua utilizável.
  }
}, { capture: true });

document.addEventListener("submit", (evento) => {
  const formulario = evento.target instanceof HTMLFormElement ? evento.target : null;
  if (!formulario?.classList.contains("clinical-command")) return;
  const entrada = formulario.querySelector<HTMLInputElement>('input[aria-label="Comando clínico universal"]');
  const pergunta = entrada?.value.trim();
  if (!pergunta) return;

  // Mantém exatamente a mesma fronteira semântica usada pelo classificador da
  // Home. Ações e pesquisas comuns não deixam um hint que possa contaminar uma
  // visita subsequente ao Assistente.
  const normal = pergunta.toLocaleLowerCase("pt-BR").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  const parecePergunta = /^(qual|como|quando|por que|porque|compare|resuma|explique|analise|revisar?)\b/.test(normal)
    || pergunta.includes("?");
  if (!parecePergunta) return;

  try {
    sessionStorage.setItem(ASSISTANT_ENTRY_QUESTION_KEY, pergunta);
    sessionStorage.setItem(ASSISTANT_ENTRY_MODE_KEY, "clinica");
    sessionStorage.setItem(ASSISTANT_ENTRY_AT_KEY, String(Date.now()));
  } catch {
    // O Command Center não depende de storage para navegar.
  }
}, { capture: true });

/** A action sheet móvel se comporta como diálogo de verdade também no teclado. */
document.addEventListener("click", (evento) => {
  const alvo = evento.target instanceof Element ? evento.target : null;
  if (alvo?.closest(".barra-mobile__acao")) {
    requestAnimationFrame(() => {
      document.querySelector<HTMLElement>(".acoes-mobile header button")?.focus();
    });
    return;
  }

  if (alvo?.closest(".acoes-mobile__fundo") || alvo?.closest(".acoes-mobile > header > button")) {
    requestAnimationFrame(() => {
      document.querySelector<HTMLElement>(".barra-mobile__acao")?.focus();
    });
  }
}, { capture: true });

document.addEventListener("keydown", (evento) => {
  if (evento.key !== "Tab") return;
  const dialogo = document.querySelector<HTMLElement>(".acoes-mobile");
  if (!dialogo) return;
  const focaveis = Array.from(dialogo.querySelectorAll<HTMLElement>('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'))
    .filter((elemento) => elemento.offsetParent !== null);
  if (!focaveis.length) return;
  const primeiro = focaveis[0];
  const ultimo = focaveis[focaveis.length - 1];
  if (evento.shiftKey && document.activeElement === primeiro) {
    evento.preventDefault();
    ultimo.focus();
  } else if (!evento.shiftKey && document.activeElement === ultimo) {
    evento.preventDefault();
    primeiro.focus();
  }
}, { capture: true });

(window as unknown as { __corviaVerificarAtualizacao?: () => void }).__corviaVerificarAtualizacao = () => {
  void verificarAtualizacaoCompleta(true);
};

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
