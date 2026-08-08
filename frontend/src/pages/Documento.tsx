import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "../lib/api";
import { Carregando, Erro, SeloRevisao } from "../components/Estado";
import Fluxograma from "../components/Fluxograma";
import ExportarApresentacao from "../components/ExportarApresentacao";
import TudoSobreEsteTema from "../components/TudoSobreEsteTema";

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

type Doc = {
  title: string; theme: string; kind: string; body_md: string;
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

  return (
    <article style={{ maxWidth: contemFluxograma ? "100%" : "72ch", minWidth: 0 }}>
      <Link to="/biblioteca" className="eyebrow">← Biblioteca</Link>
      <p className="eyebrow" style={{ marginTop: "0.8rem" }}>{doc.theme} · {doc.kind}</p>
      <h1>{doc.title}</h1>
      <div style={{ display: "flex", gap: 8, alignItems: "center", margin: "0.5rem 0 1.2rem" }}>
        <SeloRevisao status={doc.review_status} />
        <span className="selo">versão {doc.version}</span>
      </div>

      <ExportarApresentacao slug={slug!} titulo={doc.title} />

      <div className="cartao" style={{ minWidth: 0, overflow: "visible" }}>
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
    </article>
  );
}
