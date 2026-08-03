import { useEffect, useId, useState } from "react";

function validarSvgGerado(svg: string): string {
  const padroesProibidos = [
    /<\s*(?:script|foreignObject|iframe|object|embed|audio|video)\b/i,
    /(?:^|\s)on[a-z]+\s*=/i,
    /(?:javascript|data\s*:\s*text\/html)\s*:/i,
    /@import\b/i,
    /url\(\s*["']?(?:https?:|\/\/)/i,
    /(?:href|xlink:href)\s*=\s*["'](?:https?:|\/\/)/i,
  ];

  if (!svg.trimStart().startsWith("<svg") || padroesProibidos.some((padrao) => padrao.test(svg))) {
    throw new Error("SVG gerado contém estrutura não permitida.");
  }
  return svg;
}

/** Renderiza um bloco Mermaid sem inserir SVG como HTML no DOM.
 *
 * O Mermaid permanece em `securityLevel: strict`. O SVG resultante passa por
 * uma validação defensiva e é exibido como imagem por Blob URL; assim, mesmo
 * conteúdo clínico malformado não vira nó HTML executável na página. */
export default function Fluxograma({ fonte }: { fonte: string }) {
  const id = "fluxograma-" + useId().replace(/[^a-zA-Z0-9]/g, "");
  const [svgUrl, setSvgUrl] = useState("");
  const [falhou, setFalhou] = useState(false);

  useEffect(() => {
    let cancelado = false;
    let urlCriada: string | null = null;

    setSvgUrl("");
    setFalhou(false);

    (async () => {
      try {
        const mermaid = (await import("mermaid")).default;
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: "strict",
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

        const resultado = await mermaid.render(id, fonte);
        const svgSeguro = validarSvgGerado(resultado.svg);
        urlCriada = URL.createObjectURL(
          new Blob([svgSeguro], { type: "image/svg+xml;charset=utf-8" }),
        );

        if (cancelado) {
          URL.revokeObjectURL(urlCriada);
          urlCriada = null;
          return;
        }
        setSvgUrl(urlCriada);
      } catch {
        if (!cancelado) setFalhou(true);
        document.getElementById(id)?.remove();
      }
    })();

    return () => {
      cancelado = true;
      if (urlCriada) URL.revokeObjectURL(urlCriada);
    };
  }, [fonte, id]);

  if (falhou) {
    return (
      <pre style={{ overflowX: "auto" }}>
        <code>{fonte}</code>
      </pre>
    );
  }

  if (!svgUrl) return <p className="eyebrow" role="status">Desenhando o fluxograma…</p>;

  return (
    <div
      className="fluxograma"
      role="img"
      aria-label="Fluxograma clínico"
      style={{ overflowX: "auto", margin: "1rem 0", textAlign: "center" }}
    >
      <img
        src={svgUrl}
        alt="Fluxograma clínico"
        style={{ display: "block", maxWidth: "100%", height: "auto", margin: "0 auto" }}
      />
    </div>
  );
}
