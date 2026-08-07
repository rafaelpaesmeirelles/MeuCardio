/** Logo do Assistente Clínica — o coração-ECG da marca com uma cruz médica
 *  (mesma cor de acento, teal) pendurada no lobo direito, escolhido em
 *  07/08/2026 junto com o Assistente Pessoal na divisão em dois modos
 *  (Trabalho 15).
 *
 *  Mesma raiz visual de LogoChat/LogoCorviaMail — o coração e o pulso de ECG
 *  são idênticos aos dos outros dois ícones da família, só o acento muda.
 *  A cruz sinaliza "conteúdo médico/científico" sem precisar de texto.
 *
 *  SVG inline (não arquivo estático) pela mesma razão do Chat: o corpo do
 *  coração precisa trocar de cor conforme o fundo (navy sobre claro,
 *  vermelho sobre o navy do cabeçalho) — um arquivo fixo não faz isso. O
 *  selo da cruz fica sempre teal, com um contorno branco fino para nunca
 *  sumir contra nenhum dos dois fundos. */

type Variante = "claro" | "sobre-navy";

export function IconeAssistenteClinica({ tamanho = 24, variante = "claro" }: { tamanho?: number; variante?: Variante }) {
  const corpo = variante === "sobre-navy" ? "#D5001D" : "#0B2E45";
  return (
    <svg width={tamanho} height={tamanho} viewBox="0 0 48 48" aria-hidden="true" focusable="false">
      <path
        d="M24 41S6 30 6 18.5C6 12.7 10.6 8 16.2 8c3.3 0 6.2 1.6 8 4.1C26 9.6 28.9 8 32.2 8 37.8 8 42 12.7 42 18.5 42 30 24 41 24 41z"
        fill={corpo}
      />
      <path
        d="M11 21h6l3-6 4 12 3-8 2.5 2H37"
        fill="none"
        stroke="#FFFFFF"
        strokeWidth="2.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Cruz médica — o acento que diferencia esta variante do Chat. */}
      <g transform="translate(30,29)">
        <rect x="0" y="0" width="13" height="13" rx="3" fill="#1C7293" stroke="#FFFFFF" strokeWidth="1.3" />
        <path d="M6.5 3v7M3 6.5h7" stroke="#FFFFFF" strokeWidth="1.9" strokeLinecap="round" />
      </g>
    </svg>
  );
}

export default function LogoAssistenteClinica({ tamanho = "normal" }: { tamanho?: "normal" | "compacto" }) {
  const compacto = tamanho === "compacto";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: compacto ? "0.4rem" : "0.55rem" }}>
      <IconeAssistenteClinica tamanho={compacto ? 26 : 42} />
      <span
        style={{
          fontFamily: "Georgia, 'Iowan Old Style', 'Palatino Linotype', 'Times New Roman', serif",
          fontWeight: 700,
          fontSize: compacto ? "1.05rem" : "1.5rem",
          letterSpacing: "-0.01em",
          lineHeight: 1,
        }}
      >
        <span style={{ color: "var(--primaria)" }}>Corv</span>
        <span style={{ color: "var(--acao)" }}>IA</span>
        <span
          style={{
            color: "var(--acento)",
            fontWeight: 500,
            marginLeft: "0.22em",
            fontFamily: "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif",
          }}
        >
          Assistente Clínica
        </span>
      </span>
    </div>
  );
}
