import { useEffect } from "react";

const ENTIDADES_SEGURAS: Array<[RegExp, string]> = [
  [/&lt;/gi, "<"],
  [/&gt;/gi, ">"],
  [/&quot;/gi, '"'],
  [/&#39;/gi, "'"],
  [/&amp;/gi, "&"],
];

function normalizarTexto(valor: string) {
  return ENTIDADES_SEGURAS.reduce((texto, [padrao, substituto]) => texto.replace(padrao, substituto), valor);
}

function normalizarNo(no: Node) {
  if (no.nodeType === Node.TEXT_NODE) {
    const atual = no.textContent ?? "";
    if (atual.includes("&")) {
      const normalizado = normalizarTexto(atual);
      if (normalizado !== atual) no.textContent = normalizado;
    }
    return;
  }
  no.childNodes.forEach(normalizarNo);
}

/**
 * Alguns provedores de e-mail devolvem remetentes já escapados como texto
 * (`Nome &lt;email&gt;`). A interface deve continuar tratando isso como texto,
 * nunca como HTML. Este guard só atua dentro do workspace Mail e não usa
 * innerHTML, mantendo a proteção contra conteúdo ativo.
 */
export default function ClinicalPresentationGuard() {
  useEffect(() => {
    function processar() {
      document.querySelectorAll(".cmp-shell").forEach(normalizarNo);
    }

    processar();
    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        mutation.addedNodes.forEach((node) => {
          if (node instanceof Element && (node.matches(".cmp-shell") || node.closest(".cmp-shell"))) normalizarNo(node);
          else if (node.parentElement?.closest(".cmp-shell")) normalizarNo(node);
        });
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, []);

  return null;
}
