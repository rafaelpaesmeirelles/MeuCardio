import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando } from "../components/Estado";
import {
  ClinicalContextLink,
  ClinicalEmpty,
  ClinicalMetric,
  ClinicalPageHeader,
  ClinicalSection,
} from "../components/ClinicalCommandPrimitives";

type Item = { slug: string; name: string; category: string; theme: string; tags: string[] };
type PaginaExames = { total: number; next_offset: number | null; items: Item[] };
type Taxonomia = {
  category: string;
  count: number;
  subtypes: { theme: string; count: number }[];
};

const ROTULO_CATEGORIA: Record<string, string> = {
  laboratorial: "Laboratorial",
  metodo_grafico: "Método gráfico",
  imagem: "Imagem",
};

function rotuloTipo(valor: string) {
  const base = ROTULO_CATEGORIA[valor] ?? valor.replaceAll("_", " ");
  return base.charAt(0).toLocaleUpperCase("pt-BR") + base.slice(1);
}

export default function Exames() {
  const [params, setParams] = useSearchParams();
  const categoria = params.get("tipo") ?? "";
  const subtipo = params.get("subtipo") ?? "";
  const [taxonomia, setTaxonomia] = useState<Taxonomia[]>([]);
  const [busca, setBusca] = useState(params.get("q") ?? "");
  const [itens, setItens] = useState<Item[] | null>(null);
  const [totalEncontrados, setTotalEncontrados] = useState(0);
  const [nextOffset, setNextOffset] = useState<number | null>(null);
  const [carregandoMais, setCarregandoMais] = useState(false);
  const requisicao = useRef(0);

  useEffect(() => {
    api.get<Taxonomia[]>("/lab-tests/taxonomy").then(setTaxonomia);
  }, []);

  useEffect(() => {
    const id = ++requisicao.current;
    setItens(null);
    setTotalEncontrados(0);
    setNextOffset(null);
    setCarregandoMais(false);
    const atraso = setTimeout(() => {
      const qs = new URLSearchParams({ limit: "200" });
      if (categoria) qs.set("category", categoria);
      if (subtipo) qs.set("theme", subtipo);
      if (busca.trim()) qs.set("q", busca.trim());
      api.get<PaginaExames>(`/lab-tests?${qs}`).then((r) => {
        if (requisicao.current !== id) return;
        setItens(r.items);
        setTotalEncontrados(r.total);
        setNextOffset(r.next_offset);
      });

      const url = new URLSearchParams();
      if (categoria) url.set("tipo", categoria);
      if (subtipo) url.set("subtipo", subtipo);
      if (busca.trim()) url.set("q", busca.trim());
      setParams(url, { replace: true });
    }, 250);
    return () => clearTimeout(atraso);
  }, [categoria, subtipo, busca, setParams]);

  async function carregarMais() {
    if (nextOffset == null || carregandoMais) return;
    const id = requisicao.current;
    setCarregandoMais(true);
    const qs = new URLSearchParams({ limit: "200", offset: String(nextOffset) });
    if (categoria) qs.set("category", categoria);
    if (subtipo) qs.set("theme", subtipo);
    if (busca.trim()) qs.set("q", busca.trim());
    try {
      const pagina = await api.get<PaginaExames>(`/lab-tests?${qs}`);
      if (requisicao.current !== id) return;
      setItens((atuais) => [...(atuais ?? []), ...pagina.items]);
      setTotalEncontrados(pagina.total);
      setNextOffset(pagina.next_offset);
    } finally {
      if (requisicao.current === id) setCarregandoMais(false);
    }
  }

  const subtiposDisponiveis = useMemo(() => {
    if (categoria) return taxonomia.find((tipo) => tipo.category === categoria)?.subtypes ?? [];
    const contagens = new Map<string, number>();
    taxonomia.forEach((tipo) => tipo.subtypes.forEach((item) => {
      contagens.set(item.theme, (contagens.get(item.theme) ?? 0) + item.count);
    }));
    return [...contagens.entries()]
      .map(([theme, count]) => ({ theme, count }))
      .sort((a, b) => a.theme.localeCompare(b.theme, "pt-BR"));
  }, [taxonomia, categoria]);

  const grupos = useMemo(() => {
    const mapa = new Map<string, Item[]>();
    for (const item of itens ?? []) {
      const chave = `${item.category}|||${item.theme}`;
      mapa.set(chave, [...(mapa.get(chave) ?? []), item]);
    }
    return [...mapa.entries()].sort(([a], [b]) => a.localeCompare(b, "pt-BR"));
  }, [itens]);

  const total = useMemo(() => taxonomia.reduce((soma, tipo) => soma + tipo.count, 0), [taxonomia]);
  const totalSubtipos = useMemo(() => new Set(taxonomia.flatMap((tipo) => tipo.subtypes.map((item) => item.theme))).size, [taxonomia]);

  function alterarCategoria(valor: string) {
    const proximo = new URLSearchParams(params);
    if (valor) proximo.set("tipo", valor); else proximo.delete("tipo");
    proximo.delete("subtipo");
    setParams(proximo);
  }

  function alterarSubtipo(valor: string) {
    const proximo = new URLSearchParams(params);
    if (valor) proximo.set("subtipo", valor); else proximo.delete("subtipo");
    setParams(proximo);
  }

  return (
    <div className="cc-page cc-exams-page">
      <ClinicalPageHeader
        eyebrow="Diagnóstico e monitorização"
        title="Exames"
        description="Marcadores, métodos gráficos e imagem organizados para chegar da indicação à interpretação, limitações e conexões clínicas."
        icon="clinica"
        actions={[
          { to: "/documentos", label: "Solicitar exames", icon: "documento", tone: "primary" },
          { to: "/assistente", label: "Discutir contexto", icon: "assistente" },
        ]}
        meta={<><span className="selo">{total || "—"} exames</span><span className="selo">interpretação estruturada</span></>}
      />

      <div className="cc-metrics">
        <ClinicalMetric label="Catálogo" value={total || "—"} detail="exames e marcadores" icon="clinica" />
        <ClinicalMetric label="Tipos" value={taxonomia.length || "—"} detail="grandes categorias" icon="documento" />
        <ClinicalMetric label="Subtipos" value={totalSubtipos || "—"} detail="áreas diagnósticas" icon="evidencia" />
        <ClinicalMetric label="Seleção" value={itens?.length ?? "…"} detail={itens && totalEncontrados > itens.length ? `de ${totalEncontrados} resultados` : "resultados atuais"} icon="busca" />
      </div>

      <ClinicalSection eyebrow="Encontrar exame" title="Do nome ao contexto diagnóstico" description="Filtros compactos preservam a área de leitura e funcionam melhor no celular.">
        <div className="cc-filter-grid cc-filter-grid--3">
          <label>
            <span>Nome, tipo ou assunto</span>
            <input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Ex.: NT-proBNP, ecocardiograma, isquemia…" aria-label="Buscar exame" />
          </label>
          <label>
            <span>Tipo</span>
            <select value={categoria} onChange={(e) => alterarCategoria(e.target.value)}>
              <option value="">Todos os tipos</option>
              {taxonomia.map((tipo) => <option key={tipo.category} value={tipo.category}>{rotuloTipo(tipo.category)} ({tipo.count})</option>)}
            </select>
          </label>
          <label>
            <span>Subtipo</span>
            <select value={subtipo} onChange={(e) => alterarSubtipo(e.target.value)}>
              <option value="">Todos os subtipos</option>
              {subtiposDisponiveis.map((item) => <option key={item.theme} value={item.theme}>{item.theme} ({item.count})</option>)}
            </select>
          </label>
        </div>
        <div className="cc-filter-summary"><span>{itens?.length ?? "…"}{itens && totalEncontrados > itens.length ? ` de ${totalEncontrados}` : ""} resultados</span>{(busca || categoria || subtipo) && <button type="button" onClick={() => { setBusca(""); setParams(new URLSearchParams(), { replace: true }); }}>Limpar filtros</button>}</div>
      </ClinicalSection>

      <ClinicalSection eyebrow="Catálogo" title={subtipo || (categoria ? rotuloTipo(categoria) : "Marcadores e exames cardiológicos")} description="Abra um item para revisar indicação, interpretação, limitações e fontes.">
        {itens === null ? (
          <Carregando texto="Consultando exames…" />
        ) : itens.length === 0 ? (
          <ClinicalEmpty title="Nenhum exame encontrado" description="Tente outro termo, tipo ou subtipo." />
        ) : (
          <div className="cc-exam-groups">
            {grupos.map(([chave, exames]) => {
              const [tipo, tema] = chave.split("|||");
              return (
                <section key={chave} className="cc-exam-group">
                  <div className="cc-exam-group__heading"><div><p className="eyebrow">{rotuloTipo(tipo)}</p><h3>{tema}</h3></div><span>{exames.length}</span></div>
                  <div className="cc-exam-grid">
                    {exames.map((exame) => (
                      <Link key={exame.slug} to={`/exames/${exame.slug}`} className="cc-exam-card">
                        <small>{rotuloTipo(exame.category)} · {exame.theme}</small>
                        <strong>{exame.name}</strong>
                        {exame.tags.length > 0 && <span>{exame.tags.slice(0, 3).join(" · ")}</span>}
                        <i>↗</i>
                      </Link>
                    ))}
                  </div>
                </section>
              );
            })}
          </div>
        )}
        {nextOffset != null && <div style={{ display: "flex", justifyContent: "center", marginTop: "1rem" }}><button type="button" className="botao botao--secundario" disabled={carregandoMais} onClick={() => void carregarMais()}>{carregandoMais ? "Carregando exames…" : `Carregar mais · ${Math.max(totalEncontrados - (itens?.length ?? 0), 0)} restantes`}</button></div>}
      </ClinicalSection>

      <ClinicalSection eyebrow="Conhecimento conectado" title="Do exame à decisão">
        <div className="cc-context-grid">
          <ClinicalContextLink to="/documentos" icon="documento" title="Solicitar exames" detail="Transformar decisão em pedido" />
          <ClinicalContextLink to="/doencas" icon="doencas" title="Guia de Doenças" detail="Interpretar dentro da doença" />
          <ClinicalContextLink to="/evidencias" icon="evidencia" title="Evidências" detail="Recomendações de uso" />
        </div>
      </ClinicalSection>
    </div>
  );
}
