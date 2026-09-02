import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Carregando, Erro, Vazio } from "../components/Estado";
import { api, todasAsPaginas } from "../lib/api";
import { areaDaCardiologia } from "../lib/taxonomiaCardiologia";

type Caso = {
  slug: string;
  titulo: string;
  tema: string | null;
  nivel: string | null;
  tentativas: number;
  acertou_na_ultima: boolean | null;
};

type Tema = { theme: string; count: number };

export default function CasosClinicos() {
  const [casos, setCasos] = useState<Caso[] | null>(null);
  const [temas, setTemas] = useState<Tema[]>([]);
  const [busca, setBusca] = useState("");
  const [tema, setTema] = useState("");
  const [area, setArea] = useState("");
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.get<Tema[]>("/casos-clinicos/themes").then(setTemas).catch(() => setTemas([]));
  }, []);

  useEffect(() => {
    let ativo = true;
    setCasos(null);
    setErro("");
    const atraso = window.setTimeout(() => {
      const params = new URLSearchParams();
      if (busca.trim()) params.set("q", busca.trim());
      if (tema) params.set("theme", tema);
      params.set("limit", "500");
      todasAsPaginas<Caso>(`/casos-clinicos?${params}`)
        .then((resposta) => { if (ativo) setCasos(resposta); })
        .catch((causa) => { if (ativo) setErro(causa instanceof Error ? causa.message : "Não foi possível carregar os casos clínicos."); });
    }, 220);
    return () => { ativo = false; window.clearTimeout(atraso); };
  }, [busca, tema]);

  const areas = useMemo(() => {
    const mapa = new Map<string, { id: string; label: string; count: number }>();
    temas.forEach((item) => {
      const encontrada = areaDaCardiologia(item.theme);
      const atual = mapa.get(encontrada.id);
      mapa.set(encontrada.id, { id: encontrada.id, label: encontrada.label, count: (atual?.count ?? 0) + item.count });
    });
    return [...mapa.values()].sort((a, b) => a.label.localeCompare(b.label, "pt-BR"));
  }, [temas]);

  const grupos = useMemo(() => {
    if (!casos) return null;
    const visiveis = casos.filter((caso) => !area || areaDaCardiologia(caso.tema, caso.titulo).id === area);
    const porArea = new Map<string, { label: string; patologias: Map<string, Caso[]> }>();
    visiveis.forEach((caso) => {
      const encontrada = areaDaCardiologia(caso.tema, caso.titulo);
      const grupoArea = porArea.get(encontrada.id) ?? { label: encontrada.label, patologias: new Map<string, Caso[]>() };
      const patologia = caso.tema || "Outros temas";
      grupoArea.patologias.set(patologia, [...(grupoArea.patologias.get(patologia) ?? []), caso]);
      porArea.set(encontrada.id, grupoArea);
    });
    return [...porArea.entries()]
      .map(([id, grupo]) => ({ id, ...grupo, patologias: [...grupo.patologias.entries()] }))
      .sort((a, b) => a.label.localeCompare(b.label, "pt-BR"));
  }, [casos, area]);

  return (
    <div>
      <p className="eyebrow">Treinamento de decisão</p>
      <h1>Casos clínicos interativos</h1>
      <p className="subtitulo">Um caso, a sua decisão, e depois a conduta correta com a evidência que a sustenta.</p>

      <section className="filtros-conteudo filtros-conteudo--3">
        <label><strong>Buscar por tema específico</strong><input type="search" value={busca} onChange={(event) => setBusca(event.target.value)} placeholder="Ex.: fibrilação atrial, choque, valvopatia…" /></label>
        <label><strong>Área da Cardiologia</strong><select value={area} onChange={(event) => setArea(event.target.value)}><option value="">Todas as áreas</option>{areas.map((item) => <option key={item.id} value={item.id}>{item.label} ({item.count})</option>)}</select></label>
        <label><strong>Doença ou assunto</strong><select value={tema} onChange={(event) => setTema(event.target.value)}><option value="">Todas as doenças</option>{temas.map((item) => <option key={item.theme} value={item.theme}>{item.theme} ({item.count})</option>)}</select></label>
      </section>

      {erro ? <Erro mensagem={erro} /> : grupos === null ? <Carregando texto="Organizando casos por área e doença…" /> : grupos.length === 0 ? (
        <Vazio titulo="Nenhum caso encontrado" acao="Tente outro termo, área ou doença." />
      ) : (
        <div className="colecoes-conteudo">
          {grupos.map((grupo) => <section className="colecao-conteudo" key={grupo.id}>
            <header><div><p className="eyebrow">Área da Cardiologia</p><h2>{grupo.label}</h2></div><span>{grupo.patologias.reduce((total, [, itens]) => total + itens.length, 0)} casos</span></header>
            {grupo.patologias.map(([patologia, itens]) => <div className="casos-patologia" key={patologia}>
              <h3>{patologia}</h3>
              <div className="painel__funcoes">
                {itens.map((caso) => <Link key={caso.slug} to={`/casos-clinicos/${caso.slug}`} className="cartao painel__funcao">
                  <strong>{caso.titulo}</strong>
                  <span>{caso.nivel || "Nível não informado"}</span>
                  {caso.tentativas > 0 && <span className="dado">{caso.tentativas} tentativa{caso.tentativas > 1 ? "s" : ""}{caso.acertou_na_ultima !== null && (caso.acertou_na_ultima ? " · última: acertou" : " · última: errou")}</span>}
                </Link>)}
              </div>
            </div>)}
          </section>)}
        </div>
      )}
    </div>
  );
}
