import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";
import BotaoFavorito from "../components/BotaoFavorito";

type Detalhe = {
  id: number; slug: string; title: string; study_type: string; journal: string; year: number;
  theme: string; authors: string | null; doi: string | null; pmid: string | null; url: string | null;
  summary: string; key_findings: string; clinical_implications: string; limitations: string | null;
  tags: string[];
};

export default function Estudo() {
  const { slug } = useParams();
  const [s, setS] = useState<Detalhe | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    if (!slug) return;
    api.get<Detalhe>(`/studies/${slug}`).then(setS)
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar."));
  }, [slug]);

  if (erro) return <Erro mensagem={erro} />;
  if (!s) return <Carregando />;

  return (
    <>
      <Link to="/estudos" style={{ fontSize: "0.86rem" }}>← Voltar para estudos</Link>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginTop: "0.8rem" }}>
        <div>
          <p className="eyebrow">{s.journal} · {s.year} · {s.theme}</p>
          <h1 style={{ margin: 0 }}>{s.title}</h1>
          {s.authors && <p style={{ color: "var(--texto-secundario)", marginTop: 4 }}>{s.authors}</p>}
        </div>
        <BotaoFavorito itemType="estudo" itemId={s.id} />
      </div>

      <div className="cartao" style={{ marginTop: "1rem" }}>
        <p className="eyebrow">Resumo</p>
        <p>{s.summary}</p>
      </div>
      <div className="cartao" style={{ marginTop: "0.8rem" }}>
        <p className="eyebrow">Principais achados</p>
        <p>{s.key_findings}</p>
      </div>
      <div className="cartao" style={{ marginTop: "0.8rem" }}>
        <p className="eyebrow">Implicação clínica</p>
        <p>{s.clinical_implications}</p>
      </div>
      {s.limitations && (
        <div className="cartao" style={{ marginTop: "0.8rem" }}>
          <p className="eyebrow">Limitações</p>
          <p>{s.limitations}</p>
        </div>
      )}

      <div className="cartao" style={{ marginTop: "0.8rem", fontSize: "0.86rem" }}>
        {s.doi && <div>DOI: {s.doi}</div>}
        {s.pmid && <div>PMID: {s.pmid}</div>}
        {s.url && <a href={s.url} target="_blank" rel="noopener noreferrer">Ver publicação original</a>}
      </div>
    </>
  );
}
