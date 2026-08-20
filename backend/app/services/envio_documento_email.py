"""Envio de documento (receituário/documento gerado) ao destinatário, pela
conta de e-mail PADRÃO do próprio médico.

O PDF clínico mantém sua assinatura PAdES independentemente do transporte de
e-mail. S/MIME é uma camada adicional no envelope da mensagem e só é aplicada
quando a conta escolhida aceita MIME bruto (Yahoo, iCloud, Google ou
Microsoft). A preferência do perfil significa "assinar quando compatível";
não deve bloquear a caixa nativa CorVIA Mail/Mail360, que transporta o PDF
PAdES sem modificar seus bytes.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.agenda import CalendarIntegration
from app.models.email_account import EmailAccount
from app.models.user import User
from app.services import apple_mail, external_mail, mail360, yahoo_mail
from app.services.agenda_integrada.domain import integration_credentials
from app.services.apple_mail import AppleMailError
from app.services.assinatura import certificado_a1
from app.services.external_mail import ExternalMailError
from app.services.mail360 import Mail360Error
from app.services.yahoo_mail import YahooMailError

_PROVEDORES_IMAP = {"yahoo_mail": yahoo_mail, "apple_icloud": apple_mail}
_PROVEDORES_EXTERNOS = ("yahoo_mail", "apple_icloud", "google_calendar", "microsoft_365")


@dataclass
class ResultadoEnvio:
    enviado: bool
    erro: str | None = None
    assinado_smime: bool = False


def _integracao_padrao_externa(db: Session, user: User) -> CalendarIntegration | None:
    padrao = user.email_conta_padrao_envio
    if not padrao or padrao == "corvia":
        return None
    try:
        integ_id = int(padrao)
    except ValueError:
        return None
    return db.query(CalendarIntegration).filter(
        CalendarIntegration.id == integ_id,
        CalendarIntegration.owner_id == user.id,
        CalendarIntegration.enabled.is_(True),
        CalendarIntegration.status == "connected",
        CalendarIntegration.provider.in_(_PROVEDORES_EXTERNOS),
    ).first()


def suporta_smime(db: Session, user: User) -> bool:
    """A conta padrão precisa aceitar MIME bruto e ter ``send_mail``."""
    integracao = _integracao_padrao_externa(db, user)
    return bool(
        integracao
        and integracao.provider in _PROVEDORES_EXTERNOS
        and (integracao.capabilities or {}).get("send_mail")
    )


def enviar(
    db: Session,
    user: User,
    *,
    destinatario: str,
    assunto: str,
    corpo_html: str,
    assinar_smime: bool = False,
) -> ResultadoEnvio:
    integracao = _integracao_padrao_externa(db, user)

    if integracao is None:
        # Conta padrão nativa (ou nenhuma preferência gravada). O PDF clínico
        # já está assinado por PAdES; a preferência geral por S/MIME não torna
        # Mail360 incompatível com o envio. Só uma exigência explícita deste
        # envio deve falhar fechada.
        conta = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
        if not conta or conta.status != "ativa":
            return ResultadoEnvio(False, "Sua caixa do CorVIA Mail não está ativa.")
        if assinar_smime:
            return ResultadoEnvio(
                False,
                "Este envio exigiu S/MIME explicitamente, mas a caixa nativa CorVIA/Mail360 "
                "não aceita S/MIME neste transporte. Escolha uma conta externa compatível.",
            )
        try:
            mail360.enviar_mensagem(
                conta.mail360_account_key,
                conta.email_address,
                destinatario,
                assunto,
                corpo_html,
            )
            return ResultadoEnvio(True, assinado_smime=False)
        except Mail360Error as exc:
            return ResultadoEnvio(False, str(exc))

    if not (integracao.capabilities or {}).get("send_mail"):
        return ResultadoEnvio(False, "Sua conta padrão de envio não tem permissão de envio.")

    assinatura_obrigatoria = bool(assinar_smime or user.email_assinatura_digital_ativa)
    if assinatura_obrigatoria and certificado_a1.obter(db, user) is None:
        return ResultadoEnvio(
            False,
            "Não há certificado A1 conectado para assinar digitalmente este e-mail por S/MIME.",
        )

    modulo_imap = _PROVEDORES_IMAP.get(integracao.provider)
    if modulo_imap:
        try:
            resultado = modulo_imap.send_message(
                integration_credentials(integracao),
                to=destinatario,
                subject=assunto,
                html=corpo_html,
                db=db,
                user=user,
                assinar_smime=assinatura_obrigatoria,
            )
        except (YahooMailError, AppleMailError) as exc:
            return ResultadoEnvio(False, str(exc))
        return ResultadoEnvio(True, assinado_smime=bool(resultado.get("assinado_smime")))

    try:
        resultado = external_mail.send_message(
            db,
            integracao,
            to=destinatario,
            subject=assunto,
            html=corpo_html,
            user=user,
            assinar_smime=assinatura_obrigatoria,
        )
    except ExternalMailError as exc:
        return ResultadoEnvio(False, str(exc))
    return ResultadoEnvio(True, assinado_smime=bool(resultado.get("assinado_smime")))
