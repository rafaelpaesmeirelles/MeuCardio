import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties, type ReactNode } from "react";
import { ClinicalPageHeader } from "../components/ClinicalCommandPrimitives";
import Icone, { type NomeIcone } from "../components/Icone";
import { api } from "../lib/api";

type Contagem = Record<string, number>;

type IndicadoresPayload = {
  janela_dias: number;
  desde: string;
  ate: string;
  como_solicitante: {
    pedidos_abertos: number;
    pedidos_pagos: number;
    pedidos_atendidos: number;
    aguardando: number;
    gasto_centavos: number;
    prazo_cumprido: number;
    prazo_estourado: number;
    por_servico: Contagem;
    por_urgencia: Contagem;
  };
  como_respondente: {
    atendidos: number;
    por_servico: Contagem;
    por_urgencia: Contagem;
    por_exame: Contagem;
    tempo_medio_resposta_horas: number | null;
    tempo_maior_resposta_horas: number | null;
    dentro_do_prazo: number;
    fora_do_prazo: number;
    folga_mediana_horas: number | null;
    receita_centavos: number;
    fila_aberta_agora: number;
  };
  notas: string[];
};

const JANELAS = [
  { dias: 30, rotulo: "30 dias", detalhe: "Leitura recente" },
  { dias: 90, rotulo: "90 dias", detalhe: "Visão trimestral" },
  { dias: 365, rotulo: "12 meses", detalhe: "Ciclo anual" },
] as const;

