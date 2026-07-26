import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, Vazio } from "../components/Estado";

type Item = { slug: string; name: string; category: string; theme: string; tags: string[] };

const RÓTULO_CATEGORIA: Record<string, string> = {
  laboratorial: "Laboratorial", metodo_grafico: "Método gráfico", imagem: "Imagem",
};

export default function Exames() {
  const [categorias, setCategorias] = useState<{ category: string; count: number }[]>([]);
  const [categoria, setCategoria] = useState("");
  const [busca, setBusca] = useState("");
  const [itens, setItens] = useState<Item[] | null>(null);

  useEffect(() => {
    api.get<{ category: string; count: number }[]>("/lab-tests/categories").then(setCategorias);
  }, []);

  useEffect(() => {
    setItens(null);
    const atraso = setTimeout(() => {
      const qs = new URLSearchParams();
      if (categoria) qs.set("category", categoria);
      if (busca.trim()) qs.set("q", busca.trim());
      api.get<{ items: Item[] }>(`/lab-tests?${qs}`).then((r) => setItens(r.items));
    }, 250);
    return () => clearTimeout(atraso);
  }, [categoria, busca]);

  return (
    <>
      <p className="eyebrow">Exames</p>
      <h1>Marcadores e exames cardiológicos</h1>
      <p style={{ color: "var(--cinza-texto)", maxWidth: "60ch" }}>
        Biomarcadores, testes funcionais e exames eletrofisiológicos — indicação, interpretação e limitações.
      </p>

      <input
        value={busca}
        onChange={(e) => setBusca(e.target.value)}
        placeholder="Buscar — ex.: troponina, BNP, teste ergométrico…"
        aria-label="Buscar exame"
        style={{ maxWidth: 420, marginTop: "0.8rem" }}
      />

      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", margin: "0.8rem 0 1.2rem" }}>
        <button className={`botao ${categoria ? "botao--secundario" : ""}`}
                style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
                onClick={() => setCategoria("")}>
          Todos
        </button>
        {categorias.map((c) => (
          <button key={c.category}
                  className={`botao ${categoria === c.category ? "" : "botao--secundario"}`}
                  style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
                  onClick={() => setCategoria(c.category)}>
            {RÓTULO_CATEGORIA[c.category] ?? c.category} ({c.count})
          </button>
        ))}
      </div>

      {itens === null ? (
        <Carregando />
      ) : itens.length === 0 ? (
        <Vazio titulo="Nenhum exame encontrado" acao="Tente outro termo ou categoria." />
      ) : (
        <div className="grade grade--2">
          {itens.map((t) => (
            <Link key={t.slug} to={`/exames/${t.slug}`} className="cartao" style={{ textDecoration: "none" }}>
              <p className="eyebrow">{RÓTULO_CATEGORIA[t.category] ?? t.category}</p>
              <strong>{t.name}</strong>
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
