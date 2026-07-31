/** Logo do CorvIA Chat — opção "balão-coração", escolhida pelo Rafael em
 *  31/07/2026 entre quatro direções apresentadas.
 *
 *  O ícone é o coração-ECG da marca ganhando um rabinho de balão de fala: é a
 *  mesma raiz visual do CorvIA Mail (que partiu do coração-ECG com envelope),
 *  o que mantém os dois add-ons como família em vez de dois desenhos soltos.
 *
 *  O SVG é inline, e não um arquivo em /public como o do Mail, porque este
 *  precisa trocar de cor conforme o fundo: o coração é navy sobre fundo claro
 *  e vermelho sobre o navy do cabeçalho e do botão flutuante — sobre navy, um
 *  coração navy simplesmente desaparece. Um arquivo estático não faz isso sem
 *  duplicar o desenho em dois arquivos que sairiam de sincronia.
 *
 *  Só cores oficiais: navy (--primaria), vermelho (--acao), branco. */

type Variante = "claro" | "sobre-navy";

export function IconeChat({ tamanho = 24, variante = "claro" }: { tamanho?: number; variante?: Variante }) {
  // Sobre navy o coração vira vermelho; sobre fundo claro, navy. O pulso é
  // sempre branco, que é o que garante o contraste dentro do coração nos dois
  // casos.
  const corpo = variante === "sobre-navy" ? "#D5001D" : "#0B2E45";
  return (
    <svg width={tamanho} height={tamanho} viewBox="0 0 48 48" aria-hidden="true" focusable="false">
      <path
        d="M24 41S6 30 6 18.5C6 12.7 10.6 8 16.2 8c3.3 0 6.2 1.6 8 4.1C26 9.6 28.9 8 32.2 8 37.8 8 42 12.7 42 18.5 42 30 24 41 24 41z"
        fill={corpo}
      />
      {/* O rabinho de balão sai do lobo esquerdo, é o que transforma o coração
          da marca em "conversa". Desenhado por baixo do coração na ordem de
          pintura para a emenda não aparecer. */}
      <path d="M17 38.5l-6 6.5v-7.5z" fill={corpo} />
      <path
        d="M11 21h6l3-6 4 12 3-8 2.5 2H37"
        fill="none"
        stroke="#FFFFFF"
        strokeWidth="2.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function LogoChat({ tamanho = "normal" }: { tamanho?: "normal" | "compacto" }) {
  const compacto = tamanho === "compacto";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: compacto ? "0.4rem" : "0.55rem" }}>
      <IconeChat tamanho={compacto ? 26 : 42} />
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
          Chat
        </span>
      </span>
    </div>
  );
}
