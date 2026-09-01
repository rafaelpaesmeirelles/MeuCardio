import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ClinicalMetric, ClinicalPageHeader } from "../components/ClinicalCommandPrimitives";
import Icone from "../components/Icone";
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

type EstadoTrilha = "nao_iniciada" | "em_andamento" | "concluida";

const LOTE_INICIAL = 18;

const ESTADOS: Array<{ valor: EstadoTrilha; rotulo: string }> = [
  { valor: "nao_iniciada", rotulo: "Não iniciadas" },
  { valor: "em_andamento", rotulo: "Em andamento" },
  { valor: "concluida", rotulo: "Concluídas" },
];

function estadoDaTrilha(trilha: Trilha): EstadoTrilha {
  if (trilha.total_etapas > 0 && trilha.concluidas >= trilha.total_etapas) return "concluida";
  if (trilha.concluidas > 0) return "em_andamento";
  return "nao_iniciada";
}

function percentualDaTrilha(trilha: Trilha): number {
  if (trilha.total_etapas <= 0) return 0;
  return Math.max(0, Math.min(100, Math.round((trilha.concluidas / trilha.total_etapas) * 100)));
}

function rotuloEstado(estado: EstadoTrilha): string {
  if (estado === "concluida") return "Concluída";
  if (estado === "em_andamento") return "Em andamento";
  return "Iniciar";
}

function TrilhaCard({ trilha }: { trilha: Trilha }) {
  const estado = estadoDaTrilha(trilha);
  const percentual = percentualDaTrilha(trilha);

  return (
    <Link to={`/trilhas/${trilha.slug}`} className={`learning-card learning-card--${estado}`}>
      <span className="learning-card__orbit" aria-hidden="true"><i /><i /><i /></span>
      <span className="learning-card__topline">
        <span className={`learning-status learning-status--${estado}`}><i aria-hidden="true" />{rotuloEstado(estado)}</span>
        {trilha.nivel && <small>{trilha.nivel}</small>}
      </span>
      <span className="learning-card__copy">
        <strong title={trilha.titulo}>{trilha.titulo}</strong>
        {trilha.objetivo && <p>{trilha.objetivo}</p>}
      </span>
      <span className="learning-card__progress-copy">
        <span>{trilha.concluidas} de {trilha.total_etapas} etapas</span>
        <b>{percentual}%</b>
      </span>
      <span
        className="learning-card__progress"
        role="progressbar"
        aria-label={`Progresso em ${trilha.titulo}`}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={percentual}
      >
        <i style={{ width: `${percentual}%` }} />
      </span>
      <span className="learning-card__open"><span>{estado === "nao_iniciada" ? "Abrir percurso" : "Continuar percurso"}</span><Icone nome="seta" /></span>
    </Link>
  );
}

