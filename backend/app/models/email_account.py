from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class EmailAccount(Base):
    """Caixa de e-mail do assinante, provisionada no Zoho Mail360.

    `mail360_account_key` é o identificador que o Mail360 devolve na criação
    da conta nativa — é ele, não o e-mail, que entra em toda chamada
    subsequente à API (mensagens, pastas). Guardar os dois evita ter que
    reconsultar o Mail360 só para descobrir a chave a partir do endereço.

    `password_hash` — decisão do Rafael em 30/07/2026: a caixa de e-mail
    passou a ter senha PRÓPRIA, distinta da senha da conta Corvia (`users.
    password_hash`). É essa senha que autentica `POST /api/email/entrar`,
    a "sessão email" separada — ver `core/security.py` (token com
    `scope: "email"`) e `BRIEFING_CLAUDE_CODE_4.md` para o histórico da
    decisão. Nasce nula: só é definida quando o médico ativa a caixa pela
    primeira vez (`POST /api/email/conta`), depois de a assinatura de e-mail
    já estar ativa.
    """

    __tablename__ = "email_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    email_address: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    mail360_account_key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ativa")  # ativa | suspensa
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
