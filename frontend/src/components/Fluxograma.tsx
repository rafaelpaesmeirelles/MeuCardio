import { useEffect, useId, useState } from "react";

function validarSvgGerado(svg: string): string {
  const padroesProibidos = [
    /<\s*(?:script|iframe|object|embed|audio|video|img|image)\b/i,
    /(?:^|\s)on[a-z]+\s*=/i,
    /(?:javascript|data\s*:\s*text\/html)\s*:/i,
    /@import\b/i,
    /url\(\s*["']?(?:https?:|\/\/|data\s*:)/i,
    /(?:href|xlink:href|src)\s*=\s*["'](?:https?:|\/\/|data\s*:)/i,
  ];

  if (!svg.trimStart().startsWith("<svg") || padroesProibidos.some((padrao) => padrao.test(svg))) {
    throw new Error("SVG gerado contém estrutura não permitida.");
  }
  return svg;
}

function removerRaizesTemporarias(id: string) {
  document.getElementById(id)?.remove();
  document.getElementById(`d${id}`)?.remove();
}

/** Renderiza um bloco Mermaid sem inserir SVG como HTML no DOM principal.
 *
 * O Mermaid permanece em `securityLevel: strict`. Os rótulos HTML são
 * necessários porque o acervo usa `<br/>` para organizar textos clínicos
 * extensos. O SVG passa por validação defensiva e é exibido como imagem por
 * Blob URL; `foreignObject` pode existir apenas dentro desse documento de
 * imagem isolado, nunca como HTML executável da aplicação. */
export default function Fluxograma({ fonte }: { fonte: string }) {
  const id = "fluxograma-" + useId().replace(/[^a-zA-Z0-9]/g, "");
  const [svgUrl, setSvgUrl] = useState("");
  const [falhou, setFalhou] = useState(false);

  useEffect(() => {
    let cancelado = false;
    let urlCriada: string | null = null;

    setSvgUrl("");
    setFalhou(false);
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
      } catch (erro) {
        console.error("Falha ao renderizar fluxograma Mermaid", erro);
        if (!cancelado) setFalhou(true);
        removerRaizesTemporarias(id);
      }
    })();

    return () => {
      cancelado = true;
      removerRaizesTemporarias(id);
      if (urlCriada) URL.revokeObjectURL(urlCriada);
    };
  }, [fonte, id]);

  if (falhou) {
    return (
      <p className="fluxograma__erro" role="alert">
        Não foi possível desenhar esta árvore de decisão. Recarregue a página;
        se o problema persistir, use o texto clínico exibido abaixo.
      </p>
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
