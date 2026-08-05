import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, Vazio } from "../components/Estado";
import { rotuloClasseCurto, rotuloNivel } from "../lib/evidencia";

type Item = {
  slug: string;
  statement: string;
  summary: string;
  recommendation_class: string;
  evidence_level: string;
  society: string;
  year: number;
  theme: string;
  source_url: string | null;
  doi: string | null;
};

const COR_CLASSE: Record<string, { fundo: string; texto: string }> = {
  I: { fundo: "var(--primaria)", texto: "var(--branco)" },
  IIa: { fundo: "var(--acento)", texto: "var(--branco)" },
  IIb: { fundo: "var(--acento-claro)", texto: "var(--primaria)" },
  III: { fundo: "var(--alerta)", texto: "var(--branco)" },
};
const COR_CLASSE_PADRAO = { fundo: "var(--fundo)", texto: "var(--texto)" };

export default function Evidencias() {
  const [temas, setTemas] = useState<{ theme: string; count: number }[]>([]);
  const [tema, setTema] = useState("");
  const [busca, setBusca] = useState("");
  const [itens, setItens] = useState<Item[] | null>(null);

  useEffect(() => {
    api.get<{ theme: string; count: number }[]>("/evidence/themes").then(setTemas);
  }, []);

  useEffect(() => {
    setItens(null);
    const atraso = setTimeout(() => {
      const qs = new URLSearchParams({ limit: "200" });
      if (tema) qs.set("theme", tema);
      if (busca.trim()) qs.set("q", busca.trim());
      api.get<{ items: Item[] }>(`/evidence?${qs}`).then((r) => setItens(r.items));
    }, 250);
    return () => clearTimeout(atraso);
  }, [tema, busca]);

  return (
    <>
      <p className="eyebrow">Evidências</p>
      <h1>Banco de recomendações</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "68ch" }}>
        Recomendações pontuais com resumo clínico, classe, nível de evidência e
        acesso verificável ao documento de origem.
      </p>

      <input
        value={busca}
        onChange={(e) => setBusca(e.target.value)}
        placeholder="Buscar recomendação, diretriz ou assunto…"
        aria-label="Buscar evidência"
        style={{ maxWidth: 520, marginTop: "0.8rem" }}
      />

      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", margin: "0.8rem 0 1.2rem" }}>
        <button
          className={`botao ${tema ? "botao--secundario" : ""}`}
          style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
          onClick={() => setTema("")}
        >
          Todos
        </button>
        {temas.map((t) => (
          <button
            key={t.theme}
            className={`botao ${tema === t.theme ? "" : "botao--secundario"}`}
            style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
            onClick={() => setTema(t.theme)}
          >
            {t.theme} ({t.count})
          </button>
        ))}
      </div>

      {itens === null ? (
        <Carregando />
      ) : itens.length === 0 ? (
        <Vazio titulo="Nenhuma evidência encontrada" acao="Tente outro termo ou tema." />
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.7rem" }}>
          {itens.map((e) => (
            <article key={e.slug} className="cartao" style={{ display: "flex", gap: 12, alignItems: "start" }}>
              <span className="selo" style={{
                background: (COR_CLASSE[e.recommendation_class] ?? COR_CLASSE_PADRAO).fundo,
                color: (COR_CLASSE[e.recommendation_class] ?? COR_CLASSE_PADRAO).texto,
                minWidth: 46,
                textAlign: "center",
                flexShrink: 0,
              }}>
                {rotuloClasseCurto(e.recommendation_class)}
              </span>
              <div style={{ minWidth: 0, flex: 1 }}>
                <p className="eyebrow" style={{ margin: 0 }}>
                  {e.society} {e.year} · {rotuloNivel(e.evidence_level)} · {e.theme}
                </p>
                <h2 style={{ fontSize: "1rem", margin: "0.35rem 0" }}>{e.statement}</h2>
                <p style={{ color: "var(--texto-secundario)", margin: "0.35rem 0 0.6rem", lineHeight: 1.5 }}>
                  {e.summary}
                </p>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  <Link className="botao botao--secundario" to={`/evidencias/${e.slug}`}>
                    Ver análise completa
                  </Link>
                  {e.source_url && (
                    <a
                      className="botao botao--secundario"
                      href={e.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Abrir documento original ↗
                    </a>
                  )}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </>
  );
}
