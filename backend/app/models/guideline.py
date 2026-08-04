from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Guideline(Base):
    """Diretriz oficial e seus metadados de descoberta/revisão."""

    __tablename__ = "guidelines"
    __table_args__ = (UniqueConstraint("slug", name="uq_guideline_slug"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), index=True)
    org: Mapped[str] = mapped_column(String(40), index=True)
    titulo: Mapped[str] = mapped_column(String(300))
    ano: Mapped[int] = mapped_column(Integer, index=True)
    tema: Mapped[str | None] = mapped_column(String(120), nullable=True)
    doi: Mapped[str | None] = mapped_column(String(160), nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    source_fingerprint: Mapped[str | None] = mapped_column(
        String(64), nullable=True, unique=True, index=True
    )
    detection_status: Mapped[str] = mapped_column(String(30), default="manual")
    # manual | detected | aguardando_revisao | revisada

    superseded_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("guidelines.id"), nullable=True, index=True
    )
    substituida_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    alerta_enviado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class GuidelineLink(Base):
    """Liga uma diretriz a um item de conteúdo sem alterar o item automaticamente."""

    __tablename__ = "guideline_links"
    __table_args__ = (
        UniqueConstraint(
            "guideline_id", "item_type", "item_id", name="uq_vinculo_diretriz"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    guideline_id: Mapped[int] = mapped_column(
        ForeignKey("guidelines.id", ondelete="CASCADE"), index=True
    )
    item_type: Mapped[str] = mapped_column(String(30), index=True)
    item_id: Mapped[int] = mapped_column(index=True)
    origem: Mapped[str] = mapped_column(String(20), default="extraido")
    confirmado: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    trecho: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class GuidelineNotification(Base):
    """Entrega idempotente do alerta factual por assinante e canal."""

    __tablename__ = "guideline_notifications"
    __table_args__ = (
        UniqueConstraint(
            "guideline_id", "user_id", "channel",
            name="uq_guideline_notification_delivery",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    guideline_id: Mapped[int] = mapped_column(
        ForeignKey("guidelines.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    channel: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="pendente")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
