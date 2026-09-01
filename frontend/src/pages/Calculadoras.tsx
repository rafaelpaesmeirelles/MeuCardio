import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, SeloRevisao } from "../components/Estado";
import {
  ClinicalContextLink,
  ClinicalEmpty,
  ClinicalMetric,
  ClinicalPageHeader,
  ClinicalSection,
} from "../components/ClinicalCommandPrimitives";

type Calc = { slug: string; name: string; theme: string; purpose: string; status: string; kind: string };

const PREFIXO_DOSE = "Doses — ";

function normalizarBusca(valor: string): string {
  return valor.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR").replace(/\s+/g, " ").trim();
}

function CalculadoraCard({ c }: { c: Calc }) {
  const liberada = c.status === "implementada";
  const corpo = (
    <>
      <span className="cv-tool-card__icon">∑</span>
      <span className="cv-tool-card__copy">
        <small>{c.theme}</small>
        <strong>{c.name}</strong>
        <p>{c.purpose}</p>
      </span>
      {!liberada ? <SeloRevisao status={c.status} /> : <span className="cv-tool-card__open" aria-hidden="true">↗</span>}
    </>
  );
  return liberada ? <Link to={`/calculadoras/${c.slug}`} className="cv-tool-card">{corpo}</Link> : <div className="cv-tool-card is-disabled" aria-disabled="true">{corpo}</div>;
}

export default function Calculadoras() {
  const [lista, setLista] = useState<Calc[] | null>(null);
  const [busca, setBusca] = useState("");
  const [tema, setTema] = useState("");

  useEffect(() => { api.get<Calc[]>("/calculators").then(setLista); }, []);

  const temas = useMemo(() => {
    const contagem = new Map<string, number>();
    (lista || []).forEach((c) => contagem.set(c.theme, (contagem.get(c.theme) ?? 0) + 1));
    return [...contagem.entries()].sort((a, b) => a[0].localeCompare(b[0], "pt-BR"));
  }, [lista]);

  const filtradas = useMemo(() => {
    const termos = normalizarBusca(busca).split(" ").filter(Boolean);
    return (lista || []).filter((c) => {
      if (tema && c.theme !== tema) return false;
      if (!termos.length) return true;
      const texto = normalizarBusca([c.name, c.theme, c.purpose].join(" "));
      return termos.every((termo) => texto.includes(termo));
    });
  }, [lista, busca, tema]);

  if (!lista) return <Carregando texto="Abrindo ferramentas clínicas…" />;

  const doses = filtradas.filter((c) => c.kind === "dose");
  const avaliacoes = filtradas.filter((c) => c.kind !== "dose");
  const implementadas = lista.filter((c) => c.status === "implementada").length;
  const dosesPorArea = new Map<string, Calc[]>();
  for (const c of doses) {
    const area = c.theme.startsWith(PREFIXO_DOSE) ? c.theme.slice(PREFIXO_DOSE.length) : c.theme;
    dosesPorArea.set(area, [...(dosesPorArea.get(area) ?? []), c]);
  }

  return (
    <div className="cv-page cv-calculators-page">
      <ClinicalPageHeader
        eyebrow="Ferramentas de decisão"
        title="Calculadoras e escores"
        description="Escores, doses e conversões clínicas com referência e limitações explícitas. Ferramentas não validadas permanecem bloqueadas."
        icon="calculadora"
        actions={[
          { to: "/assistente", label: "Assistente Clínica", icon: "assistente", tone: "primary" },
        ]}
        meta={<><span className="selo">{implementadas} disponíveis</span><span className="selo">referência rastreável</span></>}
      />

      <ClinicalSection eyebrow="Encontrar ferramenta" title="Qual cálculo você precisa agora?" className="cv-calculator-finder">
        <div className="cv-filter-grid cv-filter-grid--3">
          <label>
            <span>Nome, escore, dose ou contexto</span>
            <input type="search" value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Ex.: TIMI, TFG, noradrenalina, pediátrica…" autoComplete="off" spellCheck={false} />
          </label>
          <label>
            <span>Tema</span>
            <select value={tema} onChange={(e) => setTema(e.target.value)}>
              <option value="">Todos os temas ({lista.length})</option>
              {temas.map(([nome, contagem]) => <option key={nome} value={nome}>{nome} ({contagem})</option>)}
            </select>
          </label>
          <div className="cv-filterbar__result" aria-live="polite"><strong>{filtradas.length}</strong><span>resultado{filtradas.length === 1 ? "" : "s"}</span></div>
        </div>
        <div className="cv-filter-summary"><span>{tema || "todas as ferramentas"}</span>{(busca || tema) && <button type="button" onClick={() => { setBusca(""); setTema(""); }}>Limpar filtros</button>}</div>
      </ClinicalSection>

      <div className="cv-metrics" aria-label="Resumo do catálogo">
        <ClinicalMetric label="Ferramentas" value={lista.length} detail="catálogo total" icon="calculadora" />
        <ClinicalMetric label="Disponíveis" value={implementadas} detail="validadas para uso" icon="check" />
        <ClinicalMetric label="Temas" value={temas.length} detail="áreas clínicas" icon="clinica" />
        <ClinicalMetric label="Seleção" value={filtradas.length} detail="resultados atuais" icon="busca" />
      </div>

      {doses.length > 0 && (
        <ClinicalSection eyebrow="Dose e infusão" title="Calculadoras de doses" description="Taxa de infusão, dose ponderal e parâmetros estruturados por área. O resultado apoia; a decisão permanece do médico.">
          <div className="cv-tool-sections">
            {[...dosesPorArea.entries()].map(([area, itens]) => (
              <section key={area} className="cv-tool-group">
                <div className="cv-tool-group__heading"><h3>{area}</h3><span>{itens.length}</span></div>
                <div className="cv-tool-grid">{itens.map((c) => <CalculadoraCard key={c.slug} c={c} />)}</div>
              </section>
            ))}
          </div>
        </ClinicalSection>
      )}

      <ClinicalSection eyebrow="Escores e avaliações" title="Estratificação e apoio à decisão">
        {avaliacoes.length === 0 ? <ClinicalEmpty title="Nenhuma calculadora encontrada" description={busca ? `Sem resultado para “${busca.trim()}”.` : "Ajuste os filtros."} /> : <div className="cv-tool-grid">{avaliacoes.map((c) => <CalculadoraCard key={c.slug} c={c} />)}</div>}
      </ClinicalSection>

      <ClinicalSection eyebrow="Contexto" title="Depois do cálculo">
        <div className="cv-context-grid">
          <ClinicalContextLink to="/doencas" icon="doencas" title="Guia de Doenças" detail="Interpretar o resultado no quadro clínico" />
          <ClinicalContextLink to="/evidencias" icon="evidencia" title="Evidências" detail="Rever indicação e limitações" />
          <ClinicalContextLink to="/documentos" icon="documento" title="Documentos" detail="Levar o resultado para a ação" />
        </div>
      </ClinicalSection>
    </div>
  );
}
