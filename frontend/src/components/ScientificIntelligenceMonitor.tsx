import { lazy, Suspense, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import { intelligenceHealthLabel, scientificDate, scientificSourceUrl, type IntelligenceStatus } from "../lib/scientificIntelligence";
import Icone from "./Icone";
const ScientificReadingAccess = lazy(() => import("./ScientificReadingAccess"));
import "../styles/scientific-intelligence-monitor.css";

export default function ScientificIntelligenceMonitor({ compact = false }: { compact?: boolean }) {
  const { usuario } = useAuth();
  const [status, setStatus] = useState<IntelligenceStatus | null>(null);
  const [error, setError] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    setStatus(null); setError(false);
    api.get<IntelligenceStatus>("/guideline-updates/status").then(value => {
      if (active) setStatus(value);
    }).catch(() => { if (active) setError(true); });
    return () => { active = false; };
  }, [usuario?.id, attempt]);
  const coverage = status?.coverage;
  const documents = status?.document_processing;
  const sourcesOk = coverage ? coverage.direct_sources_ok + coverage.structured_ok : null;
  const sourcesTotal = coverage ? coverage.direct_sources_total + coverage.structured_total : null;
  const sourcesFailed = coverage ? coverage.direct_sources_failed + coverage.structured_failed : null;
  const recent = status?.recent_discoveries.slice(0, compact ? 3 : 12) ?? [];
  return <section className={`scientific-intelligence-monitor${compact ? " is-compact" : ""}`} aria-label={compact ? "CorVIA Intelligence" : "Estado do monitoramento científico"}>
    <header><h3><Icone nome="sincronizar" /> {compact ? "CorVIA Intelligence" : "Monitoramento científico mundial"}</h3>
      {compact && <Link to="/intelligence">Abrir monitor <Icone nome="seta" /></Link>}
    </header>
    <p>Novas publicações de sociedades, periódicos e indexadores científicos conectados ao CorVIA.</p>
    {error ? <div role="status"><p>Não foi possível confirmar o estado do monitoramento agora.</p><button type="button" onClick={() => setAttempt(value => value + 1)}>Tentar novamente</button></div>
      : !status ? <p role="status">Consultando o monitoramento…</p>
        : <>
          <p className={`scientific-intelligence-monitor__health is-${status.enabled ? status.health : "inactive"}`} role="status">{intelligenceHealthLabel(status)}</p>
          <p>Consultas a cada <strong>{status.cadence_hours} hora{status.cadence_hours === 1 ? "" : "s"}</strong>.
            {status.cadence_hours === 1 ? " Frequência intensificada neste período." : " Frequência intensificada para 1 hora em períodos de maior atividade científica."}
            {status.high_frequency_window && <> {status.high_frequency_window}.</>}
          </p>
          <dl>
            <div><dt>Última consulta concluída</dt><dd>{scientificDate(status.last_completed_at)}</dd></div>
            {!compact && <div><dt>Última consulta bem-sucedida</dt><dd>{scientificDate(status.last_success_at)}</dd></div>}
            <div><dt>Próxima consulta prevista</dt><dd>{status.next_run_at ? scientificDate(status.next_run_at) : "Aguardando confirmação do agendamento"}</dd></div>
          </dl>
          {coverage && <p>{sourcesOk} de {sourcesTotal} fontes consultadas com sucesso{sourcesFailed ? ` · ${sourcesFailed} com pendência` : ""} na última execução.</p>}
          {status.analysis_status && ["rate_limited", "unavailable", "partial"].includes(status.analysis_status) && <p>
            {status.analysis_status === "rate_limited" ? "A elaboração das sínteses está temporariamente limitada." : status.analysis_status === "unavailable" ? "A análise por IA está indisponível no momento." : "Algumas publicações ainda têm análise pendente."}
            {" "}As descobertas bibliográficas permanecem disponíveis abaixo.
          </p>}
          {!compact && <p>{status.total_discovered} publicações identificadas no monitor · {status.pending_analysis} aguardando análise.</p>}
          {documents && <div className="scientific-intelligence-monitor__documents">
            <h4>Originais e leitura em português</h4>
            <p>{documents.ready_original} originais disponíveis · {documents.ready_full_pt} traduções integrais do texto prontas.</p>
            {!compact && <>
              <p>{documents.total} fontes registradas · {documents.queued} em fila ou processamento.</p>
              <p>{documents.health === "active" ? "Processamento documental ativo." : documents.health === "inactive" ? "Processamento documental sem atividade recente confirmada." : "Aguardando confirmação do processamento documental."}</p>
              {!!documents.budget_wait && <p>{documents.budget_wait} fontes aguardam saldo ou autorização para processamento.</p>}
              {!!(documents.blocked_license + documents.blocked_fulltext) && <p>{documents.blocked_license} fontes aguardam confirmação da licença · {documents.blocked_fulltext} sem texto integral compatível disponível.</p>}
              {!!documents.failed && <p>{documents.failed} fontes precisam de verificação antes de prosseguir.</p>}
              <p>Resumo, tradução integral do texto e original são compartilhados entre os conteúdos relacionados. A disponibilidade depende da fonte e da conclusão do processamento.</p>
            </>}
          </div>}
          <h4>Descobertas recentes</h4>
          {recent.length ? <ul>{recent.map(item => {
            const url = scientificSourceUrl(item);
            return <li key={item.id} id={compact ? undefined : `descoberta-${item.id}`}>
              <small>{item.org}{item.published_at ? ` · Publicado em ${scientificDate(item.published_at)}` : ""}</small>
              {compact ? <Link to={`/intelligence#descoberta-${item.id}`}>{item.title}</Link> : <strong>{item.title}</strong>}
              {!compact && <><small>Identificado em {scientificDate(item.discovered_at)}</small>
                {url && <a href={url} target="_blank" rel="noopener noreferrer">Abrir publicação original ↗</a>}
                {item.slug && <Suspense fallback={<p role="status">Carregando opções de leitura…</p>}><ScientificReadingAccess entityType="descoberta" slug={item.slug} lazy /></Suspense>}</>}
            </li>;
          })}</ul> : <p>Nenhuma descoberta recente registrada.</p>}
          {!compact && <p className="scientific-intelligence-monitor__note">A identificação de uma publicação não implica validação clínica. As sínteses disponíveis e suas fontes aparecem abaixo.</p>}
          <button type="button" className="scientific-intelligence-monitor__refresh" onClick={() => setAttempt(value => value + 1)}>Atualizar estado</button>
        </>}
  </section>;
}
