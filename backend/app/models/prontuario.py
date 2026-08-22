"""Núcleo longitudinal do Prontuário Eletrônico CorVIA.

`PatientProfile` continua sendo a identidade clínica ambulatorial. O conteúdo
clínico ligado a um paciente identificável fica cifrado em repouso.

Um atendimento finalizado é histórico: a API não permite sobrescrevê-lo.
Correções posteriores devem ser registradas como novo `ClinicalEncounter`
com `amendment_of_id` apontando para o registro original.

Problemas, alergias e medicações em uso seguem a mesma lógica conservadora:
o conteúdo é cifrado e um item deixa de ser vigente por inativação, nunca por
apagamento físico ou sobrescrita silenciosa.

Resultados de exames também são históricos e imutáveis. Uma correção é um novo
`PatientExamResult` que referencia o resultado anterior; nome, valor, unidade,
referência, observações e motivo da correção ficam cifrados em repouso.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, LargeBinary, String, UniqueConstraint
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


class PatientClinicalItem(Base):
    """Item longitudinal do resumo clínico do paciente.

    `kind` expõe somente a categoria operacional (problema/alergia/medicação).
    Nome e detalhes ficam dentro de `payload_cifrado`. O item é imutável quanto
    ao conteúdo; quando deixa de ser vigente, recebe `is_active=False` e
    `ended_at`, preservando o histórico médico.
    """

    __tablename__ = "patient_clinical_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    patient_profile_id: Mapped[int] = mapped_column(
        ForeignKey("patient_profiles.id", ondelete="RESTRICT"), index=True
    )
    source_encounter_id: Mapped[int | None] = mapped_column(
        ForeignKey("clinical_encounters.id", ondelete="SET NULL"), nullable=True, index=True
    )
    kind: Mapped[str] = mapped_column(String(20), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    payload_cifrado: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PatientExamResult(Base):
    """Resultado longitudinal de um exame de um `PatientProfile` identificável.

    `exam_kind` é apenas taxonomia operacional. Todo conteúdo clínico variável
    permanece no payload cifrado. `lab_test_id` é uma ponte opcional para o
    catálogo científico CorVIA, nunca a fonte de verdade do resultado emitido.
    """

    __tablename__ = "patient_exam_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    patient_profile_id: Mapped[int] = mapped_column(
        ForeignKey("patient_profiles.id", ondelete="RESTRICT"), index=True
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    source_encounter_id: Mapped[int | None] = mapped_column(
        ForeignKey("clinical_encounters.id", ondelete="SET NULL"), nullable=True, index=True
    )
    lab_test_id: Mapped[int | None] = mapped_column(
        ForeignKey("lab_tests.id", ondelete="SET NULL"), nullable=True, index=True
    )
    correction_of_id: Mapped[int | None] = mapped_column(
        ForeignKey("patient_exam_results.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    exam_kind: Mapped[str] = mapped_column(String(30), index=True)
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    payload_cifrado: Mapped[bytes] = mapped_column(LargeBinary)
    correction_reason_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)

    __table_args__ = (
        UniqueConstraint(
            "correction_of_id",
            name="uq_patient_exam_results_correction_of",
        ),
        CheckConstraint(
            "exam_kind IN ('laboratorial', 'metodo_grafico', 'imagem', 'outro')",
            name="ck_patient_exam_results_kind",
        ),
        CheckConstraint(
            "correction_of_id IS NULL OR correction_of_id <> id",
            name="ck_patient_exam_results_not_self_correction",
        ),
    )
