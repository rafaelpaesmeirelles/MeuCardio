import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";
import BotaoFavorito from "../components/BotaoFavorito";
import TudoSobreEsteTema from "../components/TudoSobreEsteTema";
import GrafoRelacionados from "../components/GrafoRelacionados";

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

      <div className="acoes-linha" style={{ marginTop: "1rem", flexWrap: "wrap" }} aria-label="Opções de leitura do trabalho científico">
        <a className="btn primario" href="#resumo-corvia">Resumo CorVIA</a>
        <a className="btn" href="#leitura-portugues">Traduzido</a>
        {s.url && (
          <a className="btn" href={s.url} target="_blank" rel="noopener noreferrer">
            Original ↗
          </a>
        )}
      </div>

      <div id="resumo-corvia" className="cartao" style={{ marginTop: "1rem", scrollMarginTop: "1rem" }}>
        <p className="eyebrow">Resumo CorVIA</p>
        <p>{s.summary}</p>
      </div>

      <div id="leitura-portugues" className="cartao" style={{ marginTop: "0.8rem", scrollMarginTop: "1rem" }}>
        <p className="eyebrow">Leitura em português</p>
        <p>{s.key_findings}</p>
        <p><strong>Implicação clínica:</strong> {s.clinical_implications}</p>
        {s.limitations && <p><strong>Limitações:</strong> {s.limitations}</p>}
        <p style={{ color: "var(--texto-secundario)", marginBottom: 0 }}>
          Esta leitura em português é uma síntese clínica original do CorVIA baseada no trabalho e nas fontes científicas disponíveis. Ela não depende do Google Tradutor e não reproduz tradução integral de conteúdo protegido.
        </p>
      </div>

      <div className="cartao" style={{ marginTop: "0.8rem", fontSize: "0.86rem" }}>
        {s.doi && <div>DOI: {s.doi}</div>}
        {s.pmid && <div>PMID: {s.pmid}</div>}
        <p style={{ color: "var(--texto-secundario)", margin: "0.55rem 0 0" }}>
          O Resumo CorVIA é a versão curta. A opção Traduzido abre a leitura clínica em português dentro do próprio CorVIA; Original abre a fonte científica.
        </p>
      </div>

      <TudoSobreEsteTema tema={s.theme} excluirTipo="estudo" excluirSlug={slug} />

      <GrafoRelacionados entityType="estudo" slug={slug} />
    </>
  );
}
