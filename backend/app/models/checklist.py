from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class DischargeChecklist(Base):
    """Modelo de checklist de alta por doença ou procedimento."""

    __tablename__ = "discharge_checklists"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    condicao: Mapped[str] = mapped_column(String(200))
    resumo: Mapped[str | None] = mapped_column(Text, nullable=True)
    theme: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    scope_type: Mapped[str] = mapped_column(String(20), default="doenca", index=True)

    documento_origem: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    itens: Mapped[list] = mapped_column(JSONB, default=list)
    source_refs: Mapped[list] = mapped_column(JSONB, default=list)

    review_status: Mapped[str] = mapped_column(String(30), default="pendente_revisao")
    revisao: Mapped[str | None] = mapped_column(Text, nullable=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class DischargeChecklistRun(Base):
    """Aplicação imutável do modelo a uma alta concreta."""

    __tablename__ = "discharge_checklist_runs"
    __table_args__ = (
        UniqueConstraint("checklist_id", "user_id", "patient_id", "finalizado_em",
                         name="uq_run_checklist"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    checklist_id: Mapped[int] = mapped_column(
        ForeignKey("discharge_checklists.id"), index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    patient_id: Mapped[int | None] = mapped_column(
        ForeignKey("patients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    identificacao_livre: Mapped[str | None] = mapped_column(String(200), nullable=True)

    marcados: Mapped[list] = mapped_column(JSONB, default=list)
    itens_no_momento: Mapped[list] = mapped_column(JSONB, default=list)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    finalizado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
