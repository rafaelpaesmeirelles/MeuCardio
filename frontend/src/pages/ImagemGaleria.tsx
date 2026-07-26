import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";

type Detalhe = {
  slug: string; title: string; modality: string; theme: string;
  file_path: string; findings: string; teaching_points: string | null;
  source_name: string; source_url: string; license: string; attribution: string;
  tags: string[];
};

export default function ImagemGaleria() {
  const { slug } = useParams();
  const [img, setImg] = useState<Detalhe | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    if (!slug) return;
    api.get<Detalhe>(`/gallery/images/${slug}`)
      .then(setImg)
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar a imagem."));
  }, [slug]);

  if (erro) return <Erro mensagem={erro} />;
  if (!img) return <Carregando />;

  return (
    <>
      <Link to="/galeria" style={{ fontSize: "0.86rem" }}>← Voltar para a galeria</Link>

      <p className="eyebrow" style={{ marginTop: "0.8rem" }}>{img.modality} · {img.theme}</p>
      <h1>{img.title}</h1>

      <img
        src={img.file_path}
        alt={img.title}
        style={{ width: "100%", maxWidth: 640, borderRadius: 10, marginTop: "0.8rem" }}
      />

      <div className="cartao" style={{ marginTop: "1rem" }}>
        <p className="eyebrow">Achados</p>
        <p>{img.findings}</p>
      </div>

      {img.teaching_points && (
        <div className="cartao" style={{ marginTop: "0.8rem" }}>
          <p className="eyebrow">Pontos de ensino</p>
          <p>{img.teaching_points}</p>
        </div>
      )}

      <div className="cartao" style={{ marginTop: "0.8rem" }}>
        <p className="eyebrow">Fonte e licença</p>
        <p style={{ fontSize: "0.88rem" }}>
          {img.attribution}
          <br />
          <a href={img.source_url} target="_blank" rel="noopener noreferrer">
            {img.source_name}
          </a>
          {" · "}Licença: {img.license}
        </p>
      </div>

      {img.tags.length > 0 && (
        <div style={{ marginTop: "0.8rem", display: "flex", gap: 6, flexWrap: "wrap" }}>
          {img.tags.map((t) => (
            <span key={t} className="eyebrow" style={{
              background: "var(--cinza-fundo)", padding: "0.2rem 0.5rem", borderRadius: 4,
            }}>
              {t}
            </span>
          ))}
        </div>
      )}
    </>
  );
}
