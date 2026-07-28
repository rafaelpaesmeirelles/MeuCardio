import { useEffect, useId, useRef, useState } from "react";

/** Renderiza um bloco ```mermaid``` como diagrama.
 *
 * A lib entra por import() dinâmico de propósito: o mermaid é grande e só faz
 * falta em documento que tenha diagrama, então fica num chunk à parte em vez de
 * pesar no bundle inicial de quem nunca abre um fluxograma. */
export default function Fluxograma({ fonte }: { fonte: string }) {
  // useId devolve algo como ":r3:", com caracteres inválidos para id de DOM.
  const id = "fluxograma-" + useId().replace(/[^a-zA-Z0-9]/g, "");
  const [svg, setSvg] = useState("");
  const [falhou, setFalhou] = useState(false);
  const container = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelado = false;

    (async () => {
      try {
        const mermaid = (await import("mermaid")).default;
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: "strict", // não permite HTML arbitrário nos rótulos
          theme: "base",
          fontFamily: "Inter, system-ui, sans-serif",
          // Espelha os tokens de tokens.css. O mermaid recebe cor literal, não
          // aceita var(--…), então este é o único ponto do frontend em que a
          // paleta aparece em hex fora do arquivo de tema — se a paleta mudar,
          // mudar aqui junto.
          themeVariables: {
            primaryColor: "#eef5f8",      // --acento-tinta
            primaryBorderColor: "#1c7293", // --teal
            primaryTextColor: "#26333b",   // --ink
            lineColor: "#0b2e45",          // --navy
            secondaryColor: "#fcfcfc",     // --off-white
            tertiaryColor: "#ffffff",
            fontSize: "14px",
          },
        });
        const { svg } = await mermaid.render(id, fonte);
        if (!cancelado) setSvg(svg);
      } catch {
        // Sintaxe inválida no diagrama não pode derrubar a página inteira:
        // cai para o código-fonte, que ainda é legível.
        if (!cancelado) setFalhou(true);
        document.getElementById(id)?.remove(); // mermaid deixa nó órfão ao falhar
      }
    })();

    return () => { cancelado = true; };
  }, [fonte, id]);

  if (falhou) {
    return (
      <pre style={{ overflowX: "auto" }}>
        <code>{fonte}</code>
      </pre>
    );
  }

  if (!svg) return <p className="eyebrow" role="status">Desenhando o fluxograma…</p>;

  return (
    <div
      ref={container}
      className="fluxograma"
      role="img"
      aria-label="Fluxograma clínico"
      style={{ overflowX: "auto", margin: "1rem 0", textAlign: "center" }}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
