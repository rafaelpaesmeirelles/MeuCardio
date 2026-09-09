import { useEffect, useRef, useState } from "react";
import { api } from "../lib/api";
import { checkoutLocation, formatBRL, type AIWallet } from "../lib/commercialPlans";

type CreditPackages = {
  currency: "BRL";
  enabled: boolean;
  automatic_topup: false;
  packages: Array<{ amount_centavos: number; credit_centavos: number }>;
};

export default function AIWalletCard({ subscriptionsEnabled }: { subscriptionsEnabled: boolean }) {
  const [wallet, setWallet] = useState<AIWallet | null>(null);
  const [packages, setPackages] = useState<CreditPackages | null>(null);
  const [error, setError] = useState("");
  const [paymentError, setPaymentError] = useState("");
  const [notice, setNotice] = useState("");
  const [limit, setLimit] = useState("");
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const requestKeys = useRef(new Map<number, string>());

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    api.get<AIWallet>("/ai/wallet")
      .then((value) => { if (active) { setWallet(value); setLimit(value.budget_credit_centavos === null ? "" : (value.budget_credit_centavos / 100).toFixed(2)); } })
      .catch((e) => { if (active) setError(e instanceof Error ? e.message : "Não foi possível consultar seu saldo de IA."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [attempt]);

  useEffect(() => {
    let active = true;
    setPackages(null);
    if (subscriptionsEnabled) {
      api.get<CreditPackages>("/ai-credits/packages")
        .then((value) => { if (active) setPackages(value); })
        .catch(() => { if (active) setPackages(null); });
    }
    return () => { active = false; };
  }, [subscriptionsEnabled, attempt]);

  async function saveBudget() {
    const amount = limit.trim() === "" ? null : Math.round(Number(limit) * 100);
    if (!wallet || (amount !== null && (!Number.isFinite(amount) || amount < 0))) return;
    setPending("budget");
    setError("");
    setNotice("");
    try {
      await api.put("/ai/wallet/budget", { budget_credit_centavos: amount });
      const value = await api.get<AIWallet>("/ai/wallet");
      setWallet(value);
      setLimit(value.budget_credit_centavos === null ? "" : (value.budget_credit_centavos / 100).toFixed(2));
      setNotice("Seu limite de IA foi atualizado. A busca Tudo com Tudo permanece disponível.");
    } catch (e) { setError(e instanceof Error ? e.message : "Não foi possível atualizar o limite."); }
    finally { setPending(null); }
  }

  async function recharge(amount: number) {
    if (!subscriptionsEnabled || !packages?.enabled || !packages.packages.some((item) => item.amount_centavos === amount)) return;
    setPending(`recharge-${amount}`);
    setPaymentError("");
    try {
      let key = requestKeys.current.get(amount);
      if (!key) { key = crypto.randomUUID(); requestKeys.current.set(amount, key); }
      const result = await api.post<{ url: string; purchase_id: string }>("/ai-credits/checkout", {
        amount_centavos: amount, request_key: key,
      });
      const destination = checkoutLocation(result.url);
      if (new URL(destination).hostname !== "checkout.stripe.com") throw new Error("O endereço de recarga não é válido.");
      window.location.assign(destination);
    } catch (e) { setPaymentError(e instanceof Error ? e.message : "Não foi possível iniciar a recarga. Você pode tentar novamente."); }
    finally { setPending(null); }
  }

  return (
    <section className="cartao" style={{ marginTop: "1.5rem", maxWidth: "900px" }} aria-labelledby="ai-wallet-heading">
      <h2 id="ai-wallet-heading" style={{ marginTop: 0 }}>Seu crédito de IA</h2>
      {loading && <p role="status">Consultando seu saldo…</p>}
      {error && <p role="alert">{error}</p>}
      {!loading && !wallet && <button className="botao botao--secundario" onClick={() => setAttempt((value) => value + 1)}>Consultar novamente</button>}
      {notice && <p role="status">{notice}</p>}
      {wallet && <>
        <p>Disponível para novas tarefas: <strong>{formatBRL(wallet.available_credit_centavos)}</strong></p>
        <dl style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "0.8rem" }}>
          {[
            ["Franquia deste ciclo", wallet.monthly_credit_centavos],
            ["Recargas disponíveis", wallet.paid_available_credit_centavos],
            ["Utilizado no ciclo", wallet.spent_credit_centavos],
            ["Reservado em tarefas", wallet.reserved_credit_centavos],
            ["Seu limite no ciclo", wallet.budget_credit_centavos],
          ].map(([label, value]) => <div key={label}><dt style={{ color: "var(--texto-secundario)" }}>{label}</dt><dd style={{ margin: "0.2rem 0", fontWeight: 700 }}>{value === null ? "Todo o saldo disponível" : formatBRL(value as number)}</dd></div>)}
        </dl>
        <p style={{ fontSize: "0.85rem", color: "var(--texto-secundario)" }}>Ciclo: {new Date(wallet.period_start).toLocaleDateString("pt-BR")} a {new Date(wallet.period_end).toLocaleDateString("pt-BR")}. Créditos reservados ficam separados enquanto uma tarefa está em andamento. Em upgrades durante o ciclo, cobrança e franquia de IA são proporcionais ao período restante.</p>
        {!wallet.enabled && <p role="status">O uso de IA por esta carteira está indisponível no momento.</p>}
        {wallet.billing_blocked && <p role="status">Novas tarefas de IA estão pausadas. Consulte o saldo e as condições de acesso da sua assinatura.</p>}
        {wallet.enabled && <form onSubmit={(event) => { event.preventDefault(); void saveBudget(); }}>
          <label htmlFor="ai-wallet-budget">Limite de uso de IA no ciclo (R$)</label>
          <div style={{ display: "flex", gap: "0.6rem", alignItems: "center", flexWrap: "wrap", marginTop: "0.5rem" }}>
            <input id="ai-wallet-budget" type="number" min="0" step="0.01" placeholder="Todo o saldo" value={limit} onChange={(event) => setLimit(event.target.value)} style={{ width: "150px" }} aria-describedby="ai-wallet-budget-help" />
            <button className="botao botao--secundario" disabled={pending !== null}>{pending === "budget" ? "Salvando…" : "Salvar limite"}</button>
          </div>
          <p id="ai-wallet-budget-help" style={{ fontSize: "0.85rem" }}>Deixe em branco para usar o saldo disponível, incluindo recargas, ou defina zero para pausar novas tarefas. Tarefas já iniciadas mantêm suas reservas. Este ajuste não compra créditos.</p>
        </form>}
        <p>Ao acabar o saldo, novas tarefas de IA são pausadas. Conteúdo científico, calculadoras e Tudo com Tudo continuam disponíveis.</p>
      </>}
      {subscriptionsEnabled && packages?.enabled && <div style={{ marginTop: "1rem" }}>
        <h3>Adicionar crédito de IA</h3>
        <p>Recarga opcional, sem renovação automática. O saldo é liberado após a confirmação do pagamento.</p>
        <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
          {packages.packages.map((item) => <button className="botao botao--secundario" key={item.amount_centavos} disabled={pending !== null} onClick={() => recharge(item.amount_centavos)}>
            {pending === `recharge-${item.amount_centavos}` ? "Abrindo pagamento…" : `${formatBRL(item.credit_centavos)} de crédito por ${formatBRL(item.amount_centavos)}`}
          </button>)}
        </div>
        {paymentError && <p role="alert">{paymentError}</p>}
      </div>}
    </section>
  );
}
