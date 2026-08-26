import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import GrafoRelacionados from "../components/GrafoRelacionados";
import { Carregando, Erro } from "../components/Estado";
import { api } from "../lib/api";

type Secao = { titulo?: string; paragrafos?: string[]; itens?: string[] };
type Material = {
  slug: string;
  titulo: string;
  subtitulo: string | null;
  tema: string;
  resumo: string | null;
  documento_slug: string | null;
  secoes: Secao[];
  sinais_de_alerta: string[];
  perguntas: string[];
  fontes: string[];
};

export default function MaterialPacienteDetalhe() {
  const { slug = "" } = useParams();
  const [material, setMaterial] = useState<Material | null>(null);
  const [erro, setErro] = useState("");
  const [erroDownload, setErroDownload] = useState("");
  const [baixando, setBaixando] = useState(false);
  const slugAtual = useRef(slug);

  useEffect(() => {
    slugAtual.current = slug;
    let ativo = true;
    setMaterial(null);
    setErro("");
    setErroDownload("");
    setBaixando(false);
    api.get<Material>(`/material-paciente/${slug}`)
      .then((dados) => { if (ativo) setMaterial(dados); })
      .catch((e) => {
        if (ativo) setErro(e?.message || "Não foi possível carregar o material.");
      });
    return () => { ativo = false; };
  }, [slug]);

  async function baixar() {
    if (!material) return;
    setBaixando(true);
    setErroDownload("");
    const slugSolicitado = material.slug;
    try {
      const blob = await api.blob(`/material-paciente/${material.slug}/pdf`);
      if (slugAtual.current !== slugSolicitado) return;
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${material.slug}-material-do-paciente.pdf`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (e: any) {
      if (slugAtual.current === slugSolicitado) {
        setErroDownload(e?.message || "Não foi possível gerar o PDF deste material.");
      }
    } finally {
      if (slugAtual.current === slugSolicitado) setBaixando(false);
    }
  }

  if (erro) return <Erro mensagem={erro} />;
  if (!material || material.slug !== slug) return <Carregando />;

  return (
    <article>
      <p><Link to="/material-paciente">← Material para o paciente</Link></p>
      <p className="eyebrow">{material.tema}</p>
      <h1>{material.titulo}</h1>
      {material.subtitulo && <p className="subtitulo">{material.subtitulo}</p>}
      {material.resumo && <p>{material.resumo}</p>}

      <button className="botao botao--acao" onClick={baixar} disabled={baixando}>
        {baixando ? "Gerando…" : "Baixar PDF para entregar"}
      </button>
      {erroDownload && <p className="erro">{erroDownload}</p>}

      {material.secoes.map((secao, indice) => (
        <section className="cartao" style={{ marginTop: "0.8rem" }} key={`${secao.titulo}-${indice}`}>
          {secao.titulo && <h2>{secao.titulo}</h2>}
          {(secao.paragrafos || []).map((paragrafo, i) => <p key={i}>{paragrafo}</p>)}
          {!!secao.itens?.length && <ul>{secao.itens.map((item, i) => <li key={i}>{item}</li>)}</ul>}
        </section>
      ))}

      {!!material.sinais_de_alerta.length && (
        <section className="cartao" style={{ marginTop: "0.8rem" }}>
          <h2>Sinais de alerta</h2>
          <ul>{material.sinais_de_alerta.map((item, i) => <li key={i}>{item}</li>)}</ul>
        </section>
      )}

      {!!material.perguntas.length && (
        <section className="cartao" style={{ marginTop: "0.8rem" }}>
          <h2>Perguntas frequentes</h2>
          <ul>{material.perguntas.map((item, i) => <li key={i}>{item}</li>)}</ul>
        </section>
      )}

      {!!material.fontes.length && (
        <section className="cartao" style={{ marginTop: "0.8rem" }}>
          <h2>Fontes</h2>
          <ul>{material.fontes.map((item, i) => <li key={i}>{item}</li>)}</ul>
        </section>
      )}

      {material.documento_slug && (
        <p><Link to={`/biblioteca/${material.documento_slug}`}>Ver conteúdo técnico de origem</Link></p>
      )}

      <GrafoRelacionados entityType="material_paciente" slug={material.slug} />
    </article>
  );
}
