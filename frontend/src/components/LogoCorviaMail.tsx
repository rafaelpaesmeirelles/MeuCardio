/** Logo do CorVIA Mail.
 * Em superfícies de marca completas, combina ícone + wordmark. No modo
 * compacto (topbar da caixa de entrada), o nome já aparece na identidade da
 * conta ao lado; por isso exibimos somente o símbolo e evitamos duplicidade.
 */
export default function LogoCorviaMail({ tamanho = "normal" }: { tamanho?: "normal" | "compacto" }) {
  const compacto = tamanho === "compacto";

  if (compacto) {
    return (
      <span className="corvia-mail-mark" role="img" aria-label="CorVIA Mail">
        <img src="/corviamail-icone.svg" alt="" aria-hidden="true" style={{ height: 28, width: "auto" }} />
      </span>
    );
  }

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "0.6rem" }}>
      <img src="/corviamail-icone.svg" alt="" aria-hidden="true" style={{ height: 48, width: "auto" }} />
      <span style={{
        fontFamily: "Georgia, 'Iowan Old Style', 'Palatino Linotype', 'Times New Roman', serif",
        fontWeight: 700, fontSize: "1.6rem", letterSpacing: "-0.01em", lineHeight: 1,
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
