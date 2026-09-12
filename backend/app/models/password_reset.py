import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def gerar_token() -> str:
    return secrets.token_urlsafe(32)


class PasswordResetToken(Base):
    """Token temporário entregue somente ao canal do titular, nunca no painel.

    conta/ativacao alteram a senha app; email altera a senha da caixa.
    convite confirma posse do endereço pré-autorizado e define novas
    credenciais antes de ativar a conta. Links irmãos são consumidos juntos.
    """

    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    alvo: Mapped[str] = mapped_column(String(20), default="conta")  # conta | email | ativacao | convite
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
