import { useEffect } from "react";

const ASSISTANT_ENTRY_MODE_KEY = "corvia:assistant-entry-mode:v1";
const ASSISTANT_ENTRY_QUESTION_KEY = "corvia:assistant-entry-question:v1";
const ASSISTANT_ENTRY_AT_KEY = "corvia:assistant-entry-at:v1";

function guardarEntradaAssistente(modo: "clinica" | "pessoal", pergunta?: string) {
  try {
    sessionStorage.setItem(ASSISTANT_ENTRY_MODE_KEY, modo);
    if (pergunta) sessionStorage.setItem(ASSISTANT_ENTRY_QUESTION_KEY, pergunta);
    else sessionStorage.removeItem(ASSISTANT_ENTRY_QUESTION_KEY);
    sessionStorage.setItem(ASSISTANT_ENTRY_AT_KEY, String(Date.now()));
  } catch {
    // O bridge só melhora a continuidade da navegação; nunca bloqueia a UI.
  }
}

/**
 * Ponte fina entre o App Shell e o Clinical Command Center.
 *
 * Mantém fora do `main.tsx` os comportamentos exclusivos da nova experiência:
 * - ⌘/Ctrl+K e `/` focam a Command Bar quando a Home está ativa;
 * - pergunta da Command Bar chega pré-preenchida ao Assistente Clínica;
 * - CTA do rail abre diretamente o Assistente Pessoal;
 * - action sheet móvel recebe foco e o mantém enquanto estiver aberto.
 *
 * Não chama API, não muda autenticação e não cria estado clínico compartilhado.
 */
export default function CommandCenterBridge() {
  useEffect(() => {
    function aoAtalho(evento: KeyboardEvent) {
      if (!document.body.classList.contains("command-center-active")) return;
      const alvo = evento.target instanceof HTMLElement ? evento.target : null;
      const editando = !!alvo?.closest('input, textarea, select, [contenteditable="true"]');
      const commandK = (evento.metaKey || evento.ctrlKey) && evento.key.toLowerCase() === "k";
      const slash = evento.key === "/" && !evento.metaKey && !evento.ctrlKey && !evento.altKey && !editando;
      if (!commandK && !slash) return;

      evento.preventDefault();
      evento.stopImmediatePropagation();
      document.querySelector<HTMLInputElement>('input[aria-label="Comando clínico universal"]')?.focus();
    }

    function aoCliqueAssistente(evento: MouseEvent) {
      const alvo = evento.target instanceof Element ? evento.target : null;
      if (alvo?.closest(".rail-primary--assistant")) {
        guardarEntradaAssistente("pessoal");
      }
    }

    function aoEnviarComando(evento: SubmitEvent) {
      const formulario = evento.target instanceof HTMLFormElement ? evento.target : null;
      if (!formulario?.classList.contains("clinical-command")) return;
      const entrada = formulario.querySelector<HTMLInputElement>('input[aria-label="Comando clínico universal"]');
      const pergunta = entrada?.value.trim();
      if (!pergunta) return;

      // Mesma fronteira semântica do classificador em ClinicalCommandCenter:
      // ação/pesquisa não deixa hint; somente pergunta encaminhada à IA.
      const normal = pergunta.toLocaleLowerCase("pt-BR").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      const parecePergunta = /^(qual|como|quando|por que|porque|compare|resuma|explique|analise|revisar?)\b/.test(normal)
        || pergunta.includes("?");
      if (parecePergunta) guardarEntradaAssistente("clinica", pergunta);
    }

    function aoCliqueAcoes(evento: MouseEvent) {
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
    }

    function prenderFocoAcoes(evento: KeyboardEvent) {
      if (evento.key !== "Tab") return;
      const dialogo = document.querySelector<HTMLElement>(".acoes-mobile");
      if (!dialogo) return;
      const focaveis = Array.from(
        dialogo.querySelectorAll<HTMLElement>('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'),
      ).filter((elemento) => elemento.offsetParent !== null);
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
    }

    document.addEventListener("keydown", aoAtalho, { capture: true });
    document.addEventListener("click", aoCliqueAssistente, { capture: true });
    document.addEventListener("submit", aoEnviarComando, { capture: true });
    document.addEventListener("click", aoCliqueAcoes, { capture: true });
    document.addEventListener("keydown", prenderFocoAcoes, { capture: true });

    return () => {
      document.removeEventListener("keydown", aoAtalho, { capture: true });
      document.removeEventListener("click", aoCliqueAssistente, { capture: true });
      document.removeEventListener("submit", aoEnviarComando, { capture: true });
      document.removeEventListener("click", aoCliqueAcoes, { capture: true });
      document.removeEventListener("keydown", prenderFocoAcoes, { capture: true });
    };
  }, []);

  return null;
}
