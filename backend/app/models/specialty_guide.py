from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class SpecialtyDisease(Base):
    """Verbete clínico especializado e esquema opcional de assistente determinístico."""

    __tablename__ = "specialty_diseases"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(400), index=True)
    aliases: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    area: Mapped[str] = mapped_column(String(60), index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    subtype: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    cyanosis_class: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    prevalence_rank: Mapped[int] = mapped_column(Integer, default=999, index=True)
    completeness: Mapped[str] = mapped_column(String(20), default="basico", index=True)

    summary: Mapped[str] = mapped_column(Text)
    epidemiology: Mapped[str | None] = mapped_column(Text, nullable=True)
    presentation: Mapped[list] = mapped_column(JSONB, default=list)
    diagnostic_approach: Mapped[dict] = mapped_column(JSONB, default=dict)
    differentials: Mapped[list] = mapped_column(JSONB, default=list)
    tests: Mapped[list] = mapped_column(JSONB, default=list)
    red_flags: Mapped[list] = mapped_column(JSONB, default=list)
    ambulatory_flow: Mapped[list] = mapped_column(JSONB, default=list)
    emergency_flow: Mapped[list] = mapped_column(JSONB, default=list)
    treatment_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    monitoring: Mapped[list] = mapped_column(JSONB, default=list)
    special_populations: Mapped[list] = mapped_column(JSONB, default=list)

    assistant_questions: Mapped[list] = mapped_column(JSONB, default=list)
    assistant_rules: Mapped[list] = mapped_column(JSONB, default=list)

    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    source_refs: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    source_urls: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    related_document_slugs: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    patient_material_slug: Mapped[str | None] = mapped_column(String(255), nullable=True)

    review_status: Mapped[str] = mapped_column(String(40), default="pendente_revisao", index=True)
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class SymptomTriageGuide(Base):
    """Fluxo versionado de triagem para consultório e emergência."""

    __tablename__ = "symptom_triage_guides"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(300), index=True)
    aliases: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    areas: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    summary: Mapped[str] = mapped_column(Text)

    questions: Mapped[list] = mapped_column(JSONB, default=list)
    rules: Mapped[list] = mapped_column(JSONB, default=list)
    default_tests: Mapped[list] = mapped_column(JSONB, default=list)
    differentials: Mapped[list] = mapped_column(JSONB, default=list)
    red_flags: Mapped[list] = mapped_column(JSONB, default=list)
    ambulatory_flow: Mapped[list] = mapped_column(JSONB, default=list)
    emergency_flow: Mapped[list] = mapped_column(JSONB, default=list)

    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    source_refs: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    source_urls: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    review_status: Mapped[str] = mapped_column(String(40), default="pendente_revisao", index=True)
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
