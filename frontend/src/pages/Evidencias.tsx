import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando } from "../components/Estado";
import ClinicalText from "../components/ClinicalText";
import { rotuloClasseCurto, rotuloNivel } from "../lib/evidencia";
import {
  ClinicalContextLink,
  ClinicalEmpty,
  ClinicalMetric,
  ClinicalPageHeader,
  ClinicalSection,
} from "../components/ClinicalCommandPrimitives";

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

function classeTone(classe: string) {
  if (classe === "I") return "is-class-i";
  if (classe === "IIa") return "is-class-iia";
  if (classe === "IIb") return "is-class-iib";
  if (classe === "III") return "is-class-iii";
  return "";
}

export default function Evidencias() {
  const [temas, setTemas] = useState<Tema[]>([]);
  const [tema, setTema] = useState("");
  const [busca, setBusca] = useState("");
  const [itens, setItens] = useState<Item[] | null>(null);

  useEffect(() => {
    api.get<Tema[]>("/evidence/themes").then(setTemas);
  }, []);

  useEffect(() => {
    setItens(null);
    const atraso = setTimeout(() => {
      const qs = new URLSearchParams({ limit: "200" });
      if (tema) qs.set("theme", tema);
      if (busca.trim()) qs.set("q", busca.trim());
      api.get<{ items: Item[] }>(`/evidence?${qs}`).then((r) => setItens(r.items));
    }, 250);
    return () => clearTimeout(atraso);
  }, [tema, busca]);

  const total = useMemo(() => temas.reduce((soma, item) => soma + item.count, 0), [temas]);
  const sociedades = useMemo(() => new Set((itens ?? []).map((item) => item.society).filter(Boolean)).size, [itens]);
  const anos = useMemo(() => (itens ?? []).map((item) => item.year).filter(Boolean), [itens]);
  const maisRecente = anos.length ? Math.max(...anos) : null;

  return (
    <div className="cc-page cc-evidence-page">
      <ClinicalPageHeader
        eyebrow="Decisão baseada em evidências"
        title="Banco de recomendações"
        description="Recomendações pontuais com classe, nível de evidência, resumo clínico e acesso verificável ao documento de origem."
        icon="evidencia"
        actions={[
          { to: "/estudos", label: "Estudos", icon: "evidencia" },
          { to: "/diretrizes", label: "Guidelines", icon: "documento", tone: "primary" },
        ]}
        meta={<><span className="selo">{total || "—"} recomendações</span><span className="selo">origem rastreável</span></>}
      />

      <div className="cc-metrics">
        <ClinicalMetric label="Recomendações" value={total || "—"} detail="catálogo estruturado" icon="evidencia" />
        <ClinicalMetric label="Temas" value={temas.length || "—"} detail="áreas e assuntos" icon="doencas" />
        <ClinicalMetric label="Sociedades" value={sociedades || "—"} detail="na seleção atual" icon="conhecimento" />
        <ClinicalMetric label="Mais recente" value={maisRecente || "—"} detail="na seleção atual" icon="agenda" />
      </div>

      <ClinicalSection eyebrow="Encontrar recomendação" title="Pesquise sem atravessar uma parede de filtros" description="Busca e tema ficam disponíveis de forma compacta; o restante da tela é reservado para decisão clínica.">
        <div className="cc-filter-grid cc-filter-grid--3">
          <label>
            <span>Recomendação, diretriz ou assunto</span>
            <input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Ex.: anticoagulação, ICFER, hipertensão…" aria-label="Buscar evidência" />
          </label>
          <label>
            <span>Tema clínico</span>
            <select value={tema} onChange={(e) => setTema(e.target.value)}>
              <option value="">Todos os temas</option>
              {temas.map((item) => <option key={item.theme} value={item.theme}>{item.theme} ({item.count})</option>)}
            </select>
          </label>
          <div className="cc-filterbar__result">{itens?.length ?? "…"} resultado{itens?.length === 1 ? "" : "s"}</div>
        </div>
        <div className="cc-filter-summary">
          <span>{tema || "todo o catálogo"}</span>
          {(busca || tema) && <button type="button" onClick={() => { setBusca(""); setTema(""); }}>Limpar filtros</button>}
        </div>
      </ClinicalSection>

      <ClinicalSection eyebrow="Recomendações" title={tema || "O que a evidência recomenda?"} description="Abra a análise completa ou vá diretamente ao documento original quando disponível.">
        {itens === null ? (
          <Carregando texto="Consultando recomendações…" />
        ) : itens.length === 0 ? (
          <ClinicalEmpty title="Nenhuma evidência encontrada" description="Tente outro termo ou tema." />
        ) : (
          <div className="cc-recommendation-list">
            {itens.map((item) => (
              <Link key={item.slug} to={`/evidencias/${item.slug}`} className="cc-recommendation-row">
                <span className="cc-recommendation-row__copy">
                  <small>{item.society} {item.year} · {item.theme}</small>
                  <strong>{item.statement}</strong>
                  {item.summary.trim() !== item.statement.trim() && <ClinicalText compact>{item.summary}</ClinicalText>}
                </span>
                <span className="cc-recommendation-row__meta">
                  <span className={`cc-evidence-class ${classeTone(item.recommendation_class)}`}>{rotuloClasseCurto(item.recommendation_class)}</span>
                  <span>{rotuloNivel(item.evidence_level)}</span>
                  {item.doi && <span>DOI</span>}
                </span>
              </Link>
            ))}
          </div>
        )}
      </ClinicalSection>

      <ClinicalSection eyebrow="Conhecimento conectado" title="Da recomendação ao contexto">
        <div className="cc-context-grid">
          <ClinicalContextLink to="/estudos" icon="evidencia" title="Estudos" detail="Literatura que sustenta a decisão" />
          <ClinicalContextLink to="/diretrizes" icon="documento" title="Guidelines" detail="Documento e sociedade de origem" />
          <ClinicalContextLink to="/assistente" icon="assistente" title="Assistente Clínica" detail="Discutir aplicação prática" />
        </div>
      </ClinicalSection>
    </div>
  );
}
