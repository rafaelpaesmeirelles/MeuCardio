import "../styles/grafo-constelacao.css";

/**
 * Visualização do Grafo de Conhecimento Clínico (issue #52) — a "demonstração
 * premium" única da vitrine de login e o mockup do slide de onboarding que
 * ensina a mudança de paradigma do produto: não "a Corvia tem vários
 * módulos", e sim "tudo na Corvia está conectado".
 *
 * É uma ilustração fiel ao que o produto realmente faz, não uma promessa: os
 * tipos de entidade desenhados aqui (medicamento, documento, evidência,
 * estudo, exame, caso clínico, trilha) são exatamente os tipos que
 * `backend/app/services/knowledge_graph.py` registra em
 * `TIPOS_ENTIDADE_PERMITIDOS` e que `GET /api/grafo/relacionados` agrupa na
 * resposta — os mesmos que `GrafoRelacionados.tsx` já exibe hoje nas 8
 * páginas de detalhe. Nenhum tipo inventado.
 *
 * SVG inline puro: sem dependência nova, sem imagem remota, sem canvas —
 * a tela de login precisa abrir rápido. Todo o movimento é decorativo e
 * desligado por `prefers-reduced-motion` (ver grafo-constelacao.css).
 */

type No = {
  /** Rótulo curto exibido dentro do nó. */
  rotulo: string;
  /** Tipo de entidade, no vocabulário real do grafo. */
  tipo: string;
  x: number;
  y: number;
};

/* Constelação em torno do nó central: cada satélite é um TIPO diferente de
   entidade, para mostrar que a navegação atravessa categorias — que é
   justamente o que o grafo faz e uma lista por tema não faz. */
const SATELITES: No[] = [
  { rotulo: "Hipertensão", tipo: "Doença", x: 150, y: 26 },
  { rotulo: "Classe I · A", tipo: "Evidência", x: 262, y: 74 },
  { rotulo: "LIFE", tipo: "Estudo", x: 262, y: 158 },
  { rotulo: "HAS resistente", tipo: "Caso clínico", x: 150, y: 206 },
  { rotulo: "Potássio", tipo: "Exame", x: 38, y: 158 },
  { rotulo: "Anti-hipertensivos", tipo: "Trilha", x: 38, y: 74 },
];

const CENTRO = { x: 150, y: 116 };

/** Largura da pílula de cada nó, em unidades do viewBox. */
function largura(no: No): number {
  return Math.max(58, no.rotulo.length * 5.2 + 20);
}

export default function GrafoConstelacao({
  variante = "escuro",
  className = "",
}: {
  variante?: "escuro" | "claro";
  className?: string;
}) {
  return (
    <div className={`grafo-const grafo-const--${variante} ${className}`.trim()}>
      {/* viewBox com folga lateral negativa: a pílula mais larga ("Trilha ·
          Anti-hipertensivos") é centrada em x=38 e ultrapassaria a borda
          esquerda de um viewBox iniciando em 0 — ela ficava cortada dentro do
          mockup do tour, que recorta o excedente. */}
      <svg
        viewBox="-30 -6 360 244"
        role="img"
        aria-label="Grafo de conhecimento da Corvia: um medicamento conectado a doença, evidência, estudo, exame, caso clínico e trilha de estudo, navegável em qualquer direção."
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Anéis de fundo — profundidade, sem competir com o conteúdo. */}
        <ellipse className="grafo-const__anel" cx={CENTRO.x} cy={CENTRO.y} rx="118" ry="88" />
        <ellipse className="grafo-const__anel grafo-const__anel--interno" cx={CENTRO.x} cy={CENTRO.y} rx="74" ry="55" />

        {/* Arestas centro ↔ satélite. O tracejado "flui" nos dois sentidos em
            metade delas, reforçando que a relação não tem direção única. */}
        <g className="grafo-const__arestas">
          {SATELITES.map((no, i) => (
            <line
              key={no.rotulo}
              className={`grafo-const__aresta${i % 2 === 0 ? " grafo-const__aresta--volta" : ""}`}
              x1={CENTRO.x}
              y1={CENTRO.y}
              x2={no.x}
              y2={no.y}
              style={{ animationDelay: `${i * 0.45}s` }}
            />
          ))}
          {/* Arestas entre satélites vizinhos — "qualquer direção", não uma estrela. */}
          {SATELITES.map((no, i) => {
            const proximo = SATELITES[(i + 1) % SATELITES.length];
            return (
              <line
                key={`${no.rotulo}-borda`}
                className="grafo-const__aresta grafo-const__aresta--borda"
                x1={no.x}
                y1={no.y}
                x2={proximo.x}
                y2={proximo.y}
              />
            );
          })}
        </g>

        {/* Satélites */}
        {SATELITES.map((no) => {
          const w = largura(no);
          return (
            <g className="grafo-const__no" key={no.rotulo}>
              <rect x={no.x - w / 2} y={no.y - 15} width={w} height={30} rx="9" />
              <text className="grafo-const__tipo" x={no.x} y={no.y - 2}>
                {no.tipo}
              </text>
              <text className="grafo-const__rotulo" x={no.x} y={no.y + 9}>
                {no.rotulo}
              </text>
            </g>
          );
        })}

        {/* Nó central em destaque */}
        <g className="grafo-const__no grafo-const__no--centro">
          <circle className="grafo-const__halo" cx={CENTRO.x} cy={CENTRO.y} r="42" />
          <circle className="grafo-const__halo grafo-const__halo--dois" cx={CENTRO.x} cy={CENTRO.y} r="42" />
          <rect x={CENTRO.x - 47} y={CENTRO.y - 19} width="94" height="38" rx="12" />
          <text className="grafo-const__tipo" x={CENTRO.x} y={CENTRO.y - 3}>
            Medicamento
          </text>
          <text className="grafo-const__rotulo grafo-const__rotulo--centro" x={CENTRO.x} y={CENTRO.y + 11}>
            Losartana
          </text>
        </g>
      </svg>
    </div>
  );
}
