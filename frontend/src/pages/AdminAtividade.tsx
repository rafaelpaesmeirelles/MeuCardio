import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Carregando, Erro } from "../components/Estado";
import { api } from "../lib/api";
import "../styles/admin-atividade.css";

type Period = "day" | "week" | "month" | "year";
type Metric = "registrations" | "subscriptions" | "accesses";
type Counts = {
  registrations: number | null;
  subscriptions: number | null;
  accesses: number | null;
  unique_users: number | null;
  subscriptions_partial?: boolean;
  accesses_partial?: boolean;
};
type Activity = {
  timezone: string;
  generated_at: string;
  period: Period;
  granularity: "hour" | "day" | "month";
  start: string;
  end: string;
  totals: Counts;
  series: Array<Counts & { date: string }>;
  current: Record<Period, Counts>;
  active_now: { count: number | null; window_seconds: number; available: boolean };
  coverage: {
    accesses_since: string | null;
    subscriptions_since: string | null;
    subscriptions_note: string;
    accesses_note: string;
    registrations_note?: string;
  };
};

const PERIODS: Array<{ value: Period; label: string; current: string }> = [
  { value: "day", label: "Dia", current: "Hoje" },
  { value: "week", label: "Semana", current: "Esta semana" },
  { value: "month", label: "Mês", current: "Este mês" },
  { value: "year", label: "Ano", current: "Este ano" },
];
const METRICS: Array<{ key: Metric; title: string; description: string }> = [
  { key: "registrations", title: "Novos cadastros", description: "Contas criadas no período." },
  { key: "subscriptions", title: "Novas assinaturas", description: "Primeiras ativações confirmadas pelo Stripe." },
  { key: "accesses", title: "Acessos", description: "Logins bem-sucedidos registrados no período." },
];
const numberFormat = new Intl.NumberFormat("pt-BR");
const valueText = (value: number | null | undefined) => value == null ? "—" : numberFormat.format(value);

function today() {
  const parts = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Sao_Paulo", year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(new Date());
  const part = (type: string) => parts.find((item) => item.type === type)?.value ?? "";
  return `${part("year")}-${part("month")}-${part("day")}`;
}

function dateText(value: string | null, timezone: string, options: Intl.DateTimeFormatOptions = { dateStyle: "short" }) {
  if (!value) return "não disponível";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "não disponível" : date.toLocaleString("pt-BR", { ...options, timeZone: timezone });
}

function partial(counts: Counts, metric: Metric) {
  return metric === "subscriptions" ? counts.subscriptions_partial : metric === "accesses" ? counts.accesses_partial : false;
}

function MetricValue({ counts, metric }: { counts: Counts; metric: Metric }) {
  return <>{valueText(counts[metric])}{partial(counts, metric) && <span className="admin-atividade__partial" title="Contagem parcial: o período inclui datas anteriores à coleta."> parcial</span>}</>;
}

function SeriesChart({ data, metric }: { data: Activity; metric: typeof METRICS[number] }) {
  const maximum = Math.max(1, ...data.series.map((row) => row[metric.key] ?? 0));
  const label = (value: string) => dateText(value, data.timezone,
    data.granularity === "hour" ? { hour: "2-digit", minute: "2-digit" } :
      data.granularity === "month" ? { month: "short" } : { day: "2-digit", month: "2-digit" });
  const available = data.series.some((row) => row[metric.key] !== null);
  return <section className={`admin-atividade__chart admin-atividade__chart--${metric.key}`} aria-label={`${metric.title} por ${data.granularity === "hour" ? "hora" : data.granularity === "month" ? "mês" : "dia"}`}>
    <div className="admin-atividade__chart-heading"><h3>{metric.title}</h3><small>Máx. {available ? valueText(maximum === 1 && data.series.every((row) => !row[metric.key]) ? 0 : maximum) : "—"}</small></div>
    {available ? <div className="admin-atividade__bars" aria-hidden="true">
      {data.series.map((row) => <div key={row.date} className="admin-atividade__bar-slot" title={`${label(row.date)}: ${valueText(row[metric.key])}${partial(row, metric.key) ? " (parcial)" : ""}`}>
        <span className={row[metric.key] === null ? "is-unavailable" : ""} style={{ height: `${row[metric.key] === null ? 0 : (row[metric.key] ?? 0) / maximum * 100}%` }} />
      </div>)}
    </div> : <p className="admin-atividade__chart-empty">Histórico indisponível neste período.</p>}
    <div className="admin-atividade__chart-axis" aria-hidden="true"><span>{data.series[0] ? label(data.series[0].date) : ""}</span><span>{data.series.length > 1 ? label(data.series[data.series.length - 1].date) : ""}</span></div>
  </section>;
}

