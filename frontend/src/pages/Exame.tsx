import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";
import BotaoFavorito from "../components/BotaoFavorito";
import TudoSobreEsteTema from "../components/TudoSobreEsteTema";
import GrafoRelacionados from "../components/GrafoRelacionados";

type Detalhe = {
  id: number; slug: string; name: string; category: string; theme: string;
  what_it_measures: string; reference_range: string | null;
  indications: string; interpretation: string; limitations: string | null;
  source_refs: string[];
};

const RÓTULO_CATEGORIA: Record<string, string> = {
  laboratorial: "Laboratorial", metodo_grafico: "Método gráfico", imagem: "Imagem",
};

export default function Exame() {
  const { slug } = useParams();
  const [t, setT] = useState<Detalhe | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    if (!slug) return;
    api.get<Detalhe>(`/lab-tests/${slug}`)
      .then(setT)
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar."));
  }, [slug]);

  if (erro) return <Erro mensagem={erro} />;
  if (!t) return <Carregando />;

  return (
    <>
      <Link to="/exames" style={{ fontSize: "0.86rem" }}>← Voltar para exames</Link>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginTop: "0.8rem" }}>
        <div>
          <p className="eyebrow">{RÓTULO_CATEGORIA[t.category] ?? t.category} · {t.theme}</p>
          <h1 style={{ margin: 0 }}>{t.name}</h1>
        </div>
        <BotaoFavorito itemType="exame" itemId={t.id} />
      </div>

      <div className="cartao" style={{ marginTop: "1rem" }}>
        <p className="eyebrow">O que mede</p>
        <p>{t.what_it_measures}</p>
      </div>
      {t.reference_range && (
        <div className="cartao" style={{ marginTop: "0.8rem" }}>
          <p className="eyebrow">Valor de referência</p>
          <p>{t.reference_range}</p>
        </div>
      )}
      <div className="cartao" style={{ marginTop: "0.8rem" }}>
        <p className="eyebrow">Indicações</p>
        <p>{t.indications}</p>
      </div>
      <div className="cartao" style={{ marginTop: "0.8rem" }}>
        <p className="eyebrow">Interpretação</p>
        <p>{t.interpretation}</p>
      </div>
      {t.limitations && (
        <div className="cartao" style={{ marginTop: "0.8rem" }}>
          <p className="eyebrow">Limitações</p>
          <p>{t.limitations}</p>
        </div>
      )}
      {t.source_refs.length > 0 && (
        <div className="cartao" style={{ marginTop: "0.8rem" }}>
          <p className="eyebrow">Fontes</p>
          <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "0.86rem" }}>
            {t.source_refs.map((s, i) => <li key={i}>{s}</li>)}
          </ul>
        </div>
      )}

      <TudoSobreEsteTema tema={t.theme} excluirTipo="exame" excluirSlug={slug} />

      <GrafoRelacionados entityType="exame" slug={slug} />
    </>
  );
}
