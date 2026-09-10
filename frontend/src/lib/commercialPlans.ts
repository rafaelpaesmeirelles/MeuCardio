export type CommercialPlanId = "basico" | "basico_mail" | "ia" | "completo";
export type CommercialFeature = "ai" | "mail";

export type CommercialEntitlements = {
  tudo_com_tudo: boolean;
  ai: boolean;
  mail: boolean;
  source: string;
  commercial_version: string | null;
};

export type CommercialPlan = {
  id: CommercialPlanId;
  name: string;
  price_centavos: number;
  periodicidade: "mensal";
  ai_monthly_credit_centavos?: number;
  checkout_available?: boolean;
  features: Pick<CommercialEntitlements, "tudo_com_tudo" | "ai" | "mail">;
};

export type CommercialCatalog = {
  currency: string;
  commercial_version: string;
  subscriptions_enabled: boolean;
  checkout_available?: boolean;
  ai_monthly_credit_centavos?: number;
  plans: CommercialPlan[];
};

export type CommercialStatus = {
  status: string;
  current_period_end: string | null;
  plano: string | null;
  periodicidade?: string | null;
  acesso_administrativo?: boolean;
  portal_available?: boolean;
  change_plan_available?: boolean;
  entitlements?: CommercialEntitlements;
};

export type AIWallet = {
  currency: string;
  period_start: string;
  period_end: string;
  plan: string | null;
  enabled: boolean;
  monthly_credit_centavos: number;
  spent_credit_centavos: number;
  reserved_credit_centavos: number;
  available_credit_centavos: number;
  budget_credit_centavos: number | null;
  paid_available_credit_centavos: number;
  billing_blocked: boolean;
  pricing_version: string;
  recharge_supported: boolean;
  payments_enabled: boolean;
};

export function formatBRL(centavos: number): string {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(centavos / 100);
}

export function canUseCommercialFeature(status: CommercialStatus | null, feature: CommercialFeature): boolean {
  // The server resolves administrative access and legacy contracts. Plan names
  // alone must never grant or revoke existing benefits in the browser.
  return status?.entitlements?.[feature] === true;
}

export function canCheckout(catalog: CommercialCatalog | null, plan: CommercialPlan): boolean {
  return catalog?.subscriptions_enabled === true &&
    (plan.checkout_available ?? catalog.checkout_available) === true;
}

export function planCredit(catalog: CommercialCatalog, plan: CommercialPlan): number | null {
  if (!plan.features.ai) return null;
  const credit = plan.ai_monthly_credit_centavos ?? catalog.ai_monthly_credit_centavos;
  return typeof credit === "number" && Number.isFinite(credit) && credit >= 0 ? credit : null;
}

export function checkoutLocation(value: unknown): string {
  if (typeof value !== "string") throw new Error("O pagamento não retornou um endereço válido. Tente novamente.");
  const url = new URL(value);
  if (url.protocol !== "https:" || !["checkout.stripe.com", "billing.stripe.com"].includes(url.hostname) || url.username || url.password) {
    throw new Error("O endereço de pagamento não é válido.");
  }
  return url.href;
}
