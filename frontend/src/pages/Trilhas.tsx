import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Carregando, Erro, Vazio } from "../components/Estado";
import { api } from "../lib/api";
import { normalizarBusca } from "../lib/taxonomiaCardiologia";

type Trilha = {
  slug: string;
  titulo: string;
  tema: string | null;
  objetivo: string | null;
  nivel: string | null;
  total_etapas: number;
  concluidas: number;
  finalizada_em: string | null;
};

export default function Trilhas() {
  const [trilhas, setTrilhas] = useState<Trilha[] | null>(null);
  const [busca, setBusca] = useState("");
  const [tema, setTema] = useState("");
  const [erro, setErro] = useState("");

  useEffect(() => {
    setErro("");
    api.get<Trilha[]>("/trilhas")
      .then(setTrilhas)
      .catch((causa) => setErro(causa instanceof Error ? causa.message : "Não foi possível carregar as trilhas de estudo."));
  }, []);

  const temas = useMemo(() => {
    if (!trilhas) return [];
    return [...new Set(trilhas.map((trilha) => trilha.tema || "Outros temas"))].sort((a, b) => a.localeCompare(b, "pt-BR"));
  }, [trilhas]);

  const grupos = useMemo(() => {
    if (!trilhas) return null;
    const termo = normalizarBusca(busca);
    const visiveis = trilhas.filter((trilha) => {
      const assunto = trilha.tema || "Outros temas";
      if (tema && assunto !== tema) return false;
      if (!termo) return true;
      return normalizarBusca([trilha.titulo, assunto, trilha.objetivo ?? "", trilha.nivel ?? ""].join(" ")).includes(termo);
    });
    return [...new Set(visiveis.map((trilha) => trilha.tema || "Outros temas"))]
      .sort((a, b) => a.localeCompare(b, "pt-BR"))
      .map((assunto) => ({ assunto, itens: visiveis.filter((trilha) => (trilha.tema || "Outros temas") === assunto) }));
  }, [trilhas, busca, tema]);

  return (
    <div>
      <p className="eyebrow">Aprendizado guiado</p>
      <h1>Trilhas de estudo</h1>
      <p className="subtitulo">Sequências guiadas do conteúdo que já está na plataforma. Cada etapa explica por que vem naquele ponto — a trilha organiza, não repete.</p>

      <section className="filtros-conteudo">
        <label><strong>Buscar por tema específico</strong><input type="search" value={busca} onChange={(event) => setBusca(event.target.value)} placeholder="Ex.: insuficiência cardíaca, ECG, cardiopatias congênitas…" /></label>
        <label><strong>Assunto</strong><select value={tema} onChange={(event) => setTema(event.target.value)}><option value="">Todos os assuntos</option>{temas.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
      </section>

      {erro ? <Erro mensagem={erro} /> : grupos === null ? <Carregando texto="Carregando o catálogo de trilhas…" /> : grupos.length === 0 ? (
        <Vazio titulo="Nenhuma trilha encontrada" acao={trilhas?.length ? "Tente outro termo ou assunto." : "Nenhuma trilha revisada está disponível."} />
      ) : (
        <div className="colecoes-conteudo">
          {grupos.map((grupo) => <section className="colecao-conteudo" key={grupo.assunto}>
            <header><div><p className="eyebrow">Assunto</p><h2>{grupo.assunto}</h2></div><span>{grupo.itens.length} {grupo.itens.length === 1 ? "trilha" : "trilhas"}</span></header>
            <div className="painel__funcoes">
              {grupo.itens.map((trilha) => {
                const percentual = trilha.total_etapas ? Math.round((trilha.concluidas / trilha.total_etapas) * 100) : 0;
                return <Link key={trilha.slug} to={`/trilhas/${trilha.slug}`} className="cartao painel__funcao">
                  <strong>{trilha.titulo}</strong>
                  <span>{trilha.objetivo}</span>
                  <span className="trilha__barra" aria-label={`${percentual}% concluído`}><span style={{ width: `${percentual}%` }} /></span>
                  <span className="dado">{trilha.concluidas}/{trilha.total_etapas} etapas{trilha.finalizada_em && " · concluída"}{trilha.nivel && ` · ${trilha.nivel}`}</span>
                </Link>;
              })}
            </div>
          </section>)}
        </div>
      )}
    </div>
  );
}
