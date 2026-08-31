import type { ClinicalAIStatus } from "../types/clinicalAI";

const LABELS: Record<string, string> = {
  draft: "Rascunho da IA", analyzing: "Em análise", awaiting_review: "Aguardando confirmação",
  completed: "Confirmado pelo médico", failed: "Falha na análise", unusable: "Resultado não utilizável",
  cancelled: "Cancelado", pending: "Aguardando confirmação", accepted: "Confirmado pelo médico",
  rejected: "Rejeitado pelo médico", edited: "Editado pelo médico", blocked: "Bloqueado por segurança",
};

export default function ClinicalAIStatusBadge({ status, label }: { status: ClinicalAIStatus | string; label?: string }) {
  const normalized = ["security_blocked", "blocked_security", "blocked_pii"].includes(status) ? "blocked" : status;
  return <span className={`cai-status cai-status--${normalized}`}>{label ?? LABELS[normalized] ?? normalized.replaceAll("_", " ")}</span>;
}
