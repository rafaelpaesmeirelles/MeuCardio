import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import AIWalletCard from "../components/AIWalletCard";
import {
  canCheckout, checkoutLocation, formatBRL, planCredit,
  type CommercialCatalog, type CommercialPlan, type CommercialStatus,
} from "../lib/commercialPlans";

const STATUS: Record<string, string> = {
  ativo: "Ativa", teste: "Período de teste", inativo: "Inativa", pendente: "Pendente",
  inadimplente: "Pagamento pendente", suspenso: "Suspensa", cancelado: "Cancelada", pausado: "Pausada",
};

export default function Assinatura() {
  const [catalog, setCatalog] = useState<CommercialCatalog | null>(null);
  const [status, setStatus] = useState<CommercialStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    Promise.all([api.get<CommercialCatalog>("/billing/plans"), api.get<CommercialStatus>("/billing/status")])
      .then(([plans, current]) => { if (active) { setCatalog(plans); setStatus(current); } })
      .catch((e) => { if (active) setError(e instanceof Error ? e.message : "Não foi possível carregar os planos."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [attempt]);

  async function choose(plan: CommercialPlan, change = false) {
    if (!catalog || !canCheckout(catalog, plan)) return;
    if (change && !window.confirm(`Alterar sua assinatura para ${plan.name}, por ${formatBRL(plan.price_centavos)}/mês? O pagamento considera o ajuste proporcional do ciclo atual.`)) return;
    setPending(plan.id);
    setError("");
    setNotice("");
    try {
      const endpoint = change ? "/billing/trocar-plano" : "/billing/checkout";
      const result = await api.post<{ checkout_url?: string | null; convidado?: boolean; mensagem?: string; nota?: string }>(
        `${endpoint}?plano=${plan.id}&periodicidade=mensal`,
      );
      if (result.convidado || change) {
        setNotice(result.nota || result.mensagem || "Seu acesso foi atualizado.");
        setStatus(await api.get<CommercialStatus>("/billing/status"));
      } else window.location.assign(checkoutLocation(result.checkout_url));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível iniciar o pagamento.");
    } finally { setPending(null); }
  }

  async function portal() {
    setPending("portal");
    setError("");
    try {
      const result = await api.post<{ portal_url: string }>("/billing/portal");
      window.location.assign(checkoutLocation(result.portal_url));
    } catch (e) { setError(e instanceof ApiError ? e.message : "Não foi possível abrir sua assinatura."); }
    finally { setPending(null); }
  }

  return (
    <div className="pagina assinatura-page">
      <h1>Assinatura e uso de IA</h1>
      <p>O Tudo com Tudo, o acervo científico e as calculadoras estão em todos os planos.</p>
      {loading && <p role="status">Carregando seus planos e acesso…</p>}
      {error && <div role="alert" className="cartao"><p>{error}</p>{!catalog && <button className="botao botao--secundario" onClick={() => setAttempt((value) => value + 1)}>Tentar novamente</button>}</div>}
      {notice && <p role="status">{notice}</p>}
      {!loading && catalog && status && <>
        <section className="cartao" style={{ maxWidth: "760px", marginBottom: "1.5rem" }} aria-label="Seu acesso atual">
          <h2 style={{ marginTop: 0 }}>Seu acesso</h2>
          <p>{status.acesso_administrativo ? "Acesso concedido administrativamente, sem cobrança de assinatura." : `Assinatura: ${STATUS[status.status] ?? status.status}.`}</p>
          {status.plano && <p>Plano registrado: <strong>{catalog.plans.find((plan) => plan.id === status.plano)?.name ?? status.plano}</strong>{status.periodicidade && ` · ${status.periodicidade}`}</p>}
          {status.current_period_end && <p>Fim do ciclo: {new Date(status.current_period_end).toLocaleDateString("pt-BR")}</p>}
          {status.entitlements && <p style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
            <span className="tag">Tudo com Tudo incluído</span>
            {status.entitlements.ai && <span className="tag">Recursos de IA incluídos</span>}
            {status.entitlements.mail && <span className="tag">CorVIA Mail incluído</span>}
          </p>}
          {status.entitlements?.source === "subscription" && status.entitlements.commercial_version !== catalog.commercial_version && <p>As condições do seu contrato anterior permanecem vigentes até uma alteração confirmada.</p>}
          {status.portal_available && <button className="botao botao--secundario" disabled={pending !== null} onClick={portal}>{pending === "portal" ? "Abrindo…" : "Gerenciar pagamentos e recibos"}</button>}
        </section>
        {!catalog.subscriptions_enabled && <p className="cartao" role="status">Novas assinaturas ainda não estão disponíveis. Estes planos estão em preparação e os valores serão revisados antes do lançamento.</p>}
        <section aria-label="Planos CorVIA" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 250px), 1fr))", gap: "1rem", maxWidth: "1120px" }}>
          {catalog.plans.map((plan) => {
            const credit = planCredit(catalog, plan);
            const current = status.plano === plan.id && status.periodicidade === "mensal" && status.entitlements?.commercial_version === catalog.commercial_version;
            const purchasable = canCheckout(catalog, plan) && !status.acesso_administrativo;
            const existing = ["ativo", "teste", "inadimplente"].includes(status.status);
            return <article key={plan.id} className="cartao" style={{ display: "flex", flexDirection: "column" }}>
              <h2 style={{ marginTop: 0 }}>{plan.name}</h2>
              <p style={{ fontSize: "1.3rem", margin: "0.2rem 0" }}><strong>{formatBRL(plan.price_centavos)}</strong><span style={{ fontSize: "0.9rem" }}>/mês</span></p>
              <p>{plan.features.ai ? "Ciência, prática e apoio de IA." : "Ciência e ferramentas para sua prática."}{plan.features.mail && " Com CorVIA Mail."}</p>
              <ul style={{ paddingLeft: "1.1rem", flex: 1 }}>
                <li>Tudo com Tudo e conteúdo científico integrado</li>
                <li>Calculadoras, agenda e ferramentas clínicas</li>
                {plan.features.ai && <><li>Assistentes, discussões clínicas e análise de exames com IA</li><li>Heart Team Virtual e Assistente pelo WhatsApp</li>{credit !== null && <li>{formatBRL(credit)} de crédito mensal para os recursos de IA</li>}</>}
                {plan.features.mail && <li>CorVIA Mail integrado</li>}
              </ul>
              {plan.features.ai && <p style={{ fontSize: "0.85rem", color: "var(--texto-secundario)" }}>O consumo varia por tarefa. Em upgrades durante o ciclo, cobrança e franquia de IA são proporcionais ao período restante. Ao atingir seu limite, novas execuções de IA são pausadas; o Tudo com Tudo continua disponível.</p>}
              {current ? <p className="tag">Seu plano atual</p> : purchasable && (!existing || status.change_plan_available) ? <button className="botao" disabled={pending !== null} onClick={() => choose(plan, existing)}>{pending === plan.id ? "Processando…" : existing ? "Mudar para este plano" : "Assinar este plano"}</button> : null}
            </article>;
          })}
        </section>
        {status.entitlements?.ai && <AIWalletCard subscriptionsEnabled={catalog.subscriptions_enabled} />}
      </>}
    </div>
  );
}
