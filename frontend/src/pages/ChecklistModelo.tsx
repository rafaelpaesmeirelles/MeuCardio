import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import GrafoRelacionados from "../components/GrafoRelacionados";
import { Carregando, Erro } from "../components/Estado";
import ClinicalUpdates, { type ClinicalUpdate } from "../components/ClinicalUpdates";
import { api } from "../lib/api";

type Item = {
  id: string;
  texto: string;
  categoria?: string;
  obrigatorio?: boolean;
  origem_secao?: string;
};
type Checklist = {
  slug: string;
  condicao: string;
  resumo: string | null;
  theme: string | null;
  documento_origem: string | null;
  itens: Item[];
  clinical_updates?: ClinicalUpdate[];
};

export default function ChecklistModelo() {
  const { slug = "" } = useParams();
  const navigate = useNavigate();
  const [modelo, setModelo] = useState<Checklist | null>(null);
  const [erro, setErro] = useState("");
  const [erroAcao, setErroAcao] = useState("");
  const [iniciando, setIniciando] = useState(false);
  const slugAtual = useRef(slug);

  useEffect(() => {
    slugAtual.current = slug;
    let ativo = true;
    setModelo(null);
    setErro("");
    setErroAcao("");
    setIniciando(false);
    api.get<Checklist>(`/checklists/${slug}`)
      .then((dados) => { if (ativo) setModelo(dados); })
      .catch((e) => {
        if (ativo) setErro(e?.message || "Não foi possível carregar o checklist.");
      });
    return () => { ativo = false; };
  }, [slug]);

  async function iniciar() {
    if (!modelo || iniciando) return;
    const identificacao = window.prompt(
      "Identificação desta alta (opcional — leito, iniciais ou referência do caso):",
    );
    if (identificacao === null) return;
    setIniciando(true);
    setErroAcao("");
    const slugSolicitado = modelo.slug;
    try {
      const resposta = await api.post<{ id: number }>("/checklists/aplicacoes", {
        checklist_slug: modelo.slug,
        identificacao_livre: identificacao || null,
      });
      if (slugAtual.current === slugSolicitado) {
        navigate(`/checklists/alta/${resposta.id}`);
      }
    } catch (e: any) {
      if (slugAtual.current === slugSolicitado) {
        setErroAcao(e?.message || "Não foi possível iniciar este checklist.");
      }
    } finally {
      if (slugAtual.current === slugSolicitado) setIniciando(false);
    }
  }

  if (erro) return <Erro mensagem={erro} />;
  if (!modelo || modelo.slug !== slug) return <Carregando />;

  return (
    <article>
      <p><Link to="/checklists">← Checklists de alta</Link></p>
      <p className="eyebrow">{modelo.theme || "Checklist clínico"}</p>
      <h1>{modelo.condicao}</h1>
      {modelo.resumo && <p className="subtitulo">{modelo.resumo}</p>}
      <button className="botao botao--acao" onClick={iniciar} disabled={iniciando}>
        {iniciando ? "Iniciando…" : "Usar nesta alta"}
      </button>
      {erroAcao && <p className="erro">{erroAcao}</p>}

      <section className="cartao" style={{ marginTop: "0.8rem" }}>
        <h2>Itens do modelo</h2>
        <ul>
          {modelo.itens.map((item) => (
            <li key={item.id}>
              {item.texto}{item.obrigatorio ? " — obrigatório" : ""}
              {item.origem_secao && <small style={{ display: "block" }}>Origem: {item.origem_secao}</small>}
            </li>
          ))}
        </ul>
      </section>

      <ClinicalUpdates updates={modelo.clinical_updates} />

      {modelo.documento_origem && (
        <p><Link to={`/biblioteca/${modelo.documento_origem}`}>Ver protocolo de origem</Link></p>
      )}

      <GrafoRelacionados entityType="checklist" slug={modelo.slug} />
    </article>
  );
}
