export type ScientificDiscovery = {
  id: number; slug?: string; title: string; org: string; url: string | null; doi: string | null;
  discovered_at: string | null; published_at: string | null; status: string;
};
export type IntelligenceStatus = {
  health: "active" | "degraded" | "inactive" | "unknown"; enabled: boolean;
  cadence_hours: 1 | 4; normal_interval_hours: 4; surge_interval_hours: 1;
  schedule_reason: string; high_frequency_window: string | null;
  last_heartbeat_at: string | null; last_started_at: string | null;
  last_completed_at: string | null; last_success_at: string | null; next_run_at: string | null;
  analysis_status?: "rate_limited" | "unavailable" | "partial" | "ok" | "not_run";
  coverage: { direct_sources_total: number; direct_sources_ok: number; direct_sources_failed: number;
    structured_total: number; structured_ok: number; structured_failed: number } | null;
  document_processing?: {
    health: "active" | "inactive" | "unknown"; enabled: boolean; last_heartbeat_at: string | null;
    total: number; queued: number; ready_full_pt: number; ready_original: number;
    blocked_license: number; blocked_fulltext: number; budget_wait: number; failed: number;
    by_status: Record<string, number>;
  };
  recent_discoveries: ScientificDiscovery[]; total_discovered: number; pending_analysis: number;
};
export function intelligenceHealthLabel(status: IntelligenceStatus): string {
  if (status.health === "unknown") return "Aguardando confirmação do monitoramento";
  if (status.health === "inactive") return "Monitoramento sem execução recente";
  if (!status.enabled) return "Monitoramento desativado";
  return status.health === "active" ? "Monitoramento ativo" : "Monitoramento com pendências";
}
export function scientificDate(value: string | null): string {
  if (!value) return "Ainda não registrada";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Data indisponível" : date.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}
export function scientificSourceUrl(item: ScientificDiscovery): string | null {
  if (item.url && /^https?:\/\//i.test(item.url)) return item.url;
  return item.doi && /^10\.\d{4,9}\//.test(item.doi) ? `https://doi.org/${encodeURI(item.doi)}` : null;
}
