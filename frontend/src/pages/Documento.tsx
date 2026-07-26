import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "../lib/api";
import { Carregando, Erro, SeloRevisao } from "../components/Estado";

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

  return (
    <article style={{ maxWidth: "72ch" }}>
      <Link to="/biblioteca" className="eyebrow">← Biblioteca</Link>
      <p className="eyebrow" style={{ marginTop: "0.8rem" }}>{doc.theme} · {doc.kind}</p>
      <h1>{doc.title}</h1>
      <div style={{ display: "flex", gap: 8, alignItems: "center", margin: "0.5rem 0 1.2rem" }}>
        <SeloRevisao status={doc.review_status} />
        <span className="selo">versão {doc.version}</span>
      </div>
      <div className="fio-dourado" style={{ marginBottom: "1.4rem" }} />

      <div className="cartao">
        <Markdown remarkPlugins={[remarkGfm]}>{doc.body_md}</Markdown>
      </div>

      {doc.source_refs.length > 0 && (
        <div className="cartao" style={{ marginTop: "1rem" }}>
          <p className="eyebrow">Fontes</p>
          <ul style={{ margin: "0.4rem 0 0", paddingLeft: "1.1rem", fontSize: "0.88rem" }}>
            {doc.source_refs.map((r) => <li key={r}>{r}</li>)}
          </ul>
        </div>
      )}
    </article>
  );
}
