import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, SeloRevisao, Vazio } from "../components/Estado";

type Doc = {
  slug: string; title: string; kind: string; theme: string;
  summary: string | null; review_status: string;
};

export default function Biblioteca() {
  const [params, setParams] = useSearchParams();
  const tema = params.get("tema") ?? "";
  const [temas, setTemas] = useState<{ theme: string; count: number }[]>([]);
  const [docs, setDocs] = useState<Doc[] | null>(null);

  useEffect(() => {
    api.get<{ theme: string; count: number }[]>("/library/themes").then(setTemas);
  }, []);

  useEffect(() => {
    setDocs(null);
    const q = tema ? `?theme=${encodeURIComponent(tema)}` : "";
    api.get<{ items: Doc[] }>(`/library/documents${q}`).then((r) => setDocs(r.items));
  }, [tema]);

  return (
    <>
      <p className="eyebrow">Biblioteca científica</p>
      <h1>{tema || "Todos os temas"}</h1>

      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", margin: "0.8rem 0 1.2rem" }}>
        <button
          className={`botao ${tema ? "botao--secundario" : ""}`}
          style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
          onClick={() => setParams({})}
        >
          Tudo
        </button>
        {temas.map((t) => (
          <button
            key={t.theme}
            className={`botao ${tema === t.theme ? "" : "botao--secundario"}`}
            style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
            onClick={() => setParams({ tema: t.theme })}
          >
            {t.theme}
          </button>
        ))}
      </div>

      {docs === null ? (
        <Carregando />
      ) : docs.length === 0 ? (
        <Vazio titulo="Nenhum documento neste tema" acao="Importe conteúdo pelo painel de administração." />
      ) : (
        <div className="grade grade--2">
          {docs.map((d) => (
            <Link key={d.slug} to={`/biblioteca/${d.slug}`} className="cartao" style={{ color: "inherit" }}>
              <p className="eyebrow">{d.kind}</p>
              <h3>{d.title}</h3>
              {d.summary && (
                <p style={{ color: "var(--cinza-texto)", fontSize: "0.88rem" }}>{d.summary}</p>
              )}
              <SeloRevisao status={d.review_status} />
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
