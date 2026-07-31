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

// Nem toda diretriz usa a escala Classe I-III / Nível A-C da ESC/AHA: OMS, e as
// brasileiras de Chagas e de eco de estresse, usam GRADE (força forte/condicional,
// certeza alta/moderada/baixa). Sem esta distinção o selo saía "Classe Forte", que
// não existe em nenhum dos dois sistemas.
// Os dois rótulos são decididos de forma independente, porque os sistemas se
// misturam: a diretriz da SBC de Chagas, por exemplo, usa força "Forte/Ponderada"
// junto com nível de evidência A/B/C — ali o certo é "Força Forte" + "Nível B".
const CLASSES_ESC = new Set(["I", "IIa", "IIb", "III"]);
const NIVEIS_LETRA = new Set(["A", "B", "C"]);
// `evidence_level` é varchar(5) no banco, então a certeza GRADE é gravada abreviada
// ("Mod" não cabe como "Moderada"). A expansão é feita aqui, na exibição, para o
// assinante ler a palavra inteira sem exigir migração de schema.
const CERTEZA_POR_EXTENSO: Record<string, string> = {
  Alta: "alta", Mod: "moderada", Baixa: "baixa", MtBx: "muito baixa",
};
const rotuloClasse = (c: string) => (CLASSES_ESC.has(c) ? `Classe ${c}` : `Força ${c}`);
const rotuloNivel = (n: string) =>
  NIVEIS_LETRA.has(n) ? `Nível ${n}` : `Certeza ${CERTEZA_POR_EXTENSO[n] ?? n}`;

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
            {rotuloClasse(e.recommendation_class)}
          </span>
          <span className="selo" style={{ background: "var(--acento)", color: "var(--branco)" }}>
            {rotuloNivel(e.evidence_level)}
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
