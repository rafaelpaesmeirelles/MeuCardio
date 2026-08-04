import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, Vazio } from "../components/Estado";

type Item = { slug: string; name: string; category: string; theme: string; tags: string[] };
type Taxonomia = {
  category: string;
  count: number;
  subtypes: { theme: string; count: number }[];
};

const RÓTULO_CATEGORIA: Record<string, string> = {
  laboratorial: "Laboratorial",
  metodo_grafico: "Método gráfico",
  imagem: "Imagem",
};

function rotuloTipo(valor: string) {
  return RÓTULO_CATEGORIA[valor] ?? valor.replaceAll("_", " ");
}

export default function Exames() {
  const [params, setParams] = useSearchParams();
  const categoria = params.get("tipo") ?? "";
  const subtipo = params.get("subtipo") ?? "";
  const [taxonomia, setTaxonomia] = useState<Taxonomia[]>([]);
  const [busca, setBusca] = useState(params.get("q") ?? "");
  const [itens, setItens] = useState<Item[] | null>(null);

  useEffect(() => {
    api.get<Taxonomia[]>("/lab-tests/taxonomy").then(setTaxonomia);
  }, []);

  useEffect(() => {
    setItens(null);
    const atraso = setTimeout(() => {
      const qs = new URLSearchParams({ limit: "200" });
      if (categoria) qs.set("category", categoria);
      if (subtipo) qs.set("theme", subtipo);
      if (busca.trim()) qs.set("q", busca.trim());
      api.get<{ items: Item[] }>(`/lab-tests?${qs}`).then((r) => setItens(r.items));

      const url = new URLSearchParams();
      if (categoria) url.set("tipo", categoria);
      if (subtipo) url.set("subtipo", subtipo);
      if (busca.trim()) url.set("q", busca.trim());
      setParams(url, { replace: true });
    }, 250);
    return () => clearTimeout(atraso);
  }, [categoria, subtipo, busca, setParams]);

  const subtiposDisponiveis = useMemo(() => {
    if (categoria) return taxonomia.find((tipo) => tipo.category === categoria)?.subtypes ?? [];
    const contagens = new Map<string, number>();
    taxonomia.forEach((tipo) => tipo.subtypes.forEach((item) => {
      contagens.set(item.theme, (contagens.get(item.theme) ?? 0) + item.count);
    }));
    return [...contagens.entries()]
      .map(([theme, count]) => ({ theme, count }))
      .sort((a, b) => a.theme.localeCompare(b.theme, "pt-BR"));
  }, [taxonomia, categoria]);

  const grupos = useMemo(() => {
    const mapa = new Map<string, Item[]>();
    for (const item of itens ?? []) {
      const chave = `${item.category}|||${item.theme}`;
      mapa.set(chave, [...(mapa.get(chave) ?? []), item]);
    }
    return [...mapa.entries()].sort(([a], [b]) => a.localeCompare(b, "pt-BR"));
  }, [itens]);

  function escolherTipo(valor: string) {
    const proximo = new URLSearchParams(params);
    if (valor) proximo.set("tipo", valor); else proximo.delete("tipo");
    proximo.delete("subtipo");
    setParams(proximo);
  }

  function escolherSubtipo(valor: string) {
    const proximo = new URLSearchParams(params);
    if (valor) proximo.set("subtipo", valor); else proximo.delete("subtipo");
    setParams(proximo);
  }

  return (
    <>
      <p className="eyebrow">Exames</p>
      <h1>Marcadores e exames cardiológicos</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "68ch" }}>
        Conteúdo organizado por tipo e subtipo, com indicação, interpretação,
        limitações e fontes para cada exame.
      </p>

      <input
        value={busca}
        onChange={(e) => setBusca(e.target.value)}
        placeholder="Buscar nome, tipo, subtipo ou assunto…"
        aria-label="Buscar exame"
        style={{ maxWidth: 520, marginTop: "0.8rem" }}
      />

      <div style={{ marginTop: "0.9rem" }}>
        <p className="eyebrow" style={{ marginBottom: "0.35rem" }}>Tipo</p>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          <button
            className={`botao ${categoria ? "botao--secundario" : ""}`}
            style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
            onClick={() => escolherTipo("")}
          >
            Todos
          </button>
          {taxonomia.map((tipo) => (
            <button
              key={tipo.category}
              className={`botao ${categoria === tipo.category ? "" : "botao--secundario"}`}
              style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
              onClick={() => escolherTipo(tipo.category)}
            >
              {rotuloTipo(tipo.category)} ({tipo.count})
            </button>
          ))}
        </div>
      </div>

      {subtiposDisponiveis.length > 1 && (
        <div style={{ marginTop: "0.8rem" }}>
          <p className="eyebrow" style={{ marginBottom: "0.35rem" }}>Subtipo</p>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <button
              className={`botao ${subtipo ? "botao--secundario" : ""}`}
              style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
              onClick={() => escolherSubtipo("")}
            >
              Todos
            </button>
            {subtiposDisponiveis.map((item) => (
              <button
                key={item.theme}
                className={`botao ${subtipo === item.theme ? "" : "botao--secundario"}`}
                style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
                onClick={() => escolherSubtipo(item.theme)}
              >
                {item.theme} ({item.count})
              </button>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: "1.2rem" }}>
        {itens === null ? (
          <Carregando />
        ) : itens.length === 0 ? (
          <Vazio titulo="Nenhum exame encontrado" acao="Tente outro termo, tipo ou subtipo." />
        ) : grupos.map(([chave, exames]) => {
          const [tipo, tema] = chave.split("|||");
          return (
            <section key={chave} style={{ marginBottom: "1.3rem" }}>
              <p className="eyebrow" style={{ margin: 0 }}>{rotuloTipo(tipo)}</p>
              <h2 style={{ marginTop: "0.2rem" }}>{tema}</h2>
              <div className="grade grade--2">
                {exames.map((exame) => (
                  <Link key={exame.slug} to={`/exames/${exame.slug}`} className="cartao" style={{ textDecoration: "none" }}>
                    <p className="eyebrow">{rotuloTipo(exame.category)} · {exame.theme}</p>
                    <strong>{exame.name}</strong>
                    {exame.tags.length > 0 && (
                      <p style={{ color: "var(--texto-secundario)", fontSize: "0.8rem", marginBottom: 0 }}>
                        {exame.tags.slice(0, 4).join(" · ")}
                      </p>
                    )}
                  </Link>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </>
  );
}
