/** Logo do CorvIA Mail — envelope com o coração-ECG da marca no lugar de
 * encontro da aba, escolhido pelo Rafael em 30/07/2026. O ícone é um SVG
 * fixo (`/corviamail-icone.svg`, só navy + vermelho — cores já oficiais);
 * a palavra "CorvIA Mail" é texto de verdade, não parte do arquivo, para
 * não depender de fonte embutida no SVG e continuar selecionável/acessível.
 * O "Mail" em teal reaproveita o papel de acento do sistema de tokens —
 * mesma lógica das opções de logo apresentadas ao Rafael antes da escolha. */
export default function LogoCorviaMail({ tamanho = "normal" }: { tamanho?: "normal" | "compacto" }) {
  const compacto = tamanho === "compacto";
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: compacto ? "0.4rem" : "0.6rem" }}>
      <img src="/corviamail-icone.svg" alt="" aria-hidden="true"
           style={{ height: compacto ? 28 : 48, width: "auto" }} />
      <span style={{
        fontFamily: "Georgia, 'Iowan Old Style', 'Palatino Linotype', 'Times New Roman', serif",
        fontWeight: 700, fontSize: compacto ? "1.1rem" : "1.6rem", letterSpacing: "-0.01em", lineHeight: 1,
      }}>
        <span style={{ color: "var(--primaria)" }}>Corv</span>
        <span style={{ color: "var(--acao)" }}>IA</span>
        <span style={{
          color: "var(--acento)", fontWeight: 500, marginLeft: "0.24em",
          fontFamily: "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif",
        }}>
          Mail
        </span>
      </span>
    </div>
  );
}
