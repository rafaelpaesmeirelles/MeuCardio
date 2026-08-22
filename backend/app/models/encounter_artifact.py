"""Vínculo explícito entre Encounter e artefatos clínicos já existentes.

Receituário e Documentos continuam donos de seus próprios snapshots, assinatura
e regras legais. Esta tabela não duplica conteúdo: apenas registra que uma
prescrição ou documento foi produzido no contexto de um ClinicalEncounter.
"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class EncounterArtifact(Base):
    __tablename__ = "encounter_artifacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    encounter_id: Mapped[int] = mapped_column(
        ForeignKey("clinical_encounters.id", ondelete="CASCADE"), index=True
    )
    artifact_type: Mapped[str] = mapped_column(String(20), index=True)
    artifact_id: Mapped[int] = mapped_column(Integer, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)

    __table_args__ = (
        UniqueConstraint(
            "owner_id", "artifact_type", "artifact_id",
            name="uq_encounter_artifact_owner_type_id",
        ),
    )
