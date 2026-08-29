from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class PatientMultimodalExamRecord(Base):
    """Arquivo de exame privado e longitudinal do prontuário.

    O binário original é fato documental imutável. A sugestão de IA fica em
    tabela separada e nunca substitui laudo/resultado sem revisão médica.
    """

    __tablename__ = "patient_multimodal_exam_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    patient_profile_id: Mapped[int] = mapped_column(ForeignKey("patient_profiles.id", ondelete="RESTRICT"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    source_encounter_id: Mapped[int | None] = mapped_column(ForeignKey("clinical_encounters.id", ondelete="SET NULL"), nullable=True, index=True)
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    exam_type: Mapped[str] = mapped_column(String(60), index=True)
    storage_key: Mapped[str] = mapped_column(String(100), unique=True)
    original_name_cifrado: Mapped[bytes] = mapped_column(LargeBinary)
    media_type: Mapped[str] = mapped_column(String(120))
    size_bytes: Mapped[int] = mapped_column(Integer)
    notes_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)

    __table_args__ = (
        CheckConstraint("size_bytes > 0", name="ck_patient_multimodal_exam_size_positive"),
    )


class PatientMultimodalAISuggestion(Base):
    __tablename__ = "patient_multimodal_ai_suggestions"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    patient_profile_id: Mapped[int] = mapped_column(ForeignKey("patient_profiles.id", ondelete="RESTRICT"), index=True)
    exam_record_id: Mapped[int] = mapped_column(ForeignKey("patient_multimodal_exam_records.id", ondelete="RESTRICT"), index=True)
    requested_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="generated", index=True)
    payload_cifrado: Mapped[bytes] = mapped_column(LargeBinary)
    provider: Mapped[str] = mapped_column(String(30))
    model: Mapped[str] = mapped_column(String(100))
    prompt_version: Mapped[str] = mapped_column(String(80))
    tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_note_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    accepted_result_id: Mapped[int | None] = mapped_column(ForeignKey("patient_exam_results.id", ondelete="RESTRICT"), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)

    __table_args__ = (
        CheckConstraint(
            "status IN ('generated','accepted','rejected')",
            name="ck_patient_multimodal_ai_status",
        ),
        CheckConstraint(
            "(status = 'generated' AND reviewed_at IS NULL AND reviewed_by IS NULL AND accepted_result_id IS NULL) OR "
            "(status = 'rejected' AND reviewed_at IS NOT NULL AND reviewed_by IS NOT NULL AND accepted_result_id IS NULL) OR "
            "(status = 'accepted' AND reviewed_at IS NOT NULL AND reviewed_by IS NOT NULL AND accepted_result_id IS NOT NULL)",
            name="ck_patient_multimodal_ai_review_state",
        ),
        Index(
            "uq_patient_multimodal_ai_accepted_exam",
            "exam_record_id",
            unique=True,
            postgresql_where=text("status = 'accepted'"),
        ),
    )
