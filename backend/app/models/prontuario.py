"""Núcleo longitudinal do Prontuário Eletrônico CorVIA.

`PatientProfile` continua sendo a identidade clínica ambulatorial. O conteúdo
clínico de um atendimento fica cifrado em repouso porque, diferente do Patient
do Round, este registro está ligado diretamente a um paciente identificável.

Um atendimento finalizado é histórico: a API não permite sobrescrevê-lo.
Correções posteriores devem ser registradas como novo `ClinicalEncounter`
com `amendment_of_id` apontando para o registro original.
"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, LargeBinary, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class ClinicalEncounter(Base):
    __tablename__ = "clinical_encounters"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    patient_profile_id: Mapped[int] = mapped_column(
        ForeignKey("patient_profiles.id", ondelete="RESTRICT"), index=True
    )
    appointment_id: Mapped[int | None] = mapped_column(
        ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )

    encounter_type: Mapped[str] = mapped_column(String(40), default="consulta")
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Adendo: registro novo, nunca edição retroativa do original finalizado.
    amendment_of_id: Mapped[int | None] = mapped_column(
        ForeignKey("clinical_encounters.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    amendment_reason_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    # Conteúdo clínico cifrado em repouso com AES-256-GCM via app.services.cofre.
    chief_complaint_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    anamnesis_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    physical_exam_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    assessment_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    plan_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    vital_signs_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_agora, onupdate=_agora
    )

    __table_args__ = (
        # Um agendamento local pode iniciar no máximo um atendimento primário.
        # PostgreSQL permite múltiplos NULL; adendos não reutilizam appointment_id.
        UniqueConstraint("owner_id", "appointment_id", name="uq_encounter_owner_appointment"),
    )
