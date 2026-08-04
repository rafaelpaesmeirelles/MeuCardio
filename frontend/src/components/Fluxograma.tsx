import { useEffect, useRef, useState } from "react";

const ELEMENTOS_PROIBIDOS = new Set([
  "script", "iframe", "object", "embed", "audio", "video", "img", "image",
  "form", "input", "button", "textarea", "select", "option", "link", "meta",
  "base", "canvas",
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
      if (["href", "xlink:href", "src"].includes(nomeAtributo) && valor && !valor.startsWith("#")) {
        throw new Error("SVG gerado contém referência externa.");
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
const ZOOMS = [100, 125, 150, 175, 200];

export default function Fluxograma({ fonte }: { fonte: string }) {
  const recipiente = useRef<HTMLDivElement>(null);
  const quadro = useRef<HTMLDivElement>(null);
  const [estado, setEstado] = useState<Estado>("carregando");
  const [zoom, setZoom] = useState(100);

  useEffect(() => {
    let cancelado = false;
    const alvo = recipiente.current;
    if (!alvo) return;

    setEstado("carregando");
    setZoom(100);
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
        if (!svg.getAttribute("viewBox")) {
          const caixa = svg.getBBox();
          if (caixa.width > 0 && caixa.height > 0) {
            svg.setAttribute("viewBox", `${caixa.x} ${caixa.y} ${caixa.width} ${caixa.height}`);
          }
        }
        svg.removeAttribute("height");
        svg.removeAttribute("width");
        svg.setAttribute("preserveAspectRatio", "xMidYMin meet");
        svg.style.display = "block";
        svg.style.width = "100%";
        svg.style.height = "auto";
        svg.style.maxWidth = "none";
        svg.style.minWidth = "0";
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

  useEffect(() => {
    const svg = recipiente.current?.querySelector("svg");
    if (svg instanceof SVGSVGElement) {
      svg.style.width = `${zoom}%`;
    }
  }, [zoom, estado]);

  async function telaCheia() {
    const alvo = quadro.current;
    if (!alvo) return;
    if (document.fullscreenElement) {
      await document.exitFullscreen();
    } else {
      await alvo.requestFullscreen();
    }
  }

  return (
    <div
      ref={quadro}
      className="fluxograma__recipiente"
      style={{
        width: "100%",
        minWidth: 0,
        background: "var(--superficie)",
        padding: estado === "pronto" ? "0.75rem" : 0,
      }}
    >
      {estado === "carregando" && (
        <p className="eyebrow" role="status">Desenhando o fluxograma…</p>
      )}
      {estado === "erro" && (
        <p className="fluxograma__erro" role="alert">
          Não foi possível desenhar esta árvore de decisão. Recarregue a página;
          se o problema persistir, use o texto clínico exibido abaixo.
        </p>
      )}
      {estado === "pronto" && (
        <div style={{ display: "flex", gap: 6, justifyContent: "flex-end", alignItems: "center", flexWrap: "wrap", marginBottom: "0.5rem" }}>
          <label htmlFor="zoom-fluxograma" className="eyebrow" style={{ margin: 0 }}>Zoom</label>
          <select
            id="zoom-fluxograma"
            value={zoom}
            onChange={(e) => setZoom(Number(e.target.value))}
            style={{ width: "auto" }}
          >
            {ZOOMS.map((valor) => <option key={valor} value={valor}>{valor}%</option>)}
          </select>
          <button type="button" className="botao botao--secundario" onClick={telaCheia}>
            Tela cheia
          </button>
        </div>
      )}
      <div
        style={{
          width: "100%",
          minWidth: 0,
          overflowX: zoom > 100 ? "auto" : "hidden",
          overflowY: "visible",
        }}
      >
        <div
          ref={recipiente}
          className="mermaid fluxograma"
          role="img"
          aria-label="Fluxograma clínico"
          aria-hidden={estado !== "pronto"}
          style={{
            visibility: estado === "pronto" ? "visible" : "hidden",
            width: "100%",
            minWidth: 0,
            margin: estado === "pronto" ? "0 auto" : 0,
            height: estado === "pronto" ? "auto" : 0,
            textAlign: "center",
          }}
        />
      </div>
    </div>
  );
}