export default function Trilhas() {
  const [trilhas, setTrilhas] = useState<Trilha[] | null>(null);
  const [busca, setBusca] = useState("");
  const [tema, setTema] = useState("");
  const [nivel, setNivel] = useState("");
  const [estado, setEstado] = useState<EstadoTrilha | "">("");
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(true);
  const [limite, setLimite] = useState(LOTE_INICIAL);

  const carregar = useCallback(() => {
    setCarregando(true);
    setErro("");
    api.get<Trilha[]>("/trilhas")
      .then(setTrilhas)
      .catch((causa) => setErro(causa instanceof Error ? causa.message : "Não foi possível carregar as trilhas de estudo."))
      .finally(() => setCarregando(false));
  }, []);

  useEffect(() => { carregar(); }, [carregar]);

  const temas = useMemo(() => {
    if (!trilhas) return [];
    const contagem = new Map<string, number>();
    trilhas.forEach((trilha) => {
      const assunto = trilha.tema || "Outros temas";
      contagem.set(assunto, (contagem.get(assunto) ?? 0) + 1);
    });
    return [...contagem.entries()].sort((a, b) => a[0].localeCompare(b[0], "pt-BR"));
  }, [trilhas]);

  const niveis = useMemo(() => {
    if (!trilhas) return [];
    return [...new Set(trilhas.map((trilha) => trilha.nivel).filter((item): item is string => Boolean(item)))]
      .sort((a, b) => a.localeCompare(b, "pt-BR"));
  }, [trilhas]);

  const filtradas = useMemo(() => {
    if (!trilhas) return [];
    const termos = normalizarBusca(busca).split(" ").filter(Boolean);
    return trilhas.filter((trilha) => {
      const assunto = trilha.tema || "Outros temas";
      if (tema && assunto !== tema) return false;
      if (nivel && trilha.nivel !== nivel) return false;
      if (estado && estadoDaTrilha(trilha) !== estado) return false;
      if (!termos.length) return true;
      const texto = normalizarBusca([trilha.titulo, assunto, trilha.objetivo ?? "", trilha.nivel ?? ""].join(" "));
      return termos.every((termo) => texto.includes(termo));
    });
  }, [trilhas, busca, tema, nivel, estado]);

  useEffect(() => { setLimite(LOTE_INICIAL); }, [busca, tema, nivel, estado]);

  const gruposVisiveis = useMemo(() => {
    const catalogo = new Map<string, Trilha[]>();
    filtradas.forEach((trilha) => {
      const assunto = trilha.tema || "Outros temas";
      catalogo.set(assunto, [...(catalogo.get(assunto) ?? []), trilha]);
    });
    const setores = [...catalogo.entries()].sort(([a], [b]) => a.localeCompare(b, "pt-BR"));
    const ordenadas: Trilha[] = [];
    const POR_SETOR = 6;
    for (let inicio = 0; ordenadas.length < filtradas.length; inicio += POR_SETOR) {
      let adicionou = false;
      for (const [, itens] of setores) {
        const lote = itens.slice(inicio, inicio + POR_SETOR);
        if (lote.length) {
          ordenadas.push(...lote);
          adicionou = true;
        }
      }
      if (!adicionou) break;
    }
    const visiveis = ordenadas.slice(0, limite);
    const grupos = new Map<string, Trilha[]>();
    visiveis.forEach((trilha) => {
      const assunto = trilha.tema || "Outros temas";
      grupos.set(assunto, [...(grupos.get(assunto) ?? []), trilha]);
    });
    return [...grupos.entries()].map(([assunto, itens]) => ({ assunto, itens, total: catalogo.get(assunto)?.length ?? itens.length }));
  }, [filtradas, limite]);

  const resumo = useMemo(() => {
    const lista = trilhas ?? [];
    return {
      total: lista.length,
      emAndamento: lista.filter((trilha) => estadoDaTrilha(trilha) === "em_andamento").length,
      concluidas: lista.filter((trilha) => estadoDaTrilha(trilha) === "concluida").length,
      etapas: lista.reduce((total, trilha) => total + Math.max(0, trilha.total_etapas), 0),
    };
  }, [trilhas]);

  const filtrosAtivos = Boolean(busca || tema || nivel || estado);
  const limparFiltros = () => { setBusca(""); setTema(""); setNivel(""); setEstado(""); };

  return (
    <div className="cv-page cv-learning-observatory">
      <ClinicalPageHeader
        eyebrow="Observatório de aprendizagem"
        title="Matriz do conhecimento"
        description="Percursos cardiológicos organizados para orientar o próximo passo, preservar contexto e tornar sua evolução visível sem interromper o raciocínio clínico."
        icon="curso"
        actions={[{ to: "/trilhas/timeline", label: "Timeline científica", icon: "relogio", tone: "primary" }]}
        meta={trilhas ? <><span className="selo">{resumo.total} trilhas</span><span className="selo">{resumo.etapas} etapas</span></> : <span className="selo">Sincronizando catálogo</span>}
      />

      <div className="cv-metrics learning-metrics" aria-label="Resumo do aprendizado">
        <ClinicalMetric label="Catálogo" value={resumo.total} detail="trilhas disponíveis" icon="conhecimento" />
        <ClinicalMetric label="Em andamento" value={resumo.emAndamento} detail="percursos ativos" icon="sincronizar" />
        <ClinicalMetric label="Concluídas" value={resumo.concluidas} detail="percursos finalizados" icon="check" />
        <ClinicalMetric label="Áreas" value={temas.length} detail="setores do conhecimento" icon="doencas" />
      </div>

      <section className="cv-section learning-console" aria-labelledby="learning-console-title">
        <div className="cv-section__heading">
          <div><p className="eyebrow">Navegação orientada</p><h2 id="learning-console-title">Encontre o próximo percurso</h2><p>Combine assunto, nível e momento da sua formação.</p></div>
          {filtrosAtivos && <button type="button" className="learning-clear" onClick={limparFiltros}><Icone nome="fechar" />Limpar filtros</button>}
        </div>
        <div className="learning-filter-grid">
          <label className="learning-search"><span>Buscar conhecimento</span><div><Icone nome="busca" /><input type="search" value={busca} onChange={(event) => setBusca(event.target.value)} placeholder="Tema, objetivo, nível ou trilha…" autoComplete="off" spellCheck={false} /></div></label>
          <label><span>Assunto</span><select value={tema} onChange={(event) => setTema(event.target.value)}><option value="">Todos ({resumo.total})</option>{temas.map(([item, contagem]) => <option key={item} value={item}>{item} ({contagem})</option>)}</select></label>
          <label><span>Nível</span><select value={nivel} onChange={(event) => setNivel(event.target.value)}><option value="">Todos</option>{niveis.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
          <label><span>Progresso</span><select value={estado} onChange={(event) => setEstado(event.target.value as EstadoTrilha | "")}><option value="">Todos</option>{ESTADOS.map((item) => <option key={item.valor} value={item.valor}>{item.rotulo}</option>)}</select></label>
          <div className="learning-result" aria-live="polite"><strong>{filtradas.length}</strong><span>{filtradas.length === 1 ? "percurso" : "percursos"}</span></div>
        </div>
      </section>

      <section className="cv-section learning-map" aria-labelledby="learning-map-title">
        <div className="cv-section__heading learning-map__heading">
          <div><p className="eyebrow">Mapa do conhecimento</p><h2 id="learning-map-title">{tema || "Todos os setores"}</h2><p>{filtrosAtivos ? "Seleção construída pelos filtros ativos." : "Exibição progressiva para manter a navegação rápida e precisa."}</p></div>
          <Link to="/trilhas/timeline" className="learning-timeline-link"><span><Icone nome="rota" /></span><span><strong>Evolução científica</strong><small>Navegar por doença e ano</small></span><Icone nome="seta" /></Link>
        </div>

        {carregando ? (
          <div className="learning-loading" role="status" aria-live="polite"><span aria-hidden="true"><i /><i /><i /></span><strong>Sincronizando matriz do conhecimento…</strong><small>Organizando seus percursos e progresso.</small></div>
        ) : erro ? (
          <div className="learning-state learning-state--error" role="alert"><Icone nome="sincronizar" /><div><strong>Não foi possível abrir o catálogo</strong><p>{erro}</p></div><button type="button" onClick={carregar}>Tentar novamente</button></div>
        ) : filtradas.length === 0 ? (
          <div className="learning-state"><Icone nome="busca" /><div><strong>Nenhum percurso encontrado</strong><p>{trilhas?.length ? "Ajuste os filtros ou tente outra expressão." : "Nenhuma trilha está disponível neste momento."}</p></div>{filtrosAtivos && <button type="button" onClick={limparFiltros}>Remover filtros</button>}</div>
        ) : (
          <>
            <div className="learning-sectors">
              {gruposVisiveis.map((grupo, indice) => (
                <section className="learning-sector" key={grupo.assunto} aria-labelledby={`learning-sector-${indice}`}>
                  <header><span className="learning-sector__node" aria-hidden="true"><i /></span><div><small>SETOR {String(indice + 1).padStart(2, "0")}</small><h3 id={`learning-sector-${indice}`}>{grupo.assunto}</h3></div><span>{grupo.itens.length} de {grupo.total} {grupo.total === 1 ? "percurso" : "percursos"}</span></header>
                  <div className="learning-grid">{grupo.itens.map((trilha) => <TrilhaCard key={trilha.slug} trilha={trilha} />)}</div>
                </section>
              ))}
            </div>
            {limite < filtradas.length && <div className="learning-more"><span>Exibindo {Math.min(limite, filtradas.length)} de {filtradas.length}</span><button type="button" onClick={() => setLimite((atual) => atual + LOTE_INICIAL)}>Revelar mais percursos<Icone nome="adicionar" /></button></div>}
          </>
        )}
      </section>
    </div>
  );
}
