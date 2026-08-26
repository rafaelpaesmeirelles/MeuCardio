from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class UserAccess(Base):
    """Login/sessao auditavel sem armazenar credenciais ou conteudo clinico."""

    __tablename__ = "user_accesses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    surface: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    successful: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_reason: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    operating_system: Mapped[str | None] = mapped_column(String(80), nullable=True)
    browser: Mapped[str | None] = mapped_column(String(80), nullable=True)
    device_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(12), nullable=False, default="normal", index=True)
    risk_reasons: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
