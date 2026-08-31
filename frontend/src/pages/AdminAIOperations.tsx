import { useEffect, useMemo, useState } from "react";
import ClinicalAIStatusBadge from "../components/ClinicalAIStatusBadge";
import Icone from "../components/Icone";
import { api } from "../lib/api";

type HeartMetrics = {
  cases_by_status?: Record<string, number>; awaiting_review?: number; completed?: number; unusable?: number;
  tokens_input?: number; tokens_output?: number; estimated_cost_micros?: number; reserved_cost_micros?: number;
};
type SubscriberUsage = { owner_id: number; commands: number; estimated_cost_microunits: number; reserved_cost_microunits?: number; daily_used?: number; monthly_used?: number; daily_limit?: number; monthly_limit?: number; operations?: Record<string, number> };
type WhatsAppAdminMetrics = { period_days?: number; subscribers?: SubscriberUsage[]; operations?: Record<string, number>; monthly_cost_ceiling_microunits?: number };

function money(value = 0) { return (value / 1_000_000).toLocaleString("pt-BR", { style: "currency", currency: "BRL", minimumFractionDigits: 4 }); }

export default function AdminAIOperations() {
  const [heart, setHeart] = useState<HeartMetrics | null>(null);
  const [whatsapp, setWhatsApp] = useState<WhatsAppAdminMetrics | null>(null);
  const [error, setError] = useState("");
  async function load() {
    setError("");
    const [h, w] = await Promise.allSettled([api.get<HeartMetrics>("/admin/heart-team/metrics"), api.get<WhatsAppAdminMetrics>("/admin/whatsapp/metrics")]);
    if (h.status === "fulfilled") setHeart(h.value);
    if (w.status === "fulfilled") setWhatsApp(w.value);
    if (h.status === "rejected" && w.status === "rejected") setError("Não foi possível carregar as métricas operacionais.");
  }
  useEffect(() => { void load(); }, []);
  const summary = useMemo(() => {
    const subscribers = whatsapp?.subscribers ?? [];
    return {
      heartCases: Object.values(heart?.cases_by_status ?? {}).reduce((total, value) => total + value, 0),
      whatsappCommands: subscribers.reduce((total, item) => total + (item.commands ?? 0), 0),
      whatsappCost: subscribers.reduce((total, item) => total + (item.estimated_cost_microunits ?? 0), 0),
      reservedCost: subscribers.reduce((total, item) => total + (item.reserved_cost_microunits ?? 0), 0),
    };
  }, [heart, whatsapp]);
  const operations = Object.entries(whatsapp?.operations ?? {});

  return <div className="pagina cai-page cai-admin-ai">
    <header className="cai-hero"><div><p className="cai-kicker">GOVERNANÇA E CUSTO</p><h1>Operações de IA clínica</h1><p>Consumo, bloqueios, revisão humana e limites por assinante em um único painel.</p></div><div className="cai-hero__trust"><Icone nome="indicadores" /><span><strong>Limites ativos</strong><small>Auditoria · RBAC · teto por assinante</small></span></div></header>
    {error && <div className="cai-alert cai-alert--error"><Icone nome="emergencia" />{error}</div>}
    <section className="cai-admin-summary">
      <article><span><Icone nome="assistente" /></span><small>Casos Heart Team</small><strong>{summary.heartCases}</strong><em>{heart?.completed ?? 0} validados · {heart?.unusable ?? 0} inutilizáveis</em></article>
      <article><span><Icone nome="comunicacao" /></span><small>Comandos WhatsApp</small><strong>{summary.whatsappCommands}</strong><em>{whatsapp?.subscribers?.length ?? 0} assinantes no período</em></article>
      <article><span><Icone nome="indicadores" /></span><small>Em revisão clínica</small><strong>{heart?.awaiting_review ?? 0}</strong><em>validação humana obrigatória</em></article>
      <article><span><Icone nome="calculadora" /></span><small>Custo estimado</small><strong>{money((heart?.estimated_cost_micros ?? 0) + summary.whatsappCost)}</strong><em>{money((heart?.reserved_cost_micros ?? 0) + summary.reservedCost)} reservado</em></article>
    </section>
    <section className="cai-panel"><header><div><p className="cai-kicker">CONSUMO POR ASSINANTE</p><h2>Limites e custo do WhatsApp</h2></div><ClinicalAIStatusBadge status="accepted" label="Monitorado" /></header><div className="cai-model-table"><div className="is-head"><span>Assinante</span><span>Comandos</span><span>Custo estimado</span></div>{(whatsapp?.subscribers ?? []).map((item) => <div key={item.owner_id}><strong>#{item.owner_id}</strong><span>{item.commands} · {item.daily_used ?? 0}/{item.daily_limit ?? "—"} hoje</span><span>{money(item.estimated_cost_microunits)}</span></div>)}{!whatsapp?.subscribers?.length && <p className="cai-empty">Nenhum consumo registrado no período.</p>}</div></section>
    <section className="cai-panel"><header><div><p className="cai-kicker">OPERAÇÕES AGREGADAS</p><h2>Funções utilizadas</h2></div><small>{whatsapp?.period_days ?? 30} dias</small></header><div className="cai-model-table">{operations.map(([name, count]) => <div key={name}><strong>{name.replaceAll("_", " ")}</strong><span>{count}</span><span>auditado</span></div>)}{!operations.length && <p className="cai-empty">O backend ainda não disponibilizou agregação por operação. Nenhum valor foi inferido.</p>}</div></section>
  </div>;
}
