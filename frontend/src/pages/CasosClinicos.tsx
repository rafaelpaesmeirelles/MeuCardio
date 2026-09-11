import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Carregando, Erro, Vazio } from "../components/Estado";
import { api, READ_TIMEOUT_MS, type PaginaDe } from "../lib/api";
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
  const [tentativa, setTentativa] = useState(0);
  const [erroTemas, setErroTemas] = useState("");
  const [tentativaTemas, setTentativaTemas] = useState(0);
  const [carregandoMais, setCarregandoMais] = useState(false);

  useEffect(() => {
    let ativo = true;
    const controller = new AbortController();
    setErroTemas("");
    api.get<Tema[]>("/casos-clinicos/themes", { signal: controller.signal, timeoutMs: READ_TIMEOUT_MS })
      .then(resposta => { if (ativo) setTemas(resposta); })
      .catch(() => { if (ativo) setErroTemas("Não foi possível carregar os filtros de casos clínicos."); });
    return () => { ativo = false; controller.abort(); };
  }, [tentativaTemas]);

  useEffect(() => {
    let ativo = true;
    const controller = new AbortController();
    setCasos(null);
    setErro("");
    setCarregandoMais(true);
    const atraso = window.setTimeout(() => {
      const params = new URLSearchParams();
      if (busca.trim()) params.set("q", busca.trim());
      if (tema) params.set("theme", tema);
      params.set("limit", "500");
      void (async () => {
        let itens: Caso[] = [];
        let offset = 0;
        try {
          for (;;) {
            params.set("offset", String(offset));
            const pagina = await api.get<PaginaDe<Caso>>(`/casos-clinicos?${params}`, { signal: controller.signal, timeoutMs: READ_TIMEOUT_MS });
            if (!ativo) return;
            if (!Array.isArray(pagina.items)) throw new Error("A resposta de casos clínicos está incompleta. Tente novamente.");
            itens = [...itens, ...pagina.items];
            // A delayed later page must not hide cases already received.
            setCasos(itens);
            if (!pagina.has_more) break;
            if (!pagina.items.length || !Number.isSafeInteger(pagina.next_offset) || pagina.next_offset! <= offset) {
              throw new Error("Não foi possível continuar a lista de casos clínicos. Tente novamente.");
            }
            offset = pagina.next_offset!;
          }
        } catch (causa) {
          if (ativo) setErro(causa instanceof Error ? causa.message : "Não foi possível carregar os casos clínicos.");
        } finally {
          if (ativo) setCarregandoMais(false);
        }
      })();
    }, 220);
    return () => { ativo = false; window.clearTimeout(atraso); controller.abort(); };
  }, [busca, tema, tentativa]);

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

      {erroTemas && <div><Erro mensagem={erroTemas} /><button className="botao botao--secundario" type="button" onClick={() => setTentativaTemas(v => v + 1)}>Recarregar filtros</button></div>}
      {erro && <div><Erro mensagem={erro} /><button className="botao botao--secundario" type="button" onClick={() => setTentativa(v => v + 1)}>Tentar novamente</button></div>}
      {carregandoMais && casos !== null && <p role="status">Carregando os demais casos; os resultados recebidos já estão disponíveis.</p>}
      {grupos === null ? !erro && <Carregando texto="Organizando casos por área e doença…" /> : grupos.length === 0 ? (
        !carregandoMais && !erro && <Vazio titulo="Nenhum caso encontrado" acao="Tente outro termo, área ou doença." />
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
