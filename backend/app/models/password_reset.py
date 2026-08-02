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
    seguro (mesma lógica de confiança já usada na criação manual de conta).

    `alvo` — reaproveitado a partir de 30/07/2026 para a senha da caixa de
    e-mail (Tarefa 28), que é distinta da senha da conta Corvia: 'conta'
    redefine `users.password_hash` (comportamento original, único que existia
    antes), 'email' redefine `email_accounts.password_hash`. O link de
    recuperação SEMPRE vai para o e-mail principal do médico (`users.email`),
    nunca para o próprio endereço @corvia.med.br — pedir para redefinir a
    senha de uma caixa mandando o link para dentro dela mesma trancaria quem
    esqueceu a senha para sempre.

    'ativacao' — acrescentado em 02/08/2026 (e-mails transacionais, item 1 do
    spec): mesmo redirecionamento para `users.password_hash` que 'conta', mas
    também ativa a conta (`is_active = True`) ao ser usado — é o link de
    "ativar minha conta e criar senha" do e-mail de boas-vindas. Decisão do
    Rafael: nunca enviar senha por e-mail, só o link de uso único."""

    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    alvo: Mapped[str] = mapped_column(String(20), default="conta")  # conta | email | ativacao
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
