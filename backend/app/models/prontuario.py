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

Arquivos originais de exames ficam fora do banco, cifrados no cofre de arquivos.
O banco guarda somente metadados operacionais e o nome original cifrado. O
anexo é imutável e sempre pertence a um `PatientExamResult` já existente.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, LargeBinary, String, UniqueConstraint
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

    amendment_of_id: Mapped[int | None] = mapped_column(
        ForeignKey("clinical_encounters.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    amendment_reason_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

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
        UniqueConstraint("owner_id", "appointment_id", name="uq_encounter_owner_appointment"),
    )


class PatientClinicalItem(Base):
    """Item longitudinal do resumo clínico do paciente."""

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
    """Resultado longitudinal de um exame de um `PatientProfile` identificável."""

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


class PatientExamAttachment(Base):
    """Arquivo original ligado a um resultado de exame.

    `storage_name` é UUID aleatório do cofre, não dado do paciente. O nome de
    origem é cifrado para não vazar PHI por metadado do banco. Não existe
    exclusão/edição pública: um anexo clínico é histórico.
    """

    __tablename__ = "patient_exam_attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    exam_result_id: Mapped[int] = mapped_column(
        ForeignKey("patient_exam_results.id", ondelete="RESTRICT"), index=True
    )
    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    storage_name: Mapped[str] = mapped_column(String(80), unique=True)
    mime_type: Mapped[str] = mapped_column(String(80))
    size_bytes: Mapped[int] = mapped_column(Integer)
    original_name_cifrado: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
