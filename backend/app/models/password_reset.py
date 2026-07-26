import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def gerar_token() -> str:
    return secrets.token_urlsafe(32)


class PasswordResetToken(Base):
    """Token de redefinição de senha. Sem envio de e-mail configurado ainda —
    o link fica visível para um admin no painel, que repassa por um canal
    seguro (mesma lógica de confiança já usada na criação manual de conta)."""

    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, default=gerar_token)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc) + timedelta(hours=2)
    )
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    @property
    def valido(self) -> bool:
        return not self.used and datetime.now(timezone.utc) < self.expires_at
