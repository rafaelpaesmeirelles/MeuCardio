import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Props = {
  children?: string | null;
  className?: string;
  fallback?: string;
  compact?: boolean;
};

const MARCADORES_EDITORIAIS = [
  "consultada via busca nesta sessão",
  "consultado via busca nesta sessão",
  "websearch",
  "bloqueio de acesso à rede",
  "bloqueio de acesso a rede",
  "texto integral não lido nesta sessão",
  "síntese obtida via resultados de busca",
  "sintese obtida via resultados de busca",
  "verificação humana necessária",
  "verificacao humana necessaria",
];

/**
 * Conteúdo clínico pode carregar trilhas editoriais úteis para auditoria, mas
 * essas trilhas não pertencem à superfície assistencial. Preservamos o texto
 * original no backend e removemos apenas o sufixo operacional da apresentação.
 */
export function textoParaSuperficieClinica(valor?: string | null) {
  if (!valor) return "";
  const normalizado = valor.toLocaleLowerCase("pt-BR");
  const indices = MARCADORES_EDITORIAIS
    .map((marcador) => normalizado.indexOf(marcador))
    .filter((indice) => indice >= 0);

  if (!indices.length) return valor.trim();

  let corte = Math.min(...indices);
  const prefixo = valor.slice(0, corte);
  const fonte = prefixo.toLocaleLowerCase("pt-BR").lastIndexOf("fonte:");
  if (fonte >= 0 && corte - fonte < 260) corte = fonte;

  return valor
    .slice(0, corte)
    .replace(/[—–,:;\s]+$/u, "")
    .trim();
}

export default function ClinicalText({ children, className = "", fallback = "Sem dado publicado.", compact = false }: Props) {
  const texto = textoParaSuperficieClinica(children);
  if (!texto) return <p className={className}>{fallback}</p>;

  return (
    <div className={`clinical-richtext${compact ? " clinical-richtext--compact" : ""}${className ? ` ${className}` : ""}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ href, children: conteudo }) => (
            <a href={href} target="_blank" rel="noreferrer noopener">{conteudo}</a>
          ),
        }}
      >
        {texto}
      </ReactMarkdown>
    </div>
  );
}
