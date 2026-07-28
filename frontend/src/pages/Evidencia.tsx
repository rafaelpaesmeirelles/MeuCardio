import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";
import BotaoFavorito from "../components/BotaoFavorito";

type Detalhe = {
  id: number; slug: string; statement: string; recommendation_class: string;
  evidence_level: string; society: string; year: number; theme: string;
  guideline_title: string; reference: string; document_slug: string | null; tags: string[];
};

export default function Evidencia() {
  const { slug } = useParams();
  const [e, setE] = useState<Detalhe | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    if (!slug) return;
    api.get<Detalhe>(`/evidence/${slug}`).then(setE)
      .catch((err) => setErro(err instanceof ApiError ? err.message : "Não foi possível carregar."));
  }, [slug]);

  if (erro) return <Erro mensagem={erro} />;
  if (!e) return <Carregando />;

  return (
    <>
      <Link to="/evidencias" style={{ fontSize: "0.86rem" }}>← Voltar para evidências</Link>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginTop: "0.8rem" }}>
        <p className="eyebrow">{e.society} {e.year} · {e.theme}</p>
        <BotaoFavorito itemType="evidencia" itemId={e.id} />
      </div>

      <div className="cartao" style={{ marginTop: "0.4rem" }}>
        <div style={{ display: "flex", gap: 10, marginBottom: "0.6rem" }}>
          <span className="selo" style={{ background: "var(--acento)", color: "var(--branco)" }}>
            Classe {e.recommendation_class}
          </span>
          <span className="selo" style={{ background: "var(--acento)", color: "var(--branco)" }}>
            Nível {e.evidence_level}
          </span>
        </div>
        <p style={{ fontSize: "1.05rem", margin: 0 }}>{e.statement}</p>
      </div>

      <div className="cartao" style={{ marginTop: "0.8rem" }}>
        <p className="eyebrow">Diretriz de origem</p>
        <p>{e.guideline_title}</p>
      </div>

      <div className="cartao" style={{ marginTop: "0.8rem" }}>
        <p className="eyebrow">Referência completa</p>
        <p style={{ fontSize: "0.88rem" }}>{e.reference}</p>
      </div>

      {e.document_slug && (
        <Link to={`/biblioteca/${e.document_slug}`} className="botao botao--secundario"
              style={{ display: "inline-block", marginTop: "0.8rem" }}>
          Ver documento relacionado na Biblioteca
        </Link>
      )}
    </>
  );
}