export default function AdminAtividade() {
  const [period, setPeriod] = useState<Period>("month");
  const [date, setDate] = useState(today);
  const [refresh, setRefresh] = useState(0);
  const [response, setResponse] = useState<{ key: string; data: Activity } | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const key = `${period}:${date}`;
  const data = response?.key === key ? response.data : null;

  useEffect(() => {
    let mounted = true;
    let inFlight = false;
    async function load() {
      if (inFlight || document.visibilityState !== "visible") return;
      inFlight = true;
      setLoading(true);
      try {
        const result = await api.get<Activity>(`/admin/activity?period=${period}&date=${encodeURIComponent(date)}`);
        if (mounted) { setResponse({ key, data: result }); setError(""); }
      } catch (err) {
        if (mounted) setError(err instanceof Error ? err.message : "Não foi possível atualizar os indicadores.");
      } finally {
        inFlight = false;
        if (mounted) setLoading(false);
      }
    }
    setError("");
    void load();
    const onVisibility = () => { if (document.visibilityState === "visible") void load(); };
    const timer = window.setInterval(() => { void load(); }, 30_000);
    document.addEventListener("visibilitychange", onVisibility);
    return () => { mounted = false; window.clearInterval(timer); document.removeEventListener("visibilitychange", onVisibility); };
  }, [period, date, refresh, key]);

  const bucketText = (value: string) => dateText(value, data?.timezone ?? "America/Sao_Paulo",
    data?.granularity === "hour" ? { hour: "2-digit", minute: "2-digit" } :
      data?.granularity === "month" ? { month: "long", year: "numeric" } : { dateStyle: "short" });

  return <section className="admin-atividade">
    <header className="admin-atividade__header">
      <div><p className="eyebrow">Administração da conta</p><h1>Atividade e crescimento</h1><p>Cadastros, assinaturas, acessos e presença no CorVIA.</p></div>
      <Link to="/admin" className="botao botao--secundario">Administrar usuários</Link>
    </header>
    <div className="admin-atividade__controls">
      <fieldset><legend>Período das métricas</legend><div className="admin-atividade__periods">{PERIODS.map((item) => <button key={item.value} type="button" aria-pressed={period === item.value} onClick={() => setPeriod(item.value)}>{item.label}</button>)}</div></fieldset>
      <label className="admin-atividade__date">Data de referência<input type="date" value={date} max={today()} onChange={(event) => { if (event.target.value) setDate(event.target.value); }} /></label>
      <button type="button" className="botao botao--secundario" disabled={loading} onClick={() => setRefresh((value) => value + 1)}>{loading ? "Atualizando…" : "Atualizar"}</button>
    </div>
    <p className="admin-atividade__caption">Calendário de São Paulo. {period === "day" ? "Valores por hora." : period === "year" ? "Valores por mês." : "Valores por dia."} Atualização automática a cada 30 segundos enquanto esta página estiver visível.</p>
    {error && <div role="alert"><Erro mensagem={data ? `${error} Os últimos dados recebidos permanecem abaixo.` : error} /></div>}
    {!data && !error && <Carregando texto="Carregando indicadores de atividade…" />}
    {data && <>
      <div className="admin-atividade__status"><strong>Referência: {dateText(data.start, data.timezone)}{period !== "day" && ` — ${dateText(new Date(new Date(data.end).getTime() - 1).toISOString(), data.timezone)}`}</strong><span>Atualizado em {dateText(data.generated_at, data.timezone, { dateStyle: "short", timeStyle: "short" })}</span></div>
      <div className="admin-atividade__cards">
        {METRICS.map((metric) => <article key={metric.key} className={`admin-atividade__metric admin-atividade__metric--${metric.key}`}><h2>{metric.title}</h2><strong className="admin-atividade__number"><MetricValue counts={data.totals} metric={metric.key} /></strong><p>{metric.description}</p>{metric.key === "accesses" && <small>{valueText(data.totals.unique_users)} contas distintas no período{data.totals.accesses_partial ? " (histórico parcial)" : ""}.</small>}</article>)}
        <article className="admin-atividade__metric admin-atividade__metric--presence"><h2>Pessoas ativas agora</h2><strong className="admin-atividade__number">{data.active_now.available ? valueText(data.active_now.count) : "—"}</strong><p>{data.active_now.available ? `Contas com página visível e presença registrada nos últimos ${data.active_now.window_seconds} segundos.` : "Presença temporariamente indisponível."}</p><small>Contas únicas, mesmo com várias abas.</small></article>
      </div>
      <section className="admin-atividade__section" aria-labelledby="activity-series-heading"><h2 id="activity-series-heading">Evolução no período</h2><p className="admin-atividade__caption">Cada gráfico usa sua própria escala. Os valores completos estão na tabela abaixo.</p><div className="admin-atividade__charts">{METRICS.map((metric) => <SeriesChart key={metric.key} data={data} metric={metric} />)}</div>
        <div className="admin-atividade__table-wrap" tabIndex={0} role="region" aria-label="Detalhamento por período, com rolagem horizontal em telas pequenas"><table><caption>Detalhamento de cadastros, assinaturas e acessos</caption><thead><tr><th scope="col">{data.granularity === "hour" ? "Hora" : data.granularity === "month" ? "Mês" : "Dia"}</th>{METRICS.map((metric) => <th scope="col" key={metric.key}>{metric.title}</th>)}<th scope="col">Contas distintas</th></tr></thead><tbody>{data.series.map((row) => <tr key={row.date}><th scope="row">{bucketText(row.date)}</th>{METRICS.map((metric) => <td key={metric.key}><MetricValue counts={row} metric={metric.key} /></td>)}<td>{valueText(row.unique_users)}</td></tr>)}</tbody></table></div>
      </section>
      <section className="admin-atividade__section" aria-labelledby="activity-current-heading"><h2 id="activity-current-heading">Períodos atuais</h2><p className="admin-atividade__caption">Resumo do calendário atual, independentemente da data de referência selecionada.</p><div className="admin-atividade__table-wrap" tabIndex={0} role="region" aria-label="Resumo atual com rolagem horizontal"><table><thead><tr><th scope="col">Período</th>{METRICS.map((metric) => <th scope="col" key={metric.key}>{metric.title}</th>)}</tr></thead><tbody>{PERIODS.map((item) => <tr key={item.value}><th scope="row">{item.current}</th>{METRICS.map((metric) => <td key={metric.key}><MetricValue counts={data.current[item.value]} metric={metric.key} /></td>)}</tr>)}</tbody></table></div></section>
      <section className="admin-atividade__definitions" aria-labelledby="activity-definitions-heading"><h2 id="activity-definitions-heading">Como ler os indicadores</h2><dl><div><dt>Cadastros</dt><dd>{data.coverage.registrations_note ?? "Contas criadas no período."} Cadastro não significa assinatura paga.</dd></div><div><dt>Assinaturas</dt><dd>{data.coverage.subscriptions_note} {data.coverage.subscriptions_since ? `Histórico disponível desde ${dateText(data.coverage.subscriptions_since, data.timezone)}.` : "Histórico ainda não disponível."}</dd></div><div><dt>Acessos</dt><dd>{data.coverage.accesses_note} {data.coverage.accesses_since ? `Histórico disponível desde ${dateText(data.coverage.accesses_since, data.timezone)}.` : "Histórico ainda não disponível."} Contas distintas são deduplicadas dentro de cada intervalo e não devem ser somadas entre linhas.</dd></div><div><dt>Disponibilidade</dt><dd>“—” indica dado não disponível ou intervalo futuro. “Parcial” indica contagem limitada ao histórico coletado, sem estimar o que ocorreu antes.</dd></div></dl></section>
    </>}
  </section>;
}
