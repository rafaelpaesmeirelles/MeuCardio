from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    record_number: Mapped[str] = mapped_column(String(60), index=True)
    initials: Mapped[str] = mapped_column(String(20))
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sex: Mapped[str | None] = mapped_column(String(1), nullable=True)
    bed: Mapped[str | None] = mapped_column(String(40), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(60), nullable=True)
    admission_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="internado")

    chief_complaint: Mapped[str | None] = mapped_column(Text, nullable=True)
    anamnesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    physical_exam: Mapped[str | None] = mapped_column(Text, nullable=True)
    cardiac_exam: Mapped[dict] = mapped_column(JSONB, default=dict)
    vital_signs: Mapped[dict] = mapped_column(JSONB, default=dict)
    imaging: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnostic_hypothesis: Mapped[list] = mapped_column(JSONB, default=list)
    labs: Mapped[dict] = mapped_column(JSONB, default=dict)
    medications: Mapped[list] = mapped_column(JSONB, default=list)
    plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    pending: Mapped[list] = mapped_column(JSONB, default=list)

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    archived_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    archive_reason: Mapped[str | None] = mapped_column(String(300), nullable=True)

    problems: Mapped[list["PatientProblem"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )
    notes: Mapped[list["PatientNote"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )
    ai_suggestions: Mapped[list["PatientAISuggestion"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )


class PatientProblem(Base):
    __tablename__ = "patient_problems"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"))
    label: Mapped[str] = mapped_column(String(300))
    status: Mapped[str] = mapped_column(String(30), default="ativo")
    patient: Mapped[Patient] = relationship(back_populates="problems")


class PatientNote(Base):
    __tablename__ = "patient_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"))
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    patient: Mapped[Patient] = relationship(back_populates="notes")


class PatientAISuggestion(Base):
    __tablename__ = "patient_ai_suggestions"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"))
    requested_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    case_snapshot: Mapped[dict] = mapped_column(JSONB)
    differential_diagnosis: Mapped[str] = mapped_column(Text)
    suggested_workup: Mapped[str] = mapped_column(Text)
    treatment_considerations: Mapped[str] = mapped_column(Text)
    sources: Mapped[list] = mapped_column(JSONB, default=list)
    sources_pubmed: Mapped[list] = mapped_column(JSONB, default=list)
    model: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    patient: Mapped[Patient] = relationship(back_populates="ai_suggestions")