function reais(centavos: number) {
  return (centavos / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function horas(valor: number | null) {
  if (valor === null) return "—";
  if (valor < 1) return `${Math.round(valor * 60)} min`;
  return `${valor.toLocaleString("pt-BR", { maximumFractionDigits: 1 })} h`;
}

function percentual(parte: number, total: number): number | null {
  if (total <= 0) return null;
  return Math.max(0, Math.min(100, Math.round((parte / total) * 100)));
}

function formatarDataIso(valor: string) {
  const [ano, mes, dia] = valor.split("-").map(Number);
  if (!ano || !mes || !dia) return valor;
  return new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", year: "numeric" })
    .format(new Date(ano, mes - 1, dia));
}

function formatarCategoria(valor: string) {
  const texto = valor.replace(/[_-]+/g, " ").trim();
  return texto ? texto[0].toLocaleUpperCase("pt-BR") + texto.slice(1) : "Não informado";
}

function MetricCard({ icon, label, value, detail, emphasis = false }: {
  icon: NomeIcone;
  label: string;
  value: ReactNode;
  detail?: string;
  emphasis?: boolean;
}) {
  return (
    <article className={`management-metric${emphasis ? " management-metric--emphasis" : ""}`}>
      <span className="management-metric__icon"><Icone nome={icon} /></span>
      <div className="management-metric__copy">
        <span>{label}</span>
        <strong>{value}</strong>
        {detail && <small>{detail}</small>}
      </div>
    </article>
  );
}

function ExecutiveLens({ kind, eyebrow, title, active, primary, primaryLabel, progress, progressLabel, facts }: {
  kind: "respondente" | "solicitante";
  eyebrow: string;
  title: string;
  active: boolean;
  primary: ReactNode;
  primaryLabel: string;
  progress: number | null;
  progressLabel: string;
  facts: Array<{ label: string; value: ReactNode }>;
}) {
  const progressStyle = { "--management-progress": `${progress ?? 0}%` } as CSSProperties;
  return (
    <article className={`management-lens management-lens--${kind}${active ? " is-active" : " is-idle"}`}>
      <header>
        <div><p>{eyebrow}</p><h2>{title}</h2></div>
        <span className="management-lens__status"><i aria-hidden="true" />{active ? "Com atividade" : "Sem atividade"}</span>
      </header>
      {active ? (
        <div className="management-lens__body">
          <div className="management-lens__primary"><strong>{primary}</strong><span>{primaryLabel}</span></div>
          <div
            className={`management-lens__ring${progress === null ? " is-neutral" : ""}`}
            style={progressStyle}
            role="img"
            aria-label={progress === null ? `${progressLabel}: sem base de cálculo` : `${progressLabel}: ${progress}%`}
          >
            <span>{progress === null ? "—" : `${progress}%`}</span>
            <small>{progressLabel}</small>
          </div>
          <dl>{facts.map((fact) => <div key={fact.label}><dt>{fact.label}</dt><dd>{fact.value}</dd></div>)}</dl>
        </div>
      ) : (
        <div className="management-lens__idle">
          <span aria-hidden="true"><Icone nome={kind === "respondente" ? "check" : "documento"} /></span>
          <div><strong>Nenhum movimento nesta janela</strong><p>Este painel será preenchido somente quando houver atividade real.</p></div>
        </div>
      )}
    </article>
  );
}

function Distribution({ title, subtitle, data }: { title: string; subtitle: string; data: Contagem }) {
  const entries = useMemo(
    () => Object.entries(data).filter(([, value]) => value > 0).sort((a, b) => b[1] - a[1]),
    [data],
  );
  const total = entries.reduce((sum, [, value]) => sum + value, 0);

  return (
    <article className="management-distribution">
      <header><div><h3>{title}</h3><p>{subtitle}</p></div><span>{total}</span></header>
      {total > 0 ? (
        <div className="management-distribution__rows">
          {entries.map(([key, value]) => {
            const share = Math.round((value / total) * 100);
            const label = formatarCategoria(key);
            return (
              <div className="management-distribution__row" key={key}>
                <div><span title={label}>{label}</span><strong>{value}</strong></div>
                <span
                  className="management-distribution__track"
                  role="img"
                  aria-label={`${label}: ${value} de ${total}, ${share}%`}
                ><i style={{ width: `${share}%` }} /></span>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="management-distribution__empty">Sem registros nesta dimensão.</p>
      )}
    </article>
  );
}

function LoadingPanel() {
  return (
    <div className="management-loading" role="status" aria-live="polite">
      <span className="management-loading__signal" aria-hidden="true"><i /><i /><i /></span>
      <div><strong>Sincronizando seu pulso operacional…</strong><p>Consolidando apenas os dados da janela selecionada.</p></div>
      <span className="sr-only">Carregando indicadores pessoais</span>
    </div>
  );
}

export default function Indicadores() {
  const [days, setDays] = useState(30);
  const [data, setData] = useState<IndicadoresPayload | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const requestId = useRef(0);

  const load = useCallback((windowDays: number) => {
    const currentRequest = ++requestId.current;
    setLoading(true);
    setError("");
    setData(null);
    api.get<IndicadoresPayload>(`/indicadores/meus?dias=${windowDays}`)
      .then((payload) => {
        if (requestId.current === currentRequest) setData(payload);
      })
      .catch((cause) => {
        if (requestId.current !== currentRequest) return;
        setError(cause instanceof Error ? cause.message : "Não foi possível carregar os indicadores.");
      })
      .finally(() => {
        if (requestId.current === currentRequest) setLoading(false);
      });
  }, []);

  useEffect(() => { load(days); }, [days, load]);

  const respondent = data?.como_respondente;
  const requester = data?.como_solicitante;
  const hasRespondent = !!respondent && (respondent.atendidos > 0 || respondent.fila_aberta_agora > 0);
  const hasRequester = !!requester && requester.pedidos_abertos > 0;
  const respondentSla = respondent ? percentual(respondent.dentro_do_prazo, respondent.atendidos) : null;
  const requesterSla = requester ? percentual(requester.prazo_cumprido, requester.pedidos_atendidos) : null;
  const period = data ? `${formatarDataIso(data.desde)} — ${formatarDataIso(data.ate)}` : null;

  return (
    <div className="cv-page cv-management-observatory" aria-busy={loading}>
      <ClinicalPageHeader
        eyebrow="Observatório executivo pessoal"
        title="Pulso da operação"
        description="Uma leitura privada da sua atividade em telediagnóstico — demanda, resposta, prazo e fluxo financeiro no mesmo campo de decisão."
        icon="indicadores"
        actions={[{ to: "/telediagnostico", label: "Abrir telediagnóstico", icon: "evidencia", tone: "primary" }]}
        meta={
          <>
            <span className="selo management-private"><Icone nome="check" /> Somente você</span>
            <span className="selo">{period ?? "Sincronizando período"}</span>
          </>
        }
      />

      <section className="management-window" aria-labelledby="management-window-title">
        <div className="management-window__identity">
          <span><Icone nome="relogio" /></span>
          <div><p>JANELA DE LEITURA</p><h2 id="management-window-title">Escolha a perspectiva temporal</h2></div>
        </div>
        <div className="management-window__options" role="group" aria-label="Período dos indicadores">
          {JANELAS.map((windowOption) => (
            <button
              type="button"
              key={windowOption.dias}
              className={days === windowOption.dias ? "is-active" : ""}
              aria-pressed={days === windowOption.dias}
              onClick={() => setDays(windowOption.dias)}
            >
              <strong>{windowOption.rotulo}</strong><small>{windowOption.detalhe}</small>
            </button>
          ))}
        </div>
        <div className="management-window__sync" aria-live="polite">
          <i className={loading ? "is-loading" : ""} aria-hidden="true" />
          <span>{loading ? "Atualizando" : data ? `${data.janela_dias} dias consolidados` : "Sem leitura"}</span>
        </div>
      </section>

      {loading ? (
        <LoadingPanel />
      ) : error ? (
        <section className="management-state management-state--error" role="alert">
          <span><Icone nome="sincronizar" /></span>
          <div><p>LEITURA INTERROMPIDA</p><h2>Não foi possível consolidar seus indicadores</h2><strong>{error}</strong></div>
          <button type="button" onClick={() => load(days)}><Icone nome="sincronizar" />Tentar novamente</button>
        </section>
      ) : data && respondent && requester ? (
        <>
          <section className="management-pulse" aria-labelledby="management-pulse-title">
            <div className="management-pulse__heading">
              <div><p className="eyebrow">DUAS PERSPECTIVAS · UMA OPERAÇÃO</p><h2 id="management-pulse-title">Visão executiva da janela</h2></div>
              <span><i aria-hidden="true" />Dados pessoais consolidados</span>
            </div>
            <div className="management-pulse__grid">
              <ExecutiveLens
                kind="respondente"
                eyebrow="PRODUÇÃO ASSISTENCIAL"
                title="Como respondente"
                active={hasRespondent}
                primary={respondent.atendidos}
                primaryLabel="atendimentos concluídos"
                progress={respondentSla}
                progressLabel="no prazo"
                facts={[
                  { label: "Tempo médio", value: horas(respondent.tempo_medio_resposta_horas) },
                  { label: "Fila agora", value: respondent.fila_aberta_agora },
                  { label: "Receita", value: reais(respondent.receita_centavos) },
                ]}
              />
              <ExecutiveLens
                kind="solicitante"
                eyebrow="DEMANDA ASSISTENCIAL"
                title="Como solicitante"
                active={hasRequester}
                primary={requester.pedidos_abertos}
                primaryLabel="pedidos abertos"
                progress={requesterSla}
                progressLabel="no prazo"
                facts={[
                  { label: "Pagos", value: requester.pedidos_pagos },
                  { label: "Aguardando", value: requester.aguardando },
                  { label: "Investimento", value: reais(requester.gasto_centavos) },
                ]}
              />
            </div>
          </section>

          {!hasRespondent && !hasRequester ? (
            <section className="management-state management-state--empty" aria-labelledby="management-empty-title">
              <span><Icone nome="indicadores" /></span>
              <div><p>JANELA SEM MOVIMENTO</p><h2 id="management-empty-title">Sua operação está pronta para registrar atividade</h2><strong>Os indicadores surgem após um pedido solicitado ou atendido no período escolhido.</strong></div>
            </section>
          ) : (
            <div className="management-detail-sections">
              {hasRespondent && (
                <section className="cv-section management-detail" aria-labelledby="management-respondent-title">
                  <div className="cv-section__heading management-detail__heading">
                    <div><p className="eyebrow">ENTREGA E SLA</p><h2 id="management-respondent-title">Produção como respondente</h2><p>Volume concluído, tempo de resposta, prazo e receita atribuídos a você.</p></div>
                    <span>{respondent.atendidos} {respondent.atendidos === 1 ? "atendimento" : "atendimentos"}</span>
                  </div>
                  <div className="management-metrics">
                    <MetricCard icon="check" label="Atendidos no período" value={respondent.atendidos} emphasis />
                    <MetricCard icon="relogio" label="Tempo médio de resposta" value={horas(respondent.tempo_medio_resposta_horas)} detail={respondent.tempo_maior_resposta_horas !== null ? `Maior tempo: ${horas(respondent.tempo_maior_resposta_horas)}` : "Sem tempo calculável"} />
                    <MetricCard icon="rota" label="Dentro do prazo" value={respondent.atendidos > 0 ? `${respondent.dentro_do_prazo}/${respondent.atendidos}` : "—"} detail={respondent.fora_do_prazo > 0 ? `${respondent.fora_do_prazo} fora do prazo` : respondent.atendidos > 0 ? "Nenhum atraso" : "Sem base concluída"} />
                    <MetricCard icon="indicadores" label="Receita no período" value={reais(respondent.receita_centavos)} />
                    <MetricCard icon="sincronizar" label="Na fila agora" value={respondent.fila_aberta_agora} detail="Fila paga ainda não atendida" />
                    <MetricCard icon="relogio" label="Folga mediana até o prazo" value={horas(respondent.folga_mediana_horas)} />
                  </div>
                  <div className="management-distributions">
                    <Distribution title="Serviços" subtitle="Composição dos atendimentos" data={respondent.por_servico} />
                    <Distribution title="Urgência" subtitle="Prioridade operacional" data={respondent.por_urgencia} />
                    <Distribution title="Exames" subtitle="Modalidades respondidas" data={respondent.por_exame} />
                  </div>
                </section>
              )}

              {hasRequester && (
                <section className="cv-section management-detail" aria-labelledby="management-requester-title">
                  <div className="cv-section__heading management-detail__heading">
                    <div><p className="eyebrow">DEMANDA E INVESTIMENTO</p><h2 id="management-requester-title">Operação como solicitante</h2><p>Pedidos iniciados por você, seus estados e o cumprimento do prazo contratado.</p></div>
                    <span>{requester.pedidos_abertos} {requester.pedidos_abertos === 1 ? "pedido" : "pedidos"}</span>
                  </div>
                  <div className="management-metrics management-metrics--requester">
                    <MetricCard icon="documento" label="Pedidos abertos" value={requester.pedidos_abertos} emphasis />
                    <MetricCard icon="check" label="Pagamentos confirmados" value={requester.pedidos_pagos} />
                    <MetricCard icon="sincronizar" label="Aguardando resposta" value={requester.aguardando} />
                    <MetricCard icon="indicadores" label="Investimento no período" value={reais(requester.gasto_centavos)} />
                    <MetricCard icon="rota" label="Prazo cumprido" value={requester.pedidos_atendidos > 0 ? `${requester.prazo_cumprido}/${requester.pedidos_atendidos}` : "—"} detail={requester.prazo_estourado > 0 ? `${requester.prazo_estourado} fora do prazo` : requester.pedidos_atendidos > 0 ? "Nenhum atraso" : "Sem pedido atendido"} />
                    <MetricCard icon="evidencia" label="Pedidos atendidos" value={requester.pedidos_atendidos} />
                  </div>
                  <div className="management-distributions management-distributions--two">
                    <Distribution title="Serviços" subtitle="Composição das solicitações" data={requester.por_servico} />
                    <Distribution title="Urgência" subtitle="Prioridade contratada" data={requester.por_urgencia} />
                  </div>
                </section>
              )}
            </div>
          )}

          <details className="management-methodology">
            <summary><span><Icone nome="conhecimento" /></span><span><strong>Como estes números são calculados</strong><small>Metodologia, limites e leitura correta dos dados</small></span><Icone nome="chevron" /></summary>
            <div>
              <ul>{data.notas.map((note, index) => <li key={`${index}-${note}`}>{note}</li>)}</ul>
              <p><Icone nome="indicadores" /><span>Esta API consolida a janela selecionada e não fornece comparação com o período anterior. Por isso, nenhuma tendência foi presumida nesta tela.</span></p>
            </div>
          </details>
        </>
      ) : null}
    </div>
  );
}
