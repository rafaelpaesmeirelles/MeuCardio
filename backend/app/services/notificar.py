"""Envio de e-mail opcional. Se SMTP não estiver configurado no .env, todas
as funções aqui retornam False silenciosamente — nada quebra, o sistema só
passa a depender do painel de admin para esses avisos (reset de senha,
solicitação de acesso), como já acontecia antes desta funcionalidade existir.
"""

import logging
import smtplib
from email.mime.text import MIMEText

from app.core.config import settings

log = logging.getLogger("meucardio.notificar")


def tentar_enviar_email(destinatario: str, assunto: str, corpo: str) -> bool:
    if not settings.smtp_configurado:
        log.info("SMTP não configurado — e-mail para %s não enviado (%s)", destinatario, assunto)
        return False

    corpo = corpo.replace("{DOMINIO}", settings.public_url)
    msg = MIMEText(corpo, "plain", "utf-8")
    msg["Subject"] = assunto
    msg["From"] = settings.smtp_from
    msg["To"] = destinatario

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as servidor:
            servidor.starttls()
            servidor.login(settings.smtp_user, settings.smtp_password)
            servidor.send_message(msg)
        return True
    except Exception:
        log.exception("Falha ao enviar e-mail para %s", destinatario)
        return False


def notificar_admins_nova_solicitacao(db, nome_solicitante: str, email_solicitante: str) -> None:
    """Avisa todos os admins ativos que há uma solicitação de acesso nova.
    Sem SMTP configurado, isso não faz nada — o contador na barra de admin
    (endpoint /api/admin/users?status=pendente) já cumpre esse papel."""
    from app.models.user import User

    if not settings.smtp_configurado:
        return
    admins = db.query(User).filter(User.role == "admin", User.is_active.is_(True)).all()
    corpo = (
        f"{nome_solicitante} ({email_solicitante}) solicitou acesso ao MeuCardio.\n"
        f"Revise em: {{DOMINIO}}/admin"
    )
    for admin in admins:
        tentar_enviar_email(admin.email, "MeuCardio — nova solicitação de acesso", corpo)
