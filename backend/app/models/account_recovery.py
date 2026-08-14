from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AccountRecoveryEmail(Base):
    """Endereço externo dedicado à recuperação da conta CorVIA.

    Fica separado de ``users.email`` de propósito: o e-mail de login pode ser
    uma caixa ``@corvia.med.br`` que depende do próprio acesso ao Clinical OS.
    O endereço de recuperação é único globalmente e nunca é usado como login
    normal; serve somente para recuperação/alertas de segurança.
    """

    __tablename__ = "account_recovery_emails"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
