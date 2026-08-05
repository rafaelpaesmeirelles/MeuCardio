import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, Vazio, SeloRevisao } from "../components/Estado";
import { normalizarBusca } from "../lib/taxonomiaCardiologia";

type Item = {
  slug: string; title: string; theme: string;
  summary: string | null; review_status: string;
};

export default function Fluxogramas() {
  const [params, setParams] = useSearchParams();
  const tema = params.get("tema") ?? "";
  const [busca, setBusca] = useState("");
  const [itens, setItens] = useState<Item[] | null>(null);

  useEffect(() => {
    setItens(null);
    api
      .get<{ items: Item[] }>("/library/documents?kind=fluxograma&limit=200")
      .then((r) => setItens(r.items));
  }, []);

  // Os temas vêm dos próprios fluxogramas: /library/themes conta a biblioteca
  // inteira e traria temas sem nenhum fluxograma, gerando filtro que não filtra.
  const temas = itens
    ? [...new Set(itens.map((f) => f.theme))].sort((a, b) => a.localeCompare(b, "pt-BR"))
    : [];
  const termo = normalizarBusca(busca);
  const visiveis = itens?.filter((f) => {
    if (tema && f.theme !== tema) return false;
    if (!termo) return true;
    return normalizarBusca([f.title, f.theme, f.summary ?? ""].join(" ")).includes(termo);
  }) ?? null;

  return (
    <>
      <p className="eyebrow">Fluxogramas</p>
      <h1>Fluxogramas clínicos</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "60ch" }}>
        Algoritmos visuais de investigação e tratamento, organizados por patologia
        e fundamentados nas diretrizes vigentes (ESC, AHA/ACC, SBC).
      </p>

      <div className="busca-clinica" role="search">
        <label htmlFor="busca-fluxograma">Procurar por termo específico</label>
        <input
          id="busca-fluxograma"
          type="search"
          value={busca}
          onChange={(event) => setBusca(event.target.value)}
          placeholder="Ex.: fibrilação atrial, síncope, dor torácica, anticoagulação…"
        />
        {busca && <button type="button" onClick={() => setBusca("")}>Limpar busca</button>}
      </div>

      {temas.length > 1 && (
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", margin: "0.8rem 0 1.2rem" }}>
          <button
            className={`botao ${tema ? "botao--secundario" : ""}`}
            style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
            onClick={() => setParams({})}
          >
            Todos ({itens?.length ?? 0})
          </button>
          {temas.map((t) => (
            <button
              key={t}
              className={`botao ${tema === t ? "" : "botao--secundario"}`}
              style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
              onClick={() => setParams({ tema: t })}
            >
              {t} ({itens?.filter((f) => f.theme === t).length})
            </button>
          ))}
        </div>
      )}

      {visiveis === null ? (
        <Carregando />
      ) : visiveis.length === 0 ? (
        <Vazio
          titulo={busca ? "Nenhum fluxograma corresponde à busca" : tema ? "Nenhum fluxograma neste tema" : "Nenhum fluxograma publicado ainda"}
          acao={
            busca
              ? "Tente outro termo, uma sigla ou o nome da patologia."
              : tema
              ? "Escolha outro tema ou veja todos."
              : "Os algoritmos por patologia estão em elaboração e aparecerão aqui conforme forem publicados."
          }
        />
      ) : (
        <div className="grade grade--2">
          {visiveis.map((f) => (
            <Link
              key={f.slug}
              to={`/biblioteca/${f.slug}`}
              className="cartao"
              style={{ color: "inherit" }}
            >
              <p className="eyebrow">{f.theme}</p>
              <strong>{f.title}</strong>
              {f.summary && (
                <div style={{ fontSize: "0.82rem", color: "var(--texto-secundario)", marginTop: 4 }}>
                  {f.summary}
                </div>
              )}
              <div style={{ marginTop: 8 }}>
                <SeloRevisao status={f.review_status} />
              </div>
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
