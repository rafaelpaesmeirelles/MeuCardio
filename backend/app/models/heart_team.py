"""Persistence for the CorVIA Virtual Heart Team.

Clinical outputs and their reviews are append-only.  The mutable case row only
contains workflow state and pointers; the original/final snapshots live in
immutable rows with SHA-256 hashes.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Integer,
    LargeBinary, String, Text, UniqueConstraint, event,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class HeartTeamCase(Base):
    __tablename__ = "heart_team_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    question: Mapped[str | None] = mapped_column(Text, nullable=True)
    analysis_scope: Mapped[str] = mapped_column(String(24), default="global")
    selected_agents: Mapped[list] = mapped_column(JSONB, default=list)
    input_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    structured_case: Mapped[dict] = mapped_column(JSONB, default=dict)
    missing_data: Mapped[list] = mapped_column(JSONB, default=list)
    risk_classification: Mapped[dict] = mapped_column(JSONB, default=dict)
    result: Mapped[dict] = mapped_column(JSONB, default=dict)
    input_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    pipeline_version: Mapped[str] = mapped_column(String(40), default="heart-team-v1")
    model_versions: Mapped[dict] = mapped_column(JSONB, default=dict)
    tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost_micros: Mapped[int] = mapped_column(BigInteger, default=0)
    reserved_cost_micros: Mapped[int] = mapped_column(BigInteger, default=0)
    deidentified_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    medical_review_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','queued','analyzing','awaiting_review','completed','rejected','failed','unusable')",
            name="ck_heart_team_cases_status",
        ),
        CheckConstraint("estimated_cost_micros >= 0 AND reserved_cost_micros >= 0", name="ck_heart_team_case_cost"),
    )


class HeartTeamAttachment(Base):
    __tablename__ = "heart_team_attachments"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("heart_team_cases.id", ondelete="CASCADE"), index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(32), default="upload")
    reference_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    storage_key: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True)
    original_name_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    media_type: Mapped[str] = mapped_column(String(120))
    size_bytes: Mapped[int] = mapped_column(Integer)
    # ``source_sha256`` proves which local input was received; ``sha256`` is
    # always the digest of the sanitized bytes that are persisted/processed.
    source_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    sanitization_report: Mapped[dict] = mapped_column(JSONB, default=dict)
    objective_extract: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (CheckConstraint("size_bytes >= 0", name="ck_heart_team_attachment_size"),)


class HeartTeamAnalysisJob(Base):
    """Durable, idempotent queue record for long-running multi-agent analysis."""
    __tablename__ = "heart_team_analysis_jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("heart_team_cases.id", ondelete="CASCADE"), unique=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(String(20), default="queued", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    next_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    __table_args__ = (CheckConstraint("status IN ('queued','running','completed','failed')", name="ck_heart_team_analysis_job_status"),)


class HeartTeamOpinion(Base):
    __tablename__ = "heart_team_opinions"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("heart_team_cases.id", ondelete="CASCADE"), index=True)
    agent_key: Mapped[str] = mapped_column(String(64), index=True)
    round_name: Mapped[str] = mapped_column(String(24))
    position: Mapped[dict] = mapped_column(JSONB, default=dict)
    content: Mapped[dict] = mapped_column(JSONB, default=dict)
    source_ids: Mapped[list] = mapped_column(JSONB, default=list)
    confidence: Mapped[str] = mapped_column(String(24), default="insufficient")
    content_hash: Mapped[str] = mapped_column(String(64))
    model_name: Mapped[str] = mapped_column(String(120))
    tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (UniqueConstraint("case_id", "agent_key", "round_name", name="uq_heart_team_opinion_round"),)


class HeartTeamSuggestion(Base):
    __tablename__ = "heart_team_suggestions"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("heart_team_cases.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(48))
    original_text: Mapped[str] = mapped_column(Text)
    original_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class HeartTeamSuggestionReview(Base):
    __tablename__ = "heart_team_suggestion_reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    suggestion_id: Mapped[int] = mapped_column(ForeignKey("heart_team_suggestions.id", ondelete="CASCADE"), unique=True)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    decision: Mapped[str] = mapped_column(String(16))
    final_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_hash: Mapped[str] = mapped_column(String(64))
    final_hash: Mapped[str] = mapped_column(String(64))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (CheckConstraint("decision IN ('accepted','rejected','edited')", name="ck_heart_team_suggestion_review"),)


class HeartTeamFinalReview(Base):
    __tablename__ = "heart_team_final_reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("heart_team_cases.id", ondelete="CASCADE"), unique=True)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    decision: Mapped[str] = mapped_column(String(16))
    medical_responsibility_confirmed: Mapped[bool] = mapped_column(Boolean)
    human_decisions_confirmed: Mapped[bool] = mapped_column(Boolean)
    original_snapshot: Mapped[dict] = mapped_column(JSONB)
    final_snapshot: Mapped[dict] = mapped_column(JSONB)
    original_hash: Mapped[str] = mapped_column(String(64))
    final_hash: Mapped[str] = mapped_column(String(64))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (CheckConstraint("decision IN ('accepted','rejected')", name="ck_heart_team_final_review"),)


class HeartTeamPatientRecord(Base):
    """Append-only prontuário/timeline provenance after final physician review.

    This intentionally stores no clinical recommendation or patient identity;
    it records only AI-support provenance required by governance.
    """
    __tablename__ = "heart_team_patient_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("heart_team_cases.id", ondelete="RESTRICT"), unique=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    patient_profile_id: Mapped[int] = mapped_column(ForeignKey("patient_profiles.id", ondelete="RESTRICT"), index=True)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    decision: Mapped[str] = mapped_column(String(16))
    final_hash: Mapped[str] = mapped_column(String(64))
    provenance: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (CheckConstraint("decision IN ('accepted','rejected')", name="ck_heart_team_patient_record_decision"),)


class HeartTeamAuditEvent(Base):
    __tablename__ = "heart_team_audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("heart_team_cases.id", ondelete="CASCADE"), index=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    detail: Mapped[dict] = mapped_column(JSONB, default=dict)
    previous_hash: Mapped[str] = mapped_column(String(64), default="0" * 64)
    event_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class HeartTeamCache(Base):
    __tablename__ = "heart_team_cache"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    cache_key: Mapped[str] = mapped_column(String(64), unique=True)
    encrypted_payload: Mapped[bytes] = mapped_column(LargeBinary)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class HeartTeamCostLedger(Base):
    __tablename__ = "heart_team_cost_ledger"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("heart_team_cases.id", ondelete="CASCADE"), index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    agent_key: Mapped[str] = mapped_column(String(64))
    phase: Mapped[str] = mapped_column(String(24))
    reserved_micros: Mapped[int] = mapped_column(BigInteger, default=0)
    actual_micros: Mapped[int] = mapped_column(BigInteger, default=0)
    tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    model_name: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


_IMMUTABLE = (
    HeartTeamOpinion, HeartTeamSuggestion, HeartTeamSuggestionReview,
    HeartTeamFinalReview, HeartTeamPatientRecord, HeartTeamAuditEvent, HeartTeamCostLedger,
)


def _immutable(*_args, **_kwargs):
    raise ValueError("Registros clínicos e de auditoria do Heart Team são imutáveis.")


for _model in _IMMUTABLE:
    event.listen(_model, "before_update", _immutable)
    event.listen(_model, "before_delete", _immutable)
