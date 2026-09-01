import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando } from "../components/Estado";
import { areaDaCardiologia } from "../lib/taxonomiaCardiologia";
import {
  ClinicalContextLink,
  ClinicalEmpty,
  ClinicalMetric,
  ClinicalPageHeader,
  ClinicalSection,
} from "../components/ClinicalCommandPrimitives";

type Item = { slug: string; title: string; study_type: string; journal: string; year: number; theme: string };
type Tipo = { study_type: string; count: number };
type Tema = { theme: string; count: number };

const ROTULO_TIPO: Record<string, string> = {
  ensaio_clinico: "Ensaio clínico",
  revisao_sistematica: "Revisão sistemática",
  revisao_narrativa: "Revisão narrativa",
  metanalise: "Metanálise",
  consenso: "Consenso",
  coorte: "Coorte",
  caso_controle: "Caso-controle",
  estudo_de_coorte: "Estudo observacional",
  estudo_ecologico_descritivo: "Estudo ecológico descritivo",
  estudo_transversal: "Estudo transversal",
  registro_prospectivo: "Registro prospectivo",
  coorte_retrospectiva: "Coorte retrospectiva",
};

function humanizarTipo(valor: string) {
  if (ROTULO_TIPO[valor]) return ROTULO_TIPO[valor];
  const legivel = valor.replaceAll("_", " ").replaceAll("-", " ").trim();
  return legivel ? legivel.charAt(0).toLocaleUpperCase("pt-BR") + legivel.slice(1) : "Outro desenho";
}

