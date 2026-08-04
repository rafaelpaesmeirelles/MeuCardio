import { useEffect, useId, useRef, useState } from "react";

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

/**
 * Valida e interpreta o SVG retornado pelo Mermaid.
 *
 * O acervo clínico usa `<br/>` nos rótulos, então o Mermaid gera
 * `foreignObject`. O elemento é permitido, mas qualquer capacidade de executar
 * código, enviar formulário ou carregar recurso externo continua bloqueada.
 */
function validarSvgGerado(svg: string): SVGSVGElement {
  if (!svg.trimStart().startsWith("<svg")) {
    throw new Error("O Mermaid não retornou um SVG.");
  }
  if (/\bjavascript\s*:/i.test(svg) || /\bdata\s*:\s*text\/html/i.test(svg)) {
    throw new Error("SVG gerado contém protocolo não permitido.");
  }

  const documentoSvg = new DOMParser().parseFromString(svg, "image/svg+xml");
  if (documentoSvg.querySelector("parsererror")) {
    throw new Error("SVG gerado é inválido.");
  }

  const raiz = documentoSvg.documentElement;
  if (raiz.localName.toLowerCase() !== "svg") {
    throw new Error("A raiz do documento gerado não é SVG.");
  }

  for (const elemento of Array.from(documentoSvg.querySelectorAll("*"))) {
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

  return raiz as unknown as SVGSVGElement;
}

function removerRaizesTemporarias(id: string) {
  document.getElementById(id)?.remove();
  document.getElementById(`d${id}`)?.remove();
}

type Estado = "carregando" | "pronto" | "erro";

/**
 * Renderiza um bloco Mermaid como SVG validado dentro de um contêiner isolado.
 *
 * Não usa `dangerouslySetInnerHTML`, `<img>` nem Blob URL. Isso evita o problema
 * observado em produção, no qual o navegador exibia o SVG com `foreignObject`
 * como imagem quebrada. O nó validado é importado pelo DOM e anexado por
 * `replaceChildren`.
 */
export default function Fluxograma({ fonte }: { fonte: string }) {
  const id = "fluxograma-" + useId().replace(/[^a-zA-Z0-9]/g, "");
  const recipiente = useRef<HTMLDivElement>(null);
  const [estado, setEstado] = useState<Estado>("carregando");

  useEffect(() => {
    let cancelado = false;

    setEstado("carregando");
    recipiente.current?.replaceChildren();
    removerRaizesTemporarias(id);

    (async () => {
      try {
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
        const resultado = await mermaid.render(id, fonte);
        const svgValidado = validarSvgGerado(resultado.svg);

        if (cancelado || !recipiente.current) return;

        const svgImportado = document.importNode(svgValidado, true) as SVGSVGElement;
        svgImportado.removeAttribute("height");
        svgImportado.setAttribute("width", "100%");
        svgImportado.setAttribute("preserveAspectRatio", "xMinYMin meet");
        svgImportado.style.display = "block";
        svgImportado.style.width = "100%";
        svgImportado.style.minWidth = "760px";
        svgImportado.style.height = "auto";
        svgImportado.style.maxWidth = "none";
        svgImportado.style.margin = "0 auto";

        recipiente.current.replaceChildren(svgImportado);
        setEstado("pronto");
        removerRaizesTemporarias(id);
      } catch (erro) {
        console.error("Falha ao renderizar fluxograma Mermaid", erro);
        if (!cancelado) setEstado("erro");
        recipiente.current?.replaceChildren();
        removerRaizesTemporarias(id);
      }
    })();

    return () => {
      cancelado = true;
      recipiente.current?.replaceChildren();
      removerRaizesTemporarias(id);
    };
  }, [fonte, id]);

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
        className="fluxograma"
        role="img"
        aria-label="Fluxograma clínico"
        aria-hidden={estado !== "pronto"}
        style={{
          display: estado === "pronto" ? "block" : "none",
          overflowX: "auto",
          margin: "1rem 0",
          textAlign: "center",
        }}
      />
    </div>
  );
}
