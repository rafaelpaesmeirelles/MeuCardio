"""Dispensas individuais de requisitos KYC para contas Convidado.

A configuração é administrativa e fail-closed: ausência de linha significa
nenhuma dispensa. As dispensas só são aplicadas quando ``User.convidado`` é
verdadeiro; assinantes normais continuam sujeitos ao KYC completo e Investidor
não participa do fluxo de KYC.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class KycRequirementWaiver(Base):
    __tablename__ = "kyc_requirement_waivers"

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    professional_front: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    professional_back: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    personal_front: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    personal_back: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    personal_digital: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    selfie: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_agora, onupdate=_agora, nullable=False
    )
