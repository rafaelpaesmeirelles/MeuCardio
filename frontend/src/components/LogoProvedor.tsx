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
    return <span className={classes} aria-hidden="true">
      <svg viewBox="0 0 24 24" focusable="false">
        <path fill="currentColor" d="M20.013 10.726v-.028A6.346 6.346 0 0 0 8.09 7.67a3.414 3.414 0 0 0-4.989 2.829A4.72 4.72 0 0 0 4.719 19.648h14.807a4.475 4.475 0 0 0 .487-8.922Z" />
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
