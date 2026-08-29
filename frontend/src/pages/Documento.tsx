import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "../lib/api";
import { Carregando, Erro, SeloRevisao } from "../components/Estado";
import Fluxograma from "../components/Fluxograma";
import ExportarApresentacao from "../components/ExportarApresentacao";
import TudoSobreEsteTema from "../components/TudoSobreEsteTema";
import GrafoRelacionados from "../components/GrafoRelacionados";

/** Extrai o código de um bloco ```mermaid```; devolve null para qualquer outro
 * bloco. Sobrescrevemos `pre` em vez de `code` porque o diagrama é uma <div>, e
 * <div> dentro de <pre> é aninhamento inválido. */
function fonteMermaid(children: unknown): string | null {
  const filho: any = Array.isArray(children) ? children[0] : children;
  const classe = filho?.props?.className ?? "";
  if (!String(classe).split(/\s+/).includes("language-mermaid")) return null;
  const conteudo = filho.props.children;
  const texto = Array.isArray(conteudo) ? conteudo.join("") : String(conteudo ?? "");
  return texto.trim() || null;
}

function fonteOriginal(sourceRefs: string[]): string | null {
  for (const referencia of sourceRefs) {
    const url = referencia.match(/https?:\/\/[^\s)\]}]+/i)?.[0];
    if (url) return url.replace(/[.,;]+$/, "");

    const doi = referencia.match(/\b10\.\d{4,9}\/[-._;()/:A-Z0-9]+\b/i)?.[0];
    if (doi) return `https://doi.org/${doi.replace(/[.,;]+$/, "")}`;
  }
  return null;
}

type Doc = {
  title: string; theme: string; kind: string; summary: string | null; body_md: string;
  source_refs: string[]; review_status: string; version: number;
};

export default function Documento() {
  const { slug } = useParams();
  const [doc, setDoc] = useState<Doc | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.get<Doc>(`/library/documents/${slug}`).then(setDoc).catch((e) => setErro(e.message));
  }, [slug]);

  if (erro) return <Erro mensagem={erro} />;
  if (!doc) return <Carregando />;

  const contemFluxograma = /```mermaid\s/i.test(doc.body_md);
  const originalUrl = fonteOriginal(doc.source_refs);
  const temResumo = Boolean(doc.summary?.trim());

  return (
    <article style={{ maxWidth: contemFluxograma ? "100%" : "72ch", minWidth: 0 }}>
      <Link to="/biblioteca" className="eyebrow">← Biblioteca</Link>
      <p className="eyebrow" style={{ marginTop: "0.8rem" }}>{doc.theme} · {doc.kind}</p>
      <h1>{doc.title}</h1>
      <div style={{ display: "flex", gap: 8, alignItems: "center", margin: "0.5rem 0 1.2rem" }}>
        <SeloRevisao status={doc.review_status} />
        <span className="selo">versão {doc.version}</span>
      </div>

      <div className="acoes-linha" style={{ margin: "0 0 1rem", flexWrap: "wrap" }} aria-label="Opções de leitura do documento científico">
        {temResumo && <a className="btn primario" href="#resumo-corvia">Resumo CorVIA</a>}
        <a className="btn" href="#leitura-portugues">Traduzido</a>
        {originalUrl && (
          <a className="btn" href={originalUrl} target="_blank" rel="noopener noreferrer">Original ↗</a>
        )}
      </div>

      {temResumo && (
        <div id="resumo-corvia" className="cartao" style={{ marginBottom: "1rem", scrollMarginTop: "1rem" }}>
          <p className="eyebrow">Resumo CorVIA</p>
          <p>{doc.summary}</p>
        </div>
      )}

      <ExportarApresentacao slug={slug!} titulo={doc.title} />

      <div id="leitura-portugues" className="cartao" style={{ minWidth: 0, overflow: "visible", scrollMarginTop: "1rem" }}>
        <p className="eyebrow">Leitura em português</p>
        <Markdown
          remarkPlugins={[remarkGfm]}
          components={{
            pre({ children, ...props }) {
              const fonte = fonteMermaid(children);
              if (fonte) return <Fluxograma fonte={fonte} />;
              return <pre {...props}>{children}</pre>;
            },
          }}
        >
          {doc.body_md}
        </Markdown>
        <p style={{ color: "var(--texto-secundario)", fontSize: "0.86rem", marginTop: "1rem" }}>
          Leitura clínica em português produzida pelo CorVIA a partir das fontes referenciadas. Quando houver obra externa protegida, esta camada é síntese original e não republicação integral do texto-fonte.
        </p>
      </div>

      {doc.source_refs.length > 0 && (
        <div className="cartao" style={{ marginTop: "1rem", maxWidth: "72ch" }}>
          <p className="eyebrow">Fontes</p>
          <ul style={{ margin: "0.4rem 0 0", paddingLeft: "1.1rem", fontSize: "0.88rem" }}>
            {doc.source_refs.map((r) => <li key={r}>{r}</li>)}
          </ul>
        </div>
      )}

      <TudoSobreEsteTema
        tema={doc.theme}
        excluirTipo={doc.kind === "fluxograma" ? "fluxograma" : "documento"}
        excluirSlug={slug}
      />

      <GrafoRelacionados
        entityType={doc.kind === "fluxograma" ? "fluxograma" : "documento"}
        slug={slug}
      />
    </article>
  );
}
