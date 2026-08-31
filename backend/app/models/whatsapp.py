from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

def agora(): return datetime.now(timezone.utc)

class WhatsAppLink(Base):
    __tablename__ = "whatsapp_links"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    phone_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    phone_cipher: Mapped[bytes] = mapped_column(LargeBinary)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    permissions: Mapped[dict] = mapped_column(JSONB, default=dict)
    retention_days: Mapped[int] = mapped_column(Integer, default=30)
    consent_purpose: Mapped[str] = mapped_column(String(240), default="assistente_pessoal_corvia")
    consent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    paired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pin_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, onupdate=agora)

class WhatsAppPairing(Base):
    __tablename__ = "whatsapp_pairings"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    code_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    retention_days: Mapped[int] = mapped_column(Integer, default=30)
    permissions: Mapped[dict] = mapped_column(JSONB, default=dict)
    pin_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

class WhatsAppWebhookEvent(Base):
    __tablename__ = "whatsapp_webhook_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    provider_event_id: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    payload_hash: Mapped[str] = mapped_column(String(64), index=True)
    link_id: Mapped[int | None] = mapped_column(ForeignKey("whatsapp_links.id", ondelete="SET NULL"), nullable=True)
    provider_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="received", index=True)
    failure_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    link_id: Mapped[int] = mapped_column(ForeignKey("whatsapp_links.id", ondelete="CASCADE"), index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(180), nullable=True, unique=True)
    direction: Mapped[str] = mapped_column(String(10), index=True)
    message_type: Mapped[str] = mapped_column(String(20), index=True)
    payload_cipher: Mapped[bytes] = mapped_column(LargeBinary)
    pii_kinds: Mapped[list] = mapped_column(JSONB, default=list)
    status: Mapped[str] = mapped_column(String(40), default="received", index=True)
    authorization_level: Mapped[int] = mapped_column(Integer, default=1)
    meta_billable: Mapped[bool] = mapped_column(Boolean, default=False)
    estimated_cost_microunits: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, index=True)

class WhatsAppCommand(Base):
    __tablename__ = "whatsapp_commands"
    __table_args__ = (UniqueConstraint("owner_id", "idempotency_key", name="uq_whatsapp_command_owner_key"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    link_id: Mapped[int] = mapped_column(ForeignKey("whatsapp_links.id", ondelete="CASCADE"), index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    message_id: Mapped[int | None] = mapped_column(ForeignKey("whatsapp_messages.id", ondelete="SET NULL"), nullable=True)
    kind: Mapped[str] = mapped_column(String(60), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(180))
    level: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(40), index=True)
    payload_cipher: Mapped[bytes] = mapped_column(LargeBinary)
    confirmation_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confirmation_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    undo_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    undo_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    requires_in_app: Mapped[bool] = mapped_column(Boolean, default=False)
    result_cipher: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, onupdate=agora)

class WhatsAppUsageMetric(Base):
    __tablename__ = "whatsapp_usage_metrics"
    __table_args__ = (UniqueConstraint("owner_id", "idempotency_key", name="uq_whatsapp_metric_owner_key"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    link_id: Mapped[int | None] = mapped_column(ForeignKey("whatsapp_links.id", ondelete="SET NULL"), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(180))
    operation: Mapped[str] = mapped_column(String(80), index=True)
    provider: Mapped[str] = mapped_column(String(30), default="sandbox")
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    input_units: Mapped[int] = mapped_column(Integer, default=0)
    output_units: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost_microunits: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    blocked_reason: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

class WhatsAppHeartTeamJob(Base):
    __tablename__ = "whatsapp_heart_team_jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    command_id: Mapped[int] = mapped_column(ForeignKey("whatsapp_commands.id", ondelete="RESTRICT"), unique=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("heart_team_cases.id", ondelete="RESTRICT"), unique=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    link_id: Mapped[int] = mapped_column(ForeignKey("whatsapp_links.id", ondelete="RESTRICT"), index=True)
    status: Mapped[str] = mapped_column(String(24), default="queued", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    next_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    provider_message_id: Mapped[str | None] = mapped_column(String(180), nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, onupdate=agora)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class WhatsAppOutboundOutbox(Base):
    __tablename__ = "whatsapp_outbound_outbox"
    id: Mapped[int] = mapped_column(primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    link_id: Mapped[int] = mapped_column(ForeignKey("whatsapp_links.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("whatsapp_heart_team_jobs.id", ondelete="CASCADE"), nullable=True)
    mode: Mapped[str] = mapped_column(String(20), default="text")
    payload_cipher: Mapped[bytes] = mapped_column(LargeBinary)
    status: Mapped[str] = mapped_column(String(20), default="sending", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=1)
    estimated_cost_microunits: Mapped[int] = mapped_column(Integer, default=0)
    provider_message_id: Mapped[str | None] = mapped_column(String(180), nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, onupdate=agora)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

class WhatsAppOptEvent(Base):
    __tablename__ = "whatsapp_opt_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    link_id: Mapped[int | None] = mapped_column(ForeignKey("whatsapp_links.id", ondelete="SET NULL"), nullable=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event: Mapped[str] = mapped_column(String(20), index=True)
    purpose: Mapped[str] = mapped_column(String(240))
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

class WhatsAppDraft(Base):
    __tablename__ = "whatsapp_drafts"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    link_id: Mapped[int] = mapped_column(ForeignKey("whatsapp_links.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    title_cipher: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    body_cipher: Mapped[bytes] = mapped_column(LargeBinary)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, onupdate=agora)

class WhatsAppSummaryCache(Base):
    __tablename__ = "whatsapp_summary_cache"
    __table_args__ = (UniqueConstraint("owner_id", "cache_key", name="uq_whatsapp_summary_cache_owner_key"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    cache_key: Mapped[str] = mapped_column(String(64), index=True)
    media_sha256: Mapped[str] = mapped_column(String(64), index=True)
    model: Mapped[str] = mapped_column(String(100))
    pipeline_version: Mapped[str] = mapped_column(String(40))
    result_cipher: Mapped[bytes] = mapped_column(LargeBinary)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    last_accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
