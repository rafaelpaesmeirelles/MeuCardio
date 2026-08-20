"""Envio de documento (receituário/documento gerado) ao destinatário, pela
conta de e-mail PADRÃO do próprio médico — Trabalho 11, ampliação de
06/08/2026.

Substitui, nas duas rotas que mandam link de documento por e-mail
(`/api/receituario/documentos/{id}/enviar-email`,
`/api/document-templates/gerados/{id}/enviar-email`), o envio anterior via
`services/notificar.tentar_enviar_email` — SMTP transacional da própria
Corvia, com credencial quebrada em produção (`535 Authentication Failed`,
já registrado em CLAUDE.md). Agora sai pela caixa do médico (mesma conta
padrão de envio do Trabalho 9): nativa CorvIA Mail/Mail360, ou qualquer
conta externa conectada com permissão de envio — Yahoo, iCloud, Google,
Microsoft.

S/MIME funciona nos quatro transportes em que a CorVIA controla o MIME:
Yahoo/iCloud por SMTP e Google/Microsoft pelas APIs oficiais de MIME bruto.
A caixa nativa Mail360 aceita apenas campos estruturados; quando a assinatura
é obrigatória, o envio falha explicitamente em vez de sair sem assinatura.
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

# Mesmos quatro provedores externos que `app/api/email.py` já reconhece
# para a caixa unificada (`PROVEDORES_EXTERNOS_MAIL`). Yahoo/iCloud usam
# SMTP; Google/Microsoft usam as respectivas APIs de MIME bruto.
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
        CalendarIntegration.id == integ_id, CalendarIntegration.owner_id == user.id,
        CalendarIntegration.enabled.is_(True), CalendarIntegration.status == "connected",
        CalendarIntegration.provider.in_(_PROVEDORES_EXTERNOS),
    ).first()


def suporta_smime(db: Session, user: User) -> bool:
    """Usado pelo frontend para só oferecer a opção quando ela vai
    funcionar — a conta padrão precisa aceitar MIME bruto e ter `send_mail`."""
    integracao = _integracao_padrao_externa(db, user)
    return bool(
        integracao
        and integracao.provider in _PROVEDORES_EXTERNOS
        and (integracao.capabilities or {}).get("send_mail")
    )


def enviar(
    db: Session, user: User, *, destinatario: str, assunto: str, corpo_html: str,
    assinar_smime: bool = False,
) -> ResultadoEnvio:
    integracao = _integracao_padrao_externa(db, user)
    certificado = certificado_a1.obter(db, user)
    assinatura_obrigatoria = bool(
        assinar_smime or user.email_assinatura_digital_ativa
    )
    if assinatura_obrigatoria and certificado is None:
        return ResultadoEnvio(
            False,
            "Não há certificado A1 conectado para assinar digitalmente este e-mail.",
        )

    if integracao is None:
        # Conta padrão é a nativa (ou nenhuma preferência gravada — mesmo
        # default de `GET /contas`, "corvia").
        conta = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
        if not conta or conta.status != "ativa":
            return ResultadoEnvio(False, "Sua caixa do CorvIA Mail não está ativa.")
        if assinatura_obrigatoria:
            return ResultadoEnvio(
                False,
                "A caixa nativa CorVIA/Mail360 não aceita S/MIME. Selecione Google, Microsoft, Yahoo ou iCloud como conta padrão.",
            )
        try:
            mail360.enviar_mensagem(
                conta.mail360_account_key, conta.email_address, destinatario, assunto, corpo_html,
            )
            return ResultadoEnvio(True, assinado_smime=False)
        except Mail360Error as e:
            return ResultadoEnvio(False, str(e))

    if not (integracao.capabilities or {}).get("send_mail"):
        return ResultadoEnvio(False, "Sua conta padrão de envio não tem permissão de envio.")

    modulo_imap = _PROVEDORES_IMAP.get(integracao.provider)
    if modulo_imap:
        try:
            resultado = modulo_imap.send_message(
                integration_credentials(integracao), to=destinatario, subject=assunto, html=corpo_html,
                db=db, user=user, assinar_smime=assinatura_obrigatoria,
            )
        except (YahooMailError, AppleMailError) as e:
            return ResultadoEnvio(False, str(e))
        return ResultadoEnvio(True, assinado_smime=bool(resultado.get("assinado_smime")))

    try:
        resultado = external_mail.send_message(
            db, integracao, to=destinatario, subject=assunto, html=corpo_html,
            user=user, assinar_smime=assinatura_obrigatoria,
        )
    except ExternalMailError as e:
        return ResultadoEnvio(False, str(e))
    return ResultadoEnvio(True, assinado_smime=bool(resultado.get("assinado_smime")))