export default function Estudos() {
  const [tipos, setTipos] = useState<Tipo[]>([]);
  const [tipo, setTipo] = useState("");
  const [temas, setTemas] = useState<Tema[]>([]);
  const [tema, setTema] = useState("");
  const [area, setArea] = useState("");
  const [busca, setBusca] = useState("");
  const [itens, setItens] = useState<Item[] | null>(null);
  const [totalEncontrados, setTotalEncontrados] = useState(0);
  const [nextOffset, setNextOffset] = useState<number | null>(null);
  const [carregandoMais, setCarregandoMais] = useState(false);
  const requisicao = useRef(0);

  useEffect(() => {
    Promise.all([
      api.get<Tipo[]>("/studies/types"),
      api.get<Tema[]>("/studies/themes"),
    ]).then(([tiposResposta, temasResposta]) => {
      setTipos(tiposResposta);
      setTemas(temasResposta);
    });
  }, []);

  useEffect(() => {
    const id = ++requisicao.current;
    setItens(null);
    setTotalEncontrados(0);
    setNextOffset(null);
    setCarregandoMais(false);
    const atraso = setTimeout(() => {
      const qs = new URLSearchParams();
      if (tipo) qs.set("study_type", tipo);
      if (tema) qs.set("theme", tema);
      if (busca.trim()) qs.set("q", busca.trim());
      qs.set("limit", "500");
      api.get<{ total: number; next_offset: number | null; items: Item[] }>(`/studies?${qs}`).then((r) => {
        if (requisicao.current !== id) return;
        setItens(r.items);
        setTotalEncontrados(r.total);
        setNextOffset(r.next_offset);
      });
    }, 250);
    return () => clearTimeout(atraso);
  }, [tipo, tema, busca]);

  async function carregarMais() {
    if (!itens || carregandoMais || nextOffset == null) return;
    const id = requisicao.current;
    setCarregandoMais(true);
    const qs = new URLSearchParams({ limit: "500", offset: String(nextOffset) });
    if (tipo) qs.set("study_type", tipo);
    if (tema) qs.set("theme", tema);
    if (busca.trim()) qs.set("q", busca.trim());
    try {
      const pagina = await api.get<{ total: number; next_offset: number | null; items: Item[] }>(`/studies?${qs}`);
      if (requisicao.current !== id) return;
      setItens((atuais) => [...(atuais ?? []), ...pagina.items]);
      setTotalEncontrados(pagina.total);
      setNextOffset(pagina.next_offset);
    } finally {
      if (requisicao.current === id) setCarregandoMais(false);
    }
  }

  useEffect(() => {
    // "Área da Cardiologia" é uma taxonomia composta no cliente. Enquanto o
    // backend não recebe esse agrupamento, percorremos as páginas restantes ao
    // selecionar uma área para não produzir um falso “nenhum resultado” com
    // base apenas nos 500 primeiros estudos.
    if (area && itens && nextOffset != null && !carregandoMais) {
      void carregarMais();
    }
    // `carregarMais` usa o cursor e o id da requisição corrente; incluí-la na
    // lista recriaria o efeito em todo render sem alterar esse contrato.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [area, itens?.length, nextOffset, carregandoMais]);

  const areas = useMemo(() => {
    const agrupadas = new Map<string, { id: string; label: string; count: number }>();
    temas.forEach((item) => {
      const encontrada = areaDaCardiologia(item.theme);
      const atual = agrupadas.get(encontrada.id);
      agrupadas.set(encontrada.id, { id: encontrada.id, label: encontrada.label, count: (atual?.count ?? 0) + item.count });
    });
    return [...agrupadas.values()].sort((a, b) => a.label.localeCompare(b.label, "pt-BR"));
  }, [temas]);

  const visiveis = useMemo(() => {
    if (!itens) return null;
    return itens.filter((item) => !area || areaDaCardiologia(item.theme, item.title).id === area);
  }, [itens, area]);

  const totalCatalogo = useMemo(() => tipos.reduce((soma, item) => soma + item.count, 0), [tipos]);
  const desenhoMaisFrequente = useMemo(() => [...tipos].sort((a, b) => b.count - a.count)[0], [tipos]);

  return (
    <div className="cc-page cc-studies-page">
      <ClinicalPageHeader
        eyebrow="Literatura original"
        title="Estudos"
        description="Ensaios, revisões, metanálises e estudos observacionais organizados para chegar rápido ao desenho, achado e aplicação clínica."
        icon="evidencia"
        actions={[
          { to: "/evidencias", label: "Evidências", icon: "evidencia" },
          { to: "/diretrizes", label: "Guidelines", icon: "documento", tone: "primary" },
        ]}
        meta={<><span className="selo">{totalCatalogo || "—"} estudos</span><span className="selo">fontes identificadas</span></>}
      />

      <div className="cc-metrics">
        <ClinicalMetric label="Catálogo" value={totalCatalogo || "—"} detail="registros científicos" icon="evidencia" />
        <ClinicalMetric label="Desenhos" value={tipos.length || "—"} detail="tipos classificados" icon="conhecimento" />
        <ClinicalMetric label="Áreas" value={areas.length || "—"} detail="áreas da cardiologia" icon="doencas" />
        <ClinicalMetric label="Mais frequente" value={desenhoMaisFrequente ? humanizarTipo(desenhoMaisFrequente.study_type) : "—"} detail={desenhoMaisFrequente ? `${desenhoMaisFrequente.count} registros` : undefined} icon="indicadores" />
      </div>

      <ClinicalSection eyebrow="Encontrar evidência" title="Filtre o que importa" description="No mobile, filtros ficam em campos compactos em vez de ocupar a tela com dezenas de chips.">
        <div className="cc-filter-grid cc-filter-grid--4">
          <label>
            <span>Buscar estudo ou patologia</span>
            <input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Ex.: DAPA-HF, fibrilação atrial…" aria-label="Buscar estudo" />
          </label>
          <label>
            <span>Área da Cardiologia</span>
            <select value={area} onChange={(e) => setArea(e.target.value)}>
              <option value="">Todas as áreas</option>
              {areas.map((item) => <option key={item.id} value={item.id}>{item.label} ({item.count})</option>)}
            </select>
          </label>
          <label>
            <span>Patologia ou assunto</span>
            <select value={tema} onChange={(e) => setTema(e.target.value)}>
              <option value="">Todos os assuntos</option>
              {temas.map((item) => <option key={item.theme} value={item.theme}>{item.theme} ({item.count})</option>)}
            </select>
          </label>
          <label>
            <span>Desenho do estudo</span>
            <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
              <option value="">Todos os desenhos</option>
              {tipos.map((item) => <option key={item.study_type} value={item.study_type}>{humanizarTipo(item.study_type)} ({item.count})</option>)}
            </select>
          </label>
        </div>
        <div className="cc-filter-summary">
          <span>{visiveis?.length ?? "…"}{!area && itens && totalEncontrados > itens.length ? ` de ${totalEncontrados}` : ""} resultado{visiveis?.length === 1 ? "" : "s"}</span>
          {(busca || area || tema || tipo) && <button type="button" onClick={() => { setBusca(""); setArea(""); setTema(""); setTipo(""); }}>Limpar filtros</button>}
        </div>
      </ClinicalSection>

      <ClinicalSection eyebrow="Resultados" title={tipo ? humanizarTipo(tipo) : "Trabalhos científicos"} description={tema || (area ? areas.find((item) => item.id === area)?.label : "Navegue do estudo para evidências, diretrizes e contexto clínico.")}>
        {visiveis === null ? (
          <Carregando texto="Consultando literatura…" />
        ) : visiveis.length === 0 ? (
          <ClinicalEmpty title="Nenhum estudo encontrado" description="Tente outro termo ou remova um dos filtros." />
        ) : (
          <div className="cc-literature-list">
            {visiveis.map((study) => (
              <Link key={study.slug} to={`/estudos/${study.slug}`} className="cc-literature-row">
                <span className="cc-literature-row__type">{humanizarTipo(study.study_type)}</span>
                <span className="cc-literature-row__body">
                  <small>{areaDaCardiologia(study.theme, study.title).label} · {study.theme}</small>
                  <strong>{study.title}</strong>
                  <span>{study.journal || "Periódico não informado"} · {study.year || "Ano não informado"}</span>
                </span>
                <span className="cc-literature-row__open">↗</span>
              </Link>
            ))}
          </div>
        )}
        {nextOffset != null && itens && <div style={{ display: "flex", justifyContent: "center", marginTop: "1rem" }}><button type="button" className="botao botao--secundario" disabled={carregandoMais} onClick={() => void carregarMais()}>{carregandoMais ? "Carregando estudos…" : `Carregar mais · ${Math.max(totalEncontrados - itens.length, 0)} restantes`}</button></div>}
      </ClinicalSection>

      <ClinicalSection eyebrow="Conhecimento conectado" title="Do estudo à decisão">
        <div className="cc-context-grid">
          <ClinicalContextLink to="/evidencias" icon="evidencia" title="Evidências" detail="Recomendações estruturadas" />
          <ClinicalContextLink to="/diretrizes" icon="documento" title="Guidelines" detail="Documento de origem" />
          <ClinicalContextLink to="/assistente" icon="assistente" title="Assistente Clínica" detail="Comparar e discutir estudos" />
        </div>
      </ClinicalSection>
    </div>
  );
}
