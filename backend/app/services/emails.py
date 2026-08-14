"""Roteador de transporte para e-mails institucionais do CorVIA.

O conteúdo/template e as funções públicas permanecem no módulo histórico
``emails_legacy`` sem alteração. Este arquivo troca somente a camada de
transporte: Mail360 Native institucional ou SMTP. A separação mantém o hotfix
pequeno e auditável e evita duplicar regras de token, idempotência e EmailLog.
"""

from __future__ import annotations

import logging

from app.services import emails_legacy as _legacy
from app.services.emails_legacy import *  # noqa: F401,F403
from app.services.mail360 import Mail360Error, enviar_mensagem as enviar_mensagem_mail360

log = logging.getLogger("meucardio.emails")

# Compatibilidade explícita para testes e consumidores que acessam os helpers
# internos do módulo histórico.
settings = _legacy.settings
smtplib = _legacy.smtplib
_renderizar = _legacy._renderizar
_montar_mensagem = _legacy._montar_mensagem
_smtp_enviar = _legacy._smtp_enviar
_ja_enviado = _legacy._ja_enviado
_registrar_log = _legacy._registrar_log
_reply_to_da_plataforma = _legacy._reply_to_da_plataforma
_texto_simples_de_html = _legacy._texto_simples_de_html


def _mail360_enviar(destinatario: str, assunto: str, html: str) -> tuple[bool, str | None]:
    """Envia pela caixa Native institucional ``contato@corvia.med.br``."""
    remetente = _reply_to_da_plataforma()
    html_mail360 = html.replace(
        "cid:corvia-logo",
        f"{settings.public_url.rstrip('/')}/corvia-logo.png",
    )
    try:
        enviar_mensagem_mail360(
            settings.mail360_transactional_account_key,
            remetente,
            destinatario,
            assunto,
            html_mail360,
            mail_format="html",
        )
        return True, None
    except Mail360Error as exc:
        # Mail360Error já traduz falhas do provedor sem incluir token/secret.
        log.warning("Falha Mail360 transacional para %s: %s", destinatario, exc)
        return False, str(exc)
    except Exception as exc:  # noqa: BLE001
        # Não persistir a mensagem arbitrária de uma exceção inesperada.
        log.exception("Falha inesperada no Mail360 transacional para %s", destinatario)
        return False, f"Mail360: {type(exc).__name__}"


def _enviar_por_provider(
    destinatario: str,
    assunto: str,
    html: str,
    texto: str,
) -> tuple[bool, str | None]:
    provider = settings.email_transacional_provider_efetivo
    if provider == "mail360":
        return _mail360_enviar(destinatario, assunto, html)
    if provider == "smtp":
        msg = _montar_mensagem(destinatario, assunto, html, texto)
        return _smtp_enviar(msg)
    return False, "Canal transacional não configurado"


def _enviar(
    db,
    *,
    tipo: str,
    destinatario: str,
    assunto: str,
    template: str,
    contexto: dict,
    user_id: int | None = None,
    chave_idempotencia: str | None = None,
) -> bool:
    """Pipeline transacional comum, preservando idempotência e EmailLog."""
    if _ja_enviado(db, tipo, chave_idempotencia):
        log.info("E-mail %s já enviado antes (chave=%s) — não duplicado", tipo, chave_idempotencia)
        return True
    if not settings.email_transacional_configurado:
        erro = "Canal transacional não configurado"
        log.info("%s — e-mail %s para %s não enviado", erro, tipo, destinatario)
        _registrar_log(db, tipo, destinatario, user_id, chave_idempotencia, False, erro)
        return False
    try:
        html, texto = _renderizar(template, {**contexto, "assunto": assunto})
    except Exception as exc:  # noqa: BLE001
        log.exception("Falha ao renderizar template de e-mail %s", template)
        _registrar_log(
            db,
            tipo,
            destinatario,
            user_id,
            chave_idempotencia,
            False,
            f"erro de template: {exc}",
        )
        return False
    sucesso, erro = _enviar_por_provider(destinatario, assunto, html, texto)
    _registrar_log(db, tipo, destinatario, user_id, chave_idempotencia, sucesso, erro)
    return sucesso


def enviar_institucional_paciente(
    db,
    *,
    user_id: int,
    destinatario: str,
    assunto: str,
    html: str,
    tipo_log: str,
) -> ResultadoEnvioInstitucional:
    """Envia material institucional pelo mesmo provider transacional."""
    if not settings.email_transacional_configurado:
        erro = "Canal transacional não configurado"
        _registrar_log(db, tipo_log, destinatario, user_id, None, False, erro)
        return ResultadoEnvioInstitucional(
            False,
            "O envio automático pela Corvia ainda não está disponível neste servidor.",
        )
    texto = _texto_simples_de_html(html)
    sucesso, erro = _enviar_por_provider(destinatario, assunto, html, texto)
    _registrar_log(db, tipo_log, destinatario, user_id, None, sucesso, erro)
    return ResultadoEnvioInstitucional(sucesso, erro)


# As funções públicas importadas acima foram definidas em emails_legacy e,
# portanto, consultam o namespace daquele módulo ao executar. Redirecionar o
# helper ali garante que todas elas usem este transporte sem reescrever o
# conteúdo científico/contratual dos templates nem a lógica dos tokens.
_legacy._enviar = _enviar
_legacy.enviar_institucional_paciente = enviar_institucional_paciente
