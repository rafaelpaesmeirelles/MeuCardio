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
        <img src="/corviamail-icone.svg" alt="" aria-hidden="true" />
      </span>
    );
  }

  return (
    <div className="corvia-mail-logo" role="img" aria-label="CorVIA Mail">
      <img src="/corviamail-icone.svg" alt="" aria-hidden="true" />
      <span className="corvia-mail-logo__wordmark">
        <span>Corv</span><b>IA</b><em>Mail</em>
      </span>
    </div>
  );
}
