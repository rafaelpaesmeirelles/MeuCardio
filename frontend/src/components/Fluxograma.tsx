import { useEffect, useRef, useState } from "react";

const ELEMENTOS_PROIBIDOS = new Set([
  "script",
  "iframe",
  "object",
  "embed",
  "audio",
  "video",
  "img",
  "image",
  "form",
  "input",
  "button",
  "textarea",
  "select",
  "option",
  "link",
  "meta",
  "base",
  "canvas",
]);

function cssContemReferenciaPerigosa(valor: string): boolean {
  return (
    /@import\b/i.test(valor) ||
    /expression\s*\(/i.test(valor) ||
    /-moz-binding\s*:/i.test(valor) ||
    /url\(\s*["']?(?:https?:|\/\/|data\s*:)/i.test(valor)
  );
}

function validarFonteMermaid(fonte: string) {
  const diretivasInterativas = [
    /\bclick\s+[A-Za-z0-9_-]+/i,
    /\bcallback\b/i,
    /\bcall\s+[A-Za-z0-9_.-]+/i,
    /\bhref\s+["']/i,
    /\bjavascript\s*:/i,
    /\bdata\s*:\s*text\/html/i,
  ];
  if (diretivasInterativas.some((padrao) => padrao.test(fonte))) {
    throw new Error("Fluxograma contém diretiva interativa não permitida.");
  }
}

/**
 * Confere o SVG que o Mermaid já montou no contêiner. O acervo clínico usa
 * `<br/>`, portanto `foreignObject` é necessário para os rótulos, mas scripts,
 * formulários, mídia, eventos e referências externas continuam bloqueados.
 */
function validarSvgMontado(svg: SVGSVGElement) {
  for (const elemento of Array.from(svg.querySelectorAll("*"))) {
    const nome = elemento.localName.toLowerCase();
    if (ELEMENTOS_PROIBIDOS.has(nome)) {
      throw new Error(`SVG gerado contém elemento não permitido: ${nome}.`);
    }

    for (const atributo of Array.from(elemento.attributes)) {
      const nomeAtributo = atributo.name.toLowerCase();
      const valor = atributo.value.trim();

      if (nomeAtributo.startsWith("on")) {
        throw new Error("SVG gerado contém manipulador de evento.");
      }
      if (["href", "xlink:href", "src"].includes(nomeAtributo)) {
        if (valor && !valor.startsWith("#")) {
          throw new Error("SVG gerado contém referência externa.");
        }
      }
      if (nomeAtributo === "style" && cssContemReferenciaPerigosa(valor)) {
        throw new Error("SVG gerado contém estilo não permitido.");
      }
    }

    if (nome === "style" && cssContemReferenciaPerigosa(elemento.textContent || "")) {
      throw new Error("SVG gerado contém folha de estilo não permitida.");
    }
  }
}

type Estado = "carregando" | "pronto" | "erro";

/**
 * Renderiza Mermaid no próprio contêiner por meio da API oficial `run`.
 *
 * A fonte entra no nó somente por `textContent`. O Mermaid opera em modo
 * estrito e o SVG resultante ainda passa pela validação defensiva acima antes
 * de ser mostrado. Assim não há transporte por Blob/imagem nem parsing manual
 * de marcação pela aplicação.
 */
export default function Fluxograma({ fonte }: { fonte: string }) {
  const recipiente = useRef<HTMLDivElement>(null);
  const [estado, setEstado] = useState<Estado>("carregando");

  useEffect(() => {
    let cancelado = false;
    const alvo = recipiente.current;
    if (!alvo) return;

    setEstado("carregando");
    alvo.removeAttribute("data-processed");
    alvo.textContent = fonte;

    (async () => {
      try {
        validarFonteMermaid(fonte);
        const mermaid = (await import("mermaid")).default;
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: "strict",
          htmlLabels: true,
          flowchart: { htmlLabels: true, useMaxWidth: true },
          theme: "base",
          fontFamily: "Inter, system-ui, sans-serif",
          themeVariables: {
            primaryColor: "#eef5f8",
            primaryBorderColor: "#1c7293",
            primaryTextColor: "#26333b",
            lineColor: "#0b2e45",
            secondaryColor: "#fcfcfc",
            tertiaryColor: "#ffffff",
            fontSize: "14px",
          },
        });

        await mermaid.parse(fonte);
        await mermaid.run({ nodes: [alvo], suppressErrors: true });
        if (cancelado) return;

        const svg = alvo.querySelector("svg");
        if (!(svg instanceof SVGSVGElement)) {
          throw new Error("O Mermaid não montou um SVG no contêiner.");
        }

        validarSvgMontado(svg);
        svg.removeAttribute("height");
        svg.setAttribute("width", "100%");
        svg.setAttribute("preserveAspectRatio", "xMinYMin meet");
        svg.style.display = "block";
        svg.style.width = "100%";
        svg.style.minWidth = "760px";
        svg.style.height = "auto";
        svg.style.maxWidth = "none";
        svg.style.margin = "0 auto";
        setEstado("pronto");
      } catch (erro) {
        console.error("Falha ao renderizar fluxograma Mermaid", erro);
        if (!cancelado) {
          alvo.textContent = "";
          alvo.removeAttribute("data-processed");
          setEstado("erro");
        }
      }
    })();

    return () => {
      cancelado = true;
      alvo.textContent = "";
      alvo.removeAttribute("data-processed");
    };
  }, [fonte]);

  return (
    <div className="fluxograma__recipiente">
      {estado === "carregando" && (
        <p className="eyebrow" role="status">Desenhando o fluxograma…</p>
      )}
      {estado === "erro" && (
        <p className="fluxograma__erro" role="alert">
          Não foi possível desenhar esta árvore de decisão. Recarregue a página;
          se o problema persistir, use o texto clínico exibido abaixo.
        </p>
      )}
      <div
        ref={recipiente}
        className="mermaid fluxograma"
        role="img"
        aria-label="Fluxograma clínico"
        aria-hidden={estado !== "pronto"}
        style={{
          visibility: estado === "pronto" ? "visible" : "hidden",
          overflowX: "auto",
          margin: estado === "pronto" ? "1rem 0" : 0,
          height: estado === "pronto" ? "auto" : 0,
          textAlign: "center",
        }}
      />
    </div>
  );
}
