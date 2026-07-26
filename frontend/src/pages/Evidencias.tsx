import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, Vazio } from "../components/Estado";

type Item = {
  slug: string; statement: string; recommendation_class: string;
  evidence_level: string; society: string; year: number; theme: string;
};

const COR_CLASSE: Record<string, string> = {
  I: "var(--bordo)", IIa: "var(--dourado)", IIb: "#b8860b", III: "var(--alerta)",
};

export default function Evidencias() {
  const [temas, setTemas] = useState<{ theme: string; count: number }[]>([]);
  const [tema, setTema] = useState("");
  const [busca, setBusca] = useState("");
  const [itens, setItens] = useState<Item[] | null>(null);

  useEffect(() => { api.get<{ theme: string; count: number }[]>("/evidence/themes").then(setTemas); }, []);

  useEffect(() => {
    setItens(null);
    const atraso = setTimeout(() => {
      const qs = new URLSearchParams();
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
      <p style={{ color: "var(--cinza-texto)", maxWidth: "60ch" }}>
        Recomendações pontuais com classe e nível de evidência, extraídas das diretrizes vigentes.
      </p>

      <input value={busca} onChange={(e) => setBusca(e.target.value)}
             placeholder="Buscar recomendação…" aria-label="Buscar evidência"
             style={{ maxWidth: 420, marginTop: "0.8rem" }} />

      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", margin: "0.8rem 0 1.2rem" }}>
        <button className={`botao ${tema ? "botao--secundario" : ""}`}
                style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }} onClick={() => setTema("")}>
          Todos
        </button>
        {temas.map((t) => (
          <button key={t.theme} className={`botao ${tema === t.theme ? "" : "botao--secundario"}`}
                  style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }} onClick={() => setTema(t.theme)}>
            {t.theme} ({t.count})
          </button>
        ))}
      </div>

      {itens === null ? (
        <Carregando />
      ) : itens.length === 0 ? (
        <Vazio titulo="Nenhuma evidência encontrada" acao="Tente outro termo ou tema." />
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
          {itens.map((e) => (
            <Link key={e.slug} to={`/evidencias/${e.slug}`} className="cartao"
                  style={{ textDecoration: "none", display: "flex", gap: 12, alignItems: "start" }}>
              <span className="selo" style={{
                background: COR_CLASSE[e.recommendation_class] ?? "var(--cinza-fundo)",
                color: "#fff", minWidth: 46, textAlign: "center", flexShrink: 0,
              }}>
                {e.recommendation_class}
              </span>
              <div>
                <p className="eyebrow" style={{ margin: 0 }}>
                  {e.society} {e.year} · Nível {e.evidence_level} · {e.theme}
                </p>
                <span>{e.statement}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
