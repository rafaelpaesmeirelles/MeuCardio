import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  ClinicalContextLink,
  ClinicalMetric,
  ClinicalPageHeader,
} from "../components/ClinicalCommandPrimitives";
import ClinicalText from "../components/ClinicalText";
import Icone from "../components/Icone";
import { api, ApiError } from "../lib/api";
import { rotuloClasse, rotuloClasseCurto, rotuloNivel } from "../lib/evidencia";

type Item = {
  slug: string;
  statement: string;
  summary: string;
  recommendation_class: string;
  evidence_level: string;
  society: string;
  year: number;
  theme: string;
  source_url: string | null;
  doi: string | null;
};

type Tema = { theme: string; count: number };

type Listagem = {
  total: number;
  limit: number;
  offset: number;
  next_offset: number | null;
  has_more: boolean;
  items: Item[];
};

const TAMANHO_LOTE = 24;

// Valores presentes no contrato editorial atual. A consulta continua sendo
// executada pelo backend, sem reinterpretar ou reclassificar recomendações.
const CLASSES_DISPONIVEIS = [
  "I", "IIa", "IIb", "III",
  "Forte", "Ponderada", "Ponderado", "Cond", "Fraca",
  "N/A", "2b",
] as const;

const formatarNumero = new Intl.NumberFormat("pt-BR");

function classeTone(classe: string) {
  if (classe === "I") return "is-class-i";
  if (classe === "IIa") return "is-class-iia";
  if (classe === "IIb" || classe === "2b") return "is-class-iib";
  if (classe === "III") return "is-class-iii";
  if (classe === "N/A") return "is-unclassified";
  return "is-grade";
}

function rotuloClasseLegivel(classe: string, curto = false) {
  if (classe === "N/A") return curto ? "Sem classe" : "Sem classificação formal";
  if (classe === "2b") return "Classe 2b";
  return curto ? rotuloClasseCurto(classe) : rotuloClasse(classe);
}

function rotuloNivelLegivel(nivel: string) {
  return nivel === "N/A" ? "Nível não informado" : rotuloNivel(nivel);
}

function mensagemErro(causa: unknown, fallback: string) {
  return causa instanceof ApiError || causa instanceof Error ? causa.message : fallback;
}

function EvidenceCard({ item }: { item: Item }) {
  const resumoDistinto = item.summary.trim() !== item.statement.trim();

  return (
    <article className="research-evidence-card">
      <header className="research-evidence-card__source">
        <span><Icone nome="documento" /><strong>{item.society}</strong></span>
        <time dateTime={String(item.year)}>{item.year}</time>
        <span className="research-evidence-card__theme" title={item.theme}>{item.theme}</span>
      </header>

      <div className="research-evidence-card__body">
        <Link to={`/evidencias/${item.slug}`} className="research-evidence-card__statement">
          {item.statement}
        </Link>
        {resumoDistinto && <ClinicalText compact className="research-evidence-card__summary">{item.summary}</ClinicalText>}
      </div>

      <div className="research-evidence-card__grading" aria-label="Graduação da recomendação">
        <span className={`research-evidence-grade ${classeTone(item.recommendation_class)}`}>
          <small>Classe ou força</small>
          <strong>{rotuloClasseLegivel(item.recommendation_class, true)}</strong>
        </span>
        <span className="research-evidence-grade">
          <small>Nível ou certeza</small>
          <strong>{rotuloNivelLegivel(item.evidence_level)}</strong>
        </span>
      </div>

      <footer className="research-evidence-card__footer">
        <span className="research-evidence-card__trace">
          <Icone nome={item.source_url ? "check" : "evidencia"} />
          <span>
            <strong>{item.source_url ? "Origem verificável" : "Referência no detalhe"}</strong>
            <small>{item.doi ? "DOI registrado" : "Registro editorial estruturado"}</small>
          </span>
        </span>
        <span className="research-evidence-card__actions">
          {item.source_url && (
            <a href={item.source_url} target="_blank" rel="noopener noreferrer" aria-label={`Abrir documento original de ${item.society}, ${item.year}`}>
              Fonte <Icone nome="seta" />
            </a>
          )}
          <Link to={`/evidencias/${item.slug}`}>Analisar <Icone nome="seta" /></Link>
        </span>
      </footer>
    </article>
  );
}

