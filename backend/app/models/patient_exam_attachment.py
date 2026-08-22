"""Arquivo original vinculado a um resultado de exame do PatientProfile.

O binário fica cifrado no volume de exames via `app.services.cofre`. O nome
original também é cifrado porque pode conter dado identificável do paciente.
O registro é histórico: não existe operação de sobrescrita ou exclusão pela API.
"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class PatientExamAttachment(Base):
    __tablename__ = "patient_exam_attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    patient_exam_result_id: Mapped[int] = mapped_column(
        ForeignKey("patient_exam_results.id", ondelete="RESTRICT"), index=True
    )
    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    storage_name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    original_name_cifrado: Mapped[bytes] = mapped_column(LargeBinary)
    mime_type: Mapped[str] = mapped_column(String(80))
    size_bytes: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
