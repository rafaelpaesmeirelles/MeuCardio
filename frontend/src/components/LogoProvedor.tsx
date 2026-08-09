type Provedor = "google" | "microsoft" | "apple" | "yahoo";

type Props = {
  provedor: Provedor;
  className?: string;
};

/**
 * Marcas vetoriais locais dos provedores de agenda.
 *
 * Os SVGs ficam no próprio bundle: a tela não depende de CDN, não envia dados
 * a terceiros antes do consentimento e continua identificável offline/PWA.
 */
export default function LogoProvedor({ provedor, className = "" }: Props) {
  const classes = `logo-provedor logo-provedor--${provedor}${className ? ` ${className}` : ""}`;

  if (provedor === "google") {
    return <span className={classes} aria-hidden="true">
      <svg viewBox="0 0 18 18" focusable="false">
        <path fill="#4285F4" d="M17.64 9.205c0-.638-.057-1.252-.164-1.841H9v3.481h4.844a4.14 4.14 0 0 1-1.796 2.716v2.258h2.909c1.702-1.567 2.683-3.875 2.683-6.614Z" />
        <path fill="#34A853" d="M9 18c2.43 0 4.468-.806 5.957-2.181l-2.909-2.258c-.806.54-1.835.859-3.048.859-2.344 0-4.328-1.585-5.037-3.715H.956v2.333A8.999 8.999 0 0 0 9 18Z" />
        <path fill="#FBBC05" d="M3.963 10.705A5.42 5.42 0 0 1 3.682 9c0-.592.102-1.167.281-1.705V4.962H.956A9 9 0 0 0 0 9c0 1.452.347 2.827.956 4.038l3.007-2.333Z" />
        <path fill="#EA4335" d="M9 3.58c1.322 0 2.508.455 3.442 1.346l2.581-2.581C13.464.892 11.426 0 9 0A8.999 8.999 0 0 0 .956 4.962l3.007 2.333C4.672 5.165 6.656 3.58 9 3.58Z" />
      </svg>
    </span>;
  }

  if (provedor === "microsoft") {
    return <span className={classes} aria-hidden="true">
      <svg viewBox="0 0 22 22" focusable="false">
        <path fill="#F25022" d="M1 1h9.5v9.5H1z" />
        <path fill="#7FBA00" d="M11.5 1H21v9.5h-9.5z" />
        <path fill="#00A4EF" d="M1 11.5h9.5V21H1z" />
        <path fill="#FFB900" d="M11.5 11.5H21V21h-9.5z" />
      </svg>
    </span>;
  }

  if (provedor === "apple") {
    // 09/08/2026: o desenho anterior era uma nuvem genérica (pensado para
    // "iCloud"), não a maçã — o Rafael reportou não reconhecer o provedor
    // pelo ícone. Trocado pela silhueta clássica da maçã mordida com folha,
    // reconhecível de imediato, no mesmo espírito já documentado acima para
    // o Yahoo: identifica o provedor sem ser um arquivo de marca de
    // terceiro embutido — é a silhueta redesenhada, em `currentColor`.
    return <span className={classes} aria-hidden="true">
      <svg viewBox="0 0 384 512" focusable="false">
        <path fill="currentColor" d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z" />
      </svg>
    </span>;
  }

  // Yahoo — símbolo geométrico próprio, não o logotipo oficial (mesmo
  // critério já usado acima para a Apple: identifica o provedor sem
  // reproduzir marca registrada de terceiro pixel a pixel).
  return <span className={classes} aria-hidden="true">
    <svg viewBox="0 0 18 18" focusable="false">
      <circle cx="9" cy="9" r="9" fill="#6001D2" />
      <text x="9" y="13" textAnchor="middle" fontSize="10" fontWeight="700" fontFamily="Arial,Helvetica,sans-serif" fill="#fff">Y!</text>
    </svg>
  </span>;
}
