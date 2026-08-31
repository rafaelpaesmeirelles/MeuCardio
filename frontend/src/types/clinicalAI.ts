export type ClinicalAIStatus =
  | "draft" | "queued" | "analyzing" | "awaiting_review" | "completed" | "failed"
  | "unusable" | "cancelled" | "pending" | "accepted" | "rejected"
  | "edited" | "blocked";

export type HeartTeamAgent = { key: string; label: string; detail: string; required?: boolean };
export type HeartTeamSource = { id?: string | number; title?: string; route?: string; url?: string; doi?: string; pmid?: string; society?: string; date?: string; year?: number | string; evidence_status?: string };
export type HeartTeamOpinion = { id: number; agent_key: string; agent_label?: string; round_name?: string; round?: string; content: Record<string, unknown> | string; evidence_status?: string; created_at?: string };
export type HeartTeamSuggestionReview = { decision: "accepted" | "rejected" | "edited"; final_text?: string | null; final_hash?: string; note?: string | null };
export type HeartTeamSuggestion = { id: number; category: string; original_text: string; original_hash?: string; review?: HeartTeamSuggestionReview | null };
export type HeartTeamFinalReview = { decision: "accepted" | "rejected"; original_hash?: string; final_hash: string; note?: string | null; created_at: string };
export type HeartTeamCase = {
  id: number; status: ClinicalAIStatus; question?: string | null; case_data?: Record<string, unknown>;
  selected_agents?: string[]; risk_classification?: string; emergency_alerts?: string[]; missing_data?: string[];
  input_data?: Record<string, unknown>; result?: Record<string, unknown> | null;
  consensus?: Record<string, unknown> | null; verified_sources?: HeartTeamSource[]; opinions?: HeartTeamOpinion[];
  suggestions?: HeartTeamSuggestion[]; model_versions?: Record<string, string>; created_at: string; updated_at?: string;
  completed_at?: string | null; failure_code?: string | null; failure_detail?: Record<string, unknown> | null;
  partial_results_quarantined?: boolean; final_review?: HeartTeamFinalReview | null;
};

export type WhatsAppPermissionKey = "read_agenda" | "read_tasks" | "search_science" | "create_reminder" | "create_appointment" | "create_draft" | "external_communication" | "heart_team_draft";
export type WhatsAppCommandStatus = "pending" | "completed" | "failed" | "blocked_security" | "blocked_pii" | "needs_clarification" | "awaiting_confirmation" | "confirmation_expired" | "undone";
export type WhatsAppPendingMessageStatus = "awaiting_transcript_review" | "awaiting_anonymization_confirmation" | "awaiting_media_review" | "transcription_unavailable";
export type WhatsAppMediaReviewAction = "store_only" | "summarize" | "heart_team";
export type WhatsAppPendingMessage = { id: number; type: "audio" | "image" | "document" | string; status: WhatsAppPendingMessageStatus; pii_kinds?: string[]; created_at?: string; review_text?: string | null; mime_type?: string | null; filename?: string | null; pii_use_allowed?: boolean };
export type WhatsAppLinkStatus = { connected: boolean; status: string; phone_masked?: string | null; retention_days?: number | null; permissions: Record<string, boolean>; paired_at?: string | null; provider: string; feature_enabled: boolean };
export type WhatsAppCommand = { id: number; kind: string; level: number; status: WhatsAppCommandStatus; created_at?: string; executed_at?: string | null; requires_confirmation?: boolean; requires_in_app?: boolean; can_confirm?: boolean; confirmation_token?: string | null; undo_token?: string | null; message?: string | null; result?: unknown };
export type AIOperationsMetrics = { messages_received?: number; messages_sent?: number; received_messages?: number; sent_messages?: number; meta_billable_messages?: number; ai_commands?: number; commands?: number; estimated_cost_microunits?: number; blocked_commands?: number; blocked?: number; failed_webhooks?: number; webhook_failures?: number; success_rate?: number; average_latency_ms?: number; daily_limit?: number; monthly_limit?: number; daily_used?: number; monthly_used?: number; models?: Array<{ model: string; calls: number; estimated_cost_microunits?: number }> };