export default function Evidencias() {
  const [temas, setTemas] = useState<Tema[]>([]);
  const [tema, setTema] = useState("");
  const [classe, setClasse] = useState("");
  const [busca, setBusca] = useState("");
  const [itens, setItens] = useState<Item[]>([]);
  const [totalResultados, setTotalResultados] = useState(0);
  const [proximoOffset, setProximoOffset] = useState<number | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [carregandoMais, setCarregandoMais] = useState(false);
  const [erro, setErro] = useState("");
  const [erroTemas, setErroTemas] = useState("");
  const [recarregar, setRecarregar] = useState(0);
  const [recarregarTemas, setRecarregarTemas] = useState(0);
  const requisicaoAtual = useRef(0);

  useEffect(() => {
    let ativa = true;
    setErroTemas("");
    api.get<Tema[]>("/evidence/themes")
      .then((resposta) => { if (ativa) setTemas(resposta); })
      .catch((causa) => {
        if (!ativa) return;
        setTemas([]);
        setErroTemas(mensagemErro(causa, "Não foi possível carregar os temas."));
      });
    return () => { ativa = false; };
  }, [recarregarTemas]);

  useEffect(() => {
    const id = ++requisicaoAtual.current;
    setCarregandoMais(false);
    const atraso = window.setTimeout(() => {
      setCarregando(true);
      setErro("");
      const qs = new URLSearchParams({ limit: String(TAMANHO_LOTE), offset: "0" });
      if (tema) qs.set("theme", tema);
      if (classe) qs.set("recommendation_class", classe);
      if (busca.trim()) qs.set("q", busca.trim());

      api.get<Listagem>(`/evidence?${qs}`)
        .then((resposta) => {
          if (id !== requisicaoAtual.current) return;
          setItens(resposta.items);
          setTotalResultados(resposta.total);
          setProximoOffset(resposta.next_offset);
        })
        .catch((causa) => {
          if (id !== requisicaoAtual.current) return;
          setItens([]);
          setTotalResultados(0);
          setProximoOffset(null);
          setErro(mensagemErro(causa, "Não foi possível consultar as recomendações."));
        })
        .finally(() => { if (id === requisicaoAtual.current) setCarregando(false); });
    }, busca.trim() ? 280 : 0);

    return () => window.clearTimeout(atraso);
  }, [tema, classe, busca, recarregar]);

  const carregarMais = useCallback(() => {
    if (proximoOffset === null || carregandoMais) return;
    const id = requisicaoAtual.current;
    setCarregandoMais(true);
    setErro("");
    const qs = new URLSearchParams({ limit: String(TAMANHO_LOTE), offset: String(proximoOffset) });
    if (tema) qs.set("theme", tema);
    if (classe) qs.set("recommendation_class", classe);
    if (busca.trim()) qs.set("q", busca.trim());

    api.get<Listagem>(`/evidence?${qs}`)
      .then((resposta) => {
        if (id !== requisicaoAtual.current) return;
        setItens((atuais) => {
          const unicos = new Map(atuais.map((item) => [item.slug, item]));
          resposta.items.forEach((item) => unicos.set(item.slug, item));
          return [...unicos.values()];
        });
        setTotalResultados(resposta.total);
        setProximoOffset(resposta.next_offset);
      })
      .catch((causa) => {
        if (id === requisicaoAtual.current) setErro(mensagemErro(causa, "Não foi possível carregar o próximo lote."));
      })
      .finally(() => { if (id === requisicaoAtual.current) setCarregandoMais(false); });
  }, [busca, carregandoMais, classe, proximoOffset, tema]);

  const totalCatalogo = useMemo(() => temas.reduce((soma, item) => soma + item.count, 0), [temas]);
  const sociedadesVisiveis = useMemo(() => new Set(itens.map((item) => item.society).filter(Boolean)).size, [itens]);
  const maisRecente = useMemo(() => {
    const anos = itens.map((item) => item.year).filter(Boolean);
    return anos.length ? Math.max(...anos) : null;
  }, [itens]);
  const fontesVisiveis = useMemo(() => itens.filter((item) => item.source_url).length, [itens]);
  const filtrosAtivos = Boolean(busca.trim() || tema || classe);

  const limparFiltros = () => {
    setBusca("");
    setTema("");
    setClasse("");
  };

  const tentarNovamente = () => {
    setRecarregar((valor) => valor + 1);
    if (erroTemas) setRecarregarTemas((valor) => valor + 1);
  };

  return (
    <div className="cv-page research-evidence-observatory">
      <ClinicalPageHeader
        eyebrow="Pesquisa clínica · curadoria rastreável"
        title="Observatório de evidências"
        description="Recomendações estruturadas para localizar, graduar e verificar a evidência sem perder a origem científica de cada decisão."
        icon="evidencia"
        actions={[
          { to: "/estudos", label: "Estudos", icon: "conhecimento" },
          { to: "/diretrizes", label: "Diretrizes", icon: "documento", tone: "primary" },
        ]}
        meta={totalCatalogo > 0
          ? <><span className="selo">{formatarNumero.format(totalCatalogo)} recomendações</span><span className="selo">{temas.length} temas</span><span className="selo">origem rastreável</span></>
          : <span className="selo">{erroTemas ? "Acervo científico" : "Sincronizando acervo científico"}</span>}
      />

      <div className="cv-metrics research-evidence-metrics" aria-label="Resumo do acervo de evidências">
        <ClinicalMetric label="Acervo" value={totalCatalogo ? formatarNumero.format(totalCatalogo) : "—"} detail="recomendações publicadas" icon="evidencia" />
        <ClinicalMetric label="Seleção" value={carregando ? "—" : formatarNumero.format(totalResultados)} detail="resultados dos filtros" icon="filtro" />
        <ClinicalMetric label="Sociedades" value={sociedadesVisiveis || "—"} detail="no lote visível" icon="conhecimento" />
        <ClinicalMetric label="Mais recente" value={maisRecente || "—"} detail="no lote visível" icon="relogio" />
      </div>

      <section className="cv-section research-evidence-console" aria-labelledby="research-evidence-console-title">
        <div className="cv-section__heading">
          <div>
            <p className="eyebrow">Radar científico</p>
            <h2 id="research-evidence-console-title">Encontre a recomendação certa</h2>
            <p>Combine texto clínico, tema e graduação sem ocultar a proveniência.</p>
          </div>
          {filtrosAtivos && <button type="button" className="research-evidence-clear" onClick={limparFiltros}><Icone nome="fechar" />Limpar filtros</button>}
        </div>

        <div className="research-evidence-filter-grid">
          <label className="research-evidence-search">
            <span>Recomendação, diretriz ou assunto</span>
            <div><Icone nome="busca" /><input type="search" value={busca} onChange={(evento) => setBusca(evento.target.value)} placeholder="Ex.: anticoagulação, ICFER, hipertensão…" autoComplete="off" spellCheck={false} /></div>
          </label>
          <label>
            <span>Tema clínico</span>
            <select value={tema} onChange={(evento) => setTema(evento.target.value)}>
              <option value="">Todos os temas{totalCatalogo ? ` (${formatarNumero.format(totalCatalogo)})` : ""}</option>
              {temas.map((item) => <option key={item.theme} value={item.theme}>{item.theme} ({formatarNumero.format(item.count)})</option>)}
            </select>
          </label>
          <label>
            <span>Classe ou força</span>
            <select value={classe} onChange={(evento) => setClasse(evento.target.value)}>
              <option value="">Todas as graduações</option>
              {CLASSES_DISPONIVEIS.map((item) => <option key={item} value={item}>{rotuloClasseLegivel(item)}</option>)}
            </select>
          </label>
          <div className="research-evidence-result" role="status" aria-live="polite">
            <strong>{carregando ? "…" : formatarNumero.format(totalResultados)}</strong>
            <span>{totalResultados === 1 ? "resultado" : "resultados"}</span>
          </div>
        </div>

        {erroTemas && <p className="research-evidence-facet-warning" role="status"><Icone nome="notificacao" /> Os temas não puderam ser sincronizados. A busca textual e a graduação continuam disponíveis.</p>}

        <div className="research-evidence-trustline" aria-label="Como ler cada registro">
          <span><i aria-hidden="true">01</i><strong>Graduação</strong><small>Classe ou força publicada</small></span>
          <span><i aria-hidden="true">02</i><strong>Certeza</strong><small>Nível ou certeza reportada</small></span>
          <span><i aria-hidden="true">03</i><strong>Proveniência</strong><small>Sociedade, ano e fonte original</small></span>
        </div>
      </section>

      <section className="cv-section research-evidence-map" aria-labelledby="research-evidence-map-title" aria-busy={carregando}>
        <div className="cv-section__heading research-evidence-map__heading">
          <div>
            <p className="eyebrow">Mapa de recomendações</p>
            <h2 id="research-evidence-map-title">{tema || "Todas as áreas clínicas"}</h2>
            <p>{filtrosAtivos ? "Seleção construída pelos filtros ativos." : "O acervo é revelado em lotes para preservar velocidade e legibilidade."}</p>
          </div>
          {!carregando && itens.length > 0 && <span className="research-evidence-visible">{formatarNumero.format(itens.length)} de {formatarNumero.format(totalResultados)} visíveis · {fontesVisiveis} com acesso direto</span>}
        </div>

        {carregando ? (
          <div className="research-evidence-loading" role="status" aria-live="polite">
            <span aria-hidden="true"><i /><i /><i /></span>
            <strong>Sincronizando o observatório…</strong>
            <small>Organizando recomendações, graduação e proveniência.</small>
          </div>
        ) : erro && itens.length === 0 ? (
          <div className="research-evidence-state research-evidence-state--error" role="alert">
            <Icone nome="sincronizar" />
            <div><strong>Não foi possível abrir o acervo</strong><p>{erro}</p></div>
            <button type="button" onClick={tentarNovamente}>Tentar novamente</button>
          </div>
        ) : itens.length === 0 ? (
          <div className="research-evidence-state">
            <Icone nome="busca" />
            <div><strong>Nenhuma recomendação encontrada</strong><p>{filtrosAtivos ? "Ajuste os filtros ou tente outra expressão clínica." : "Nenhuma recomendação está disponível neste momento."}</p></div>
            {filtrosAtivos && <button type="button" onClick={limparFiltros}>Remover filtros</button>}
          </div>
        ) : (
          <>
            <div className="research-evidence-grid">{itens.map((item) => <EvidenceCard key={item.slug} item={item} />)}</div>
            <div className="research-evidence-pagination" aria-live="polite">
              <span>Exibindo <strong>{formatarNumero.format(itens.length)}</strong> de <strong>{formatarNumero.format(totalResultados)}</strong></span>
              {erro && <small role="alert">{erro}</small>}
              {proximoOffset !== null && <button type="button" onClick={carregarMais} disabled={carregandoMais}>{carregandoMais ? "Carregando próximo lote…" : "Revelar mais recomendações"}<Icone nome={carregandoMais ? "sincronizar" : "adicionar"} /></button>}
            </div>
          </>
        )}
      </section>

      <section className="cv-section research-evidence-context" aria-labelledby="research-evidence-context-title">
        <div className="cv-section__heading"><div><p className="eyebrow">Conhecimento conectado</p><h2 id="research-evidence-context-title">Da recomendação ao contexto</h2><p>Continue pela literatura, documento de origem ou aplicação clínica.</p></div></div>
        <div className="cv-context-grid">
          <ClinicalContextLink to="/estudos" icon="conhecimento" title="Estudos" detail="Literatura que sustenta a decisão" />
          <ClinicalContextLink to="/diretrizes" icon="documento" title="Diretrizes" detail="Documento e sociedade de origem" />
          <ClinicalContextLink to="/assistente" icon="assistente" title="Apoio CorVIA" detail="Discutir aplicação no contexto" />
        </div>
      </section>
    </div>
  );
}
