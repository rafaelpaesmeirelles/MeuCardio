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


def _admins_ativos(db):
    from app.models.user import User
    return db.query(User).filter(User.role == "admin", User.is_active.is_(True)).all()


def notificar_admins_nova_solicitacao(db, nome_solicitante: str, email_solicitante: str) -> None:
    """Avisa todos os admins ativos que há uma solicitação de acesso nova.
    Sem SMTP configurado, isso não faz nada — o contador na barra de admin
    (endpoint /api/admin/users?status=pendente) já cumpre esse papel."""
    if not settings.smtp_configurado:
        return
    corpo = (
        f"{nome_solicitante} ({email_solicitante}) solicitou acesso ao CorVIA Cardiology Spaces.\n"
        f"Revise em: {{DOMINIO}}/admin"
    )
    for admin in _admins_ativos(db):
        tentar_enviar_email(admin.email, "CorVIA — nova solicitação de acesso", corpo)


def notificar_admins_kyc_manual(db, *, nome: str, email: str, motivo: str) -> None:
    """Avisa que a validação automática não liberou o novo usuário.

    Documentos de identidade NUNCA são anexados ao e-mail: permanecem cifrados
    no cofre KYC e ficam disponíveis somente na ficha administrativa. Assim o
    admin recebe a pendência sem criar uma segunda cópia de PII em SMTP.
    """
    if not settings.smtp_configurado:
        return
    corpo = (
        f"A validação automática de cadastro de {nome} ({email}) não foi aprovada.\n\n"
        f"Motivo: {motivo}\n\n"
        "Todos os dados profissionais e documentos enviados estão disponíveis "
        "na fila KYC administrativa para decisão manual.\n"
        "Revise em: {DOMINIO}/admin"
    )
    for admin in _admins_ativos(db):
        tentar_enviar_email(admin.email, "CorVIA — cadastro exige revisão manual", corpo)
