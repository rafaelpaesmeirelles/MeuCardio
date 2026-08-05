import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, Erro, Vazio } from "../components/Estado";

type Item = {
  slug: string; title: string; modality: string; theme: string;
  file_path: string; thumbnail_path: string | null; tags: string[];
};

export default function Galeria() {
  const [params, setParams] = useSearchParams();
  const modalidade = params.get("modalidade") ?? "";
  const [modalidades, setModalidades] = useState<{ modality: string; count: number }[]>([]);
  const [busca, setBusca] = useState("");
  const [itens, setItens] = useState<Item[] | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.get<{ modality: string; count: number }[]>("/gallery/modalities")
      .then(setModalidades)
      .catch(() => setModalidades([]));
  }, []);

  useEffect(() => {
    setItens(null);
    setErro("");
    let ativo = true;
    const atraso = setTimeout(() => {
      const qs = new URLSearchParams();
      if (modalidade) qs.set("modality", modalidade);
      if (busca.trim()) qs.set("q", busca.trim());
      qs.set("limit", "500");
      api.get<{ items: Item[] }>(`/gallery/images?${qs}`)
        .then((r) => { if (ativo) setItens(r.items); })
        .catch((causa) => { if (ativo) setErro(causa instanceof Error ? causa.message : "Não foi possível carregar as imagens."); });
    }, 250);
    return () => { ativo = false; clearTimeout(atraso); };
  }, [modalidade, busca]);

  return (
    <>
      <p className="eyebrow">Galeria</p>
      <h1>Achados de imagem em cardiologia</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "60ch" }}>
        ECG, ecocardiograma, TC, RM, radiografia e cateterismo — imagens de fonte aberta,
        com origem e licença sempre indicadas.
      </p>

      <input
        value={busca}
        onChange={(e) => setBusca(e.target.value)}
        placeholder="Buscar por achado — ex.: fibrilação atrial, tamponamento…"
        aria-label="Buscar imagem"
        style={{ maxWidth: 420, marginTop: "0.8rem" }}
      />

      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", margin: "0.8rem 0 1.2rem" }}>
        <button
          className={`botao ${modalidade ? "botao--secundario" : ""}`}
          style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
          onClick={() => setParams({})}
        >
          Todas
        </button>
        {modalidades.map((m) => (
          <button
            key={m.modality}
            className={`botao ${modalidade === m.modality ? "" : "botao--secundario"}`}
            style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
            onClick={() => setParams({ modalidade: m.modality })}
          >
            {m.modality} ({m.count})
          </button>
        ))}
      </div>

      {erro ? (
        <Erro mensagem={`${erro} Atualize a página; se a falha persistir, o sistema registrará o erro para diagnóstico.`} />
      ) : itens === null ? (
        <Carregando />
      ) : itens.length === 0 ? (
        <Vazio
          titulo="Nenhuma imagem encontrada"
          acao={busca || modalidade ? "Tente outro termo ou modalidade." : "A galeria ainda está vazia."}
        />
      ) : (
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))",
          gap: "0.7rem",
        }}>
          {itens.map((img) => (
            <Link
              key={img.slug}
              to={`/galeria/${img.slug}`}
              className="cartao"
              style={{ padding: 0, overflow: "hidden", textDecoration: "none" }}
            >
              <img
                src={img.thumbnail_path ?? img.file_path}
                alt={img.title}
                loading="lazy"
                style={{ width: "100%", aspectRatio: "4/3", objectFit: "cover", display: "block" }}
              />
              <div style={{ padding: "0.5rem 0.6rem" }}>
                <p className="eyebrow" style={{ margin: 0 }}>{img.modality}</p>
                <strong style={{ fontSize: "0.88rem", lineHeight: 1.3 }}>{img.title}</strong>
              </div>
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
