"""Base oficial de médicos do CFM e trilha de sincronização.

O registro bruto fornecido pelo CFM é preservado. Campos derivados existem
somente para pesquisa/segurança e nunca substituem o conteúdo oficial.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class CfmSyncRun(Base):
    __tablename__ = "cfm_sync_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source_type: Mapped[str] = mapped_column(String(24), index=True)  # totalzip | webservice
    status: Mapped[str] = mapped_column(String(20), index=True, default="running")
    dataset_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    record_count: Mapped[int] = mapped_column(BigInteger, default=0)
    invalid_identifier_count: Mapped[int] = mapped_column(BigInteger, default=0)
    deactivated_count: Mapped[int] = mapped_column(BigInteger, default=0)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CfmPhysician(Base):
    """Uma inscrição profissional do CFM, identificada por UF + CRM bruto.

    ``crm_raw`` guarda exatamente o identificador do arquivo oficial.
    ``crm_consulta`` existe apenas quando o identificador pode ser enviado ao
    Web Service (número natural com até 7 dígitos). Isso permite conservar
    anomalias oficiais sem tratá-las como CRM válido.
    """

    __tablename__ = "cfm_physicians"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    uf: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    crm_raw: Mapped[str] = mapped_column(String(64), nullable=False)
    crm_consulta: Mapped[str | None] = mapped_column(String(7), nullable=True, index=True)
    crm_exibicao: Mapped[str | None] = mapped_column(String(64), nullable=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    tipo_inscricao_texto: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo_inscricao_codigo: Mapped[str | None] = mapped_column(String(8), nullable=True)
    situacao_texto: Mapped[str] = mapped_column(String(160), nullable=False)
    situacao_codigo: Mapped[str | None] = mapped_column(String(8), nullable=True, index=True)
    especialidades_raw: Mapped[str] = mapped_column(Text, default="")
    data_atualizacao_cfm: Mapped[date | None] = mapped_column(Date, nullable=True)

    identificador_valido: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    is_regular: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    source_last: Mapped[str] = mapped_column(String(24), nullable=False, default="totalzip")

    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora, index=True)
    last_live_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora, onupdate=_agora)
    last_seen_sync_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("cfm_sync_runs.id", ondelete="SET NULL"), nullable=True, index=True
    )

    __table_args__ = (
        UniqueConstraint("uf", "crm_raw", name="uq_cfm_physician_uf_crm_raw"),
        Index("ix_cfm_physicians_lookup_live", "uf", "crm_consulta", "is_current"),
        Index("ix_cfm_physicians_regular_current", "is_regular", "is_current"),
    )
