"""Registro de envio de e-mail transacional (02/08/2026).

Deliberadamente sem corpo e sem token: o que este log responde é "foi enviado,
quando, deu certo?" — não é cópia do conteúdo, que já vive só na caixa do
destinatário. `chave_idempotencia` existe para não duplicar envio quando o
webhook do Stripe reentrega o mesmo evento — único por (tipo, chave), quando
a chave é informada; envios sem gatilho idempotente (ex.: clique manual de
"reenviar ativação") deixam a chave nula e não são deduplicados.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class EmailLog(Base):
    __tablename__ = "email_logs"

    __table_args__ = (
        Index(
            "uq_email_log_idempotencia",
            "tipo",
            "chave_idempotencia",
            unique=True,
            postgresql_where="chave_idempotencia IS NOT NULL",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[str] = mapped_column(String(60), index=True)
    destinatario: Mapped[str] = mapped_column(String(255), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    chave_idempotencia: Mapped[str | None] = mapped_column(String(120), nullable=True)
    sucesso: Mapped[bool] = mapped_column(Boolean, default=False)
    erro: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
