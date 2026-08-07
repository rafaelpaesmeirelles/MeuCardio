/** Logo do Assistente Pessoal — o coração-ECG da marca com um pequeno
 *  calendário (mesma cor de acento, teal) pendurado no lobo direito,
 *  escolhido em 07/08/2026 junto com o Assistente Clínica (Trabalho 15).
 *
 *  O calendário sinaliza a conexão com agenda/deslocamento/rotina — o que
 *  distingue este modo do Clínica (cruz médica). Mesma raiz visual
 *  (coração + pulso de ECG) das outras três marcas da família
 *  (Chat/Mail/Clínica); só o acento muda.
 *
 *  SVG inline pela mesma razão do Chat/Clínica: o corpo do coração troca
 *  de cor conforme o fundo. O selo do calendário fica sempre teal com
 *  contorno branco fino, para não sumir contra nenhum dos dois fundos. */

type Variante = "claro" | "sobre-navy";

export function IconeAssistentePessoal({ tamanho = 24, variante = "claro" }: { tamanho?: number; variante?: Variante }) {
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
      {/* Calendário — o acento que diferencia esta variante do Clínica. */}
      <g transform="translate(30,28)">
        <rect x="0" y="1" width="13" height="12" rx="2.4" fill="#1C7293" stroke="#FFFFFF" strokeWidth="1.3" />
        <rect x="0" y="1" width="13" height="3.6" rx="2.2" fill="#0B2E45" />
        <path d="M3.4 -1v4.4M9.6 -1v4.4" stroke="#1C7293" strokeWidth="1.6" strokeLinecap="round" />
        <path d="M3.4 8l2 2 4.2-4.6" fill="none" stroke="#FFFFFF" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </g>
    </svg>
  );
}

export default function LogoAssistentePessoal({ tamanho = "normal" }: { tamanho?: "normal" | "compacto" }) {
  const compacto = tamanho === "compacto";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: compacto ? "0.4rem" : "0.55rem" }}>
      <IconeAssistentePessoal tamanho={compacto ? 26 : 42} />
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
          Assistente Pessoal
        </span>
      </span>
    </div>
  );
}
