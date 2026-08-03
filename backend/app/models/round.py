from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    record_number: Mapped[str] = mapped_column(String(60), index=True)  # prontuário
    initials: Mapped[str] = mapped_column(String(20))
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sex: Mapped[str | None] = mapped_column(String(1), nullable=True)
    bed: Mapped[str | None] = mapped_column(String(40), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(60), nullable=True)  # UTI, enfermaria...
    admission_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="internado")  # internado|alta

    # --- dados clínicos estruturados ---------------------------------------
    chief_complaint: Mapped[str | None] = mapped_column(Text, nullable=True)  # queixa principal
    anamnesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    physical_exam: Mapped[str | None] = mapped_column(Text, nullable=True)  # texto livre, achados gerais
    cardiac_exam: Mapped[dict] = mapped_column(JSONB, default=dict)
    # exame físico cardiológico estruturado — ex.:
    # {"ritmo": "regular", "bulhas": "normofoneticas", "b3": false, "b4": false,
    #  "sopro": true, "sopro_detalhes": "sistólico, foco mitral, 3+/6, irradia p/ axila",
    #  "ictus": "normolocalizado, normodinâmico", "turgencia_jugular": "ausente",
    #  "edema_mmii": "+2/4", "pulsos_perifericos": "cheios e simétricos",
    #  "perfusao_periferica": "TEC < 2s"}
    vital_signs: Mapped[dict] = mapped_column(JSONB, default=dict)
    # ex.: {"pa_sistolica": 130, "pa_diastolica": 80, "fc": 88, "fr": 18,
    #       "temperatura": 36.5, "spo2": 97, "glicemia": 110}
    imaging: Mapped[str | None] = mapped_column(Text, nullable=True)  # achados de imagem, texto livre
    diagnostic_hypothesis: Mapped[list] = mapped_column(JSONB, default=list)  # lista de strings

    labs: Mapped[dict] = mapped_column(JSONB, default=dict)
    medications: Mapped[list] = mapped_column(JSONB, default=list)
    plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    pending: Mapped[list] = mapped_column(JSONB, default=list)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    # Dono clínico do registro. O papel administrativo não concede leitura ou
    # alteração transversal: administração da plataforma e acesso ao prontuário
    # são capacidades distintas.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

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
    """Sugestão gerada pela IA a partir do caso — NUNCA gravada como fato no
    prontuário. Fica registrada à parte, sempre rotulada como sugestão que
    exige validação clínica, com o snapshot dos dados que foram enviados
    (para auditoria: saber exatamente o que saiu para o provedor externo)."""

    __tablename__ = "patient_ai_suggestions"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"))
    requested_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    case_snapshot: Mapped[dict] = mapped_column(JSONB)  # exatamente o que foi enviado à IA
    differential_diagnosis: Mapped[str] = mapped_column(Text)
    suggested_workup: Mapped[str] = mapped_column(Text)
    treatment_considerations: Mapped[str] = mapped_column(Text)
    sources: Mapped[list] = mapped_column(JSONB, default=list)  # documentos da biblioteca usados como base
    sources_pubmed: Mapped[list] = mapped_column(JSONB, default=list)  # artigos externos (PubMed) usados como base
    model: Mapped[str] = mapped_column(String(80))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    patient: Mapped[Patient] = relationship(back_populates="ai_suggestions")
