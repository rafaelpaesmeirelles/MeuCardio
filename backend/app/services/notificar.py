"""Avisos de acesso pelo transporte institucional e envio SMTP legado.

Avisos transacionais usam o provider configurado e o registro de envio do
serviço de e-mails. O helper SMTP permanece para os demais alertas legados.
Falhas de envio não interrompem a recuperação de acesso nem a revisão KYC.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from html import escape

from app.core.config import settings
from app.core.db import SessionLocal
from app.services import emails

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


def tentar_enviar_email_transacional(
    destinatario: str,
    assunto: str,
    corpo: str,
    *,
    user_id: int,
    tipo_log: str,
    link: str | None = None,
) -> bool:
    """Adapta avisos textuais de acesso ao pipeline institucional.

    ``link`` é a URL construída pelo chamador, nunca HTML fornecido pelo
    usuário. A sessão própria impede que o commit de EmailLog confirme uma
    transação de cadastro/KYC ainda em andamento na sessão do chamador.
    """
    try:
        corpo = corpo.replace("{DOMINIO}", settings.public_url)
        html = "<p>" + escape(corpo).replace("\n", "<br>") + "</p>"
        if link:
            url = escape(link.replace("{DOMINIO}", settings.public_url), quote=True)
            html = html.replace(url, f'<a href="{url}">{url}</a>')
        with SessionLocal() as db:
            resultado = emails.enviar_institucional_paciente(
                db,
                user_id=user_id,
                destinatario=destinatario,
                assunto=assunto,
                html=html,
                tipo_log=tipo_log,
            )
            return resultado.enviado
    except Exception as exc:
        # Não registrar corpo, token, endereço nem detalhe do erro do provider.
        log.warning("Falha no aviso transacional %s (%s)", tipo_log, type(exc).__name__)
        return False


def _admins_ativos(db):
    from app.models.user import User
    return db.query(User).filter(User.role == "admin", User.is_active.is_(True)).all()


def notificar_admins_nova_solicitacao(db, nome_solicitante: str, email_solicitante: str) -> None:
    """Avisa admins ativos pelo canal institucional; o painel segue disponível."""
    corpo = (
        f"{nome_solicitante} ({email_solicitante}) solicitou acesso ao CorVIA Cardiology Spaces.\n"
        f"Revise em: {{DOMINIO}}/admin"
    )
    for admin in _admins_ativos(db):
        tentar_enviar_email_transacional(
            admin.email, "CorVIA — nova solicitação de acesso", corpo,
            user_id=admin.id, tipo_log="admin_nova_solicitacao", link="{DOMINIO}/admin",
        )


def notificar_admins_kyc_manual(db, *, nome: str, email: str, motivo: str) -> None:
    """Avisa que a validação automática não liberou o novo usuário.

    Documentos de identidade NUNCA são anexados ao e-mail: permanecem cifrados
    no cofre KYC e ficam disponíveis somente na ficha administrativa. Assim o
    admin recebe a pendência sem enviar cópias dos documentos por e-mail.
    """
    corpo = (
        f"A validação automática de cadastro de {nome} ({email}) não foi aprovada.\n\n"
        f"Motivo: {motivo}\n\n"
        "Todos os dados profissionais e documentos enviados estão disponíveis "
        "na fila KYC administrativa para decisão manual.\n"
        "Revise em: {DOMINIO}/admin"
    )
    for admin in _admins_ativos(db):
        tentar_enviar_email_transacional(
            admin.email, "CorVIA — cadastro exige revisão manual", corpo,
            user_id=admin.id, tipo_log="admin_kyc_manual", link="{DOMINIO}/admin",
        )
