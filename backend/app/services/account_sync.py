"""Sincronização/heartbeat de uma conta externa, por capacidade.

A ação manual e o worker contínuo precisam obedecer à mesma regra. Uma conta
Yahoo, por exemplo, não possui calendário; chamar ``sync_integration`` nela é
um erro conceitual. Para contas mail-only, "sincronizar" significa verificar a
credencial e manter a leitura proxy pronta. Google/Microsoft renovam OAuth
automaticamente; calendário/contatos usam os syncs incrementais existentes.

Erros transitórios NÃO desconectam a conta. Somente falhas explícitas de
credencial/consentimento mudam o estado para ``reauth_required``.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.agenda import CalendarIntegration
from app.services import apple_mail, yahoo_mail
from app.services.agenda_integrada.connectors import ConnectorError
from app.services.agenda_integrada.contacts import sync_contacts
from app.services.agenda_integrada.domain import integration_credentials, sync_integration
from app.services.agenda_integrada.external_accounts import ensure_fresh_credentials

PROVEDORES_OAUTH = {"google_calendar", "microsoft_365"}
PROVEDORES_IMAP = {"yahoo_mail", "apple_icloud"}
ERROS_REAUTENTICACAO = {
    "reauth_required", "invalid_grant", "interaction_required", "consent_required",
    "oauth_refresh_token_missing",
}


def _erro_dict(componente: str, codigo: str, mensagem: str, *, reauth: bool = False) -> dict[str, Any]:
    return {
        "componente": componente,
        "ok": False,
        "codigo": codigo,
        "mensagem": mensagem,
        "reauth_required": reauth,
    }


def _ok_dict(componente: str, detalhe: Any = None) -> dict[str, Any]:
    return {"componente": componente, "ok": True, "detalhe": detalhe}


def _marcar_erro(db: Session, item: CalendarIntegration, codigo: str, mensagem: str, *, reauth: bool) -> None:
    item.status = "reauth_required" if reauth else "connected"
    item.last_error_code = codigo
    item.last_error_message = mensagem[:500]
    item.last_sync_finished_at = datetime.now(timezone.utc)
    db.commit()


def _marcar_sucesso(db: Session, item: CalendarIntegration) -> None:
    agora = datetime.now(timezone.utc)
    item.status = "connected"
    item.last_error_code = None
    item.last_error_message = None
    item.last_sync_finished_at = agora
    item.last_success_at = agora
    db.commit()


def _heartbeat_mail(db: Session, item: CalendarIntegration) -> dict[str, Any]:
    if item.provider in PROVEDORES_OAUTH:
        ensure_fresh_credentials(db, item)
        return {"modo": "oauth", "provider": item.provider}
    if item.provider == "yahoo_mail":
        return {**yahoo_mail.diagnose(integration_credentials(item)), "modo": "imap"}
    if item.provider == "apple_icloud":
        return {**apple_mail.diagnose(integration_credentials(item)), "modo": "imap"}
    raise ConnectorError("mail_not_supported", "Este provedor não possui heartbeat de e-mail homologado.", status_code=409)


def sincronizar_conta(db: Session, item: CalendarIntegration, *, full: bool = False) -> dict[str, Any]:
    """Executa somente os componentes que a conta realmente suporta.

    Retorna 200-style payload mesmo quando um componente transitório falha;
    quem chama consegue mostrar a pendência sem fazer o botão parecer inerte.
    ``reauth_required`` continua explícito no payload e no estado persistido.
    """
    if not settings.agenda_integrations_enabled:
        raise ConnectorError("integration_disabled", "Integrações externas estão desativadas.", status_code=409)
    if not item.enabled:
        raise ConnectorError("integration_disabled", "Esta conta está desconectada. Reconecte para sincronizar.", status_code=409)
    if item.status == "reauth_required":
        raise ConnectorError("reauth_required", "A conta precisa ser reconectada para renovar a autorização.", status_code=409)

    capacidades = item.capabilities or {}
    componentes: list[dict[str, Any]] = []
    algum_aplicavel = False
    teve_sucesso = False
    reauth = False

    # Heartbeat/renovação de e-mail. Gmail/Outlook não copiam mensagem para o
    # banco: a caixa externa é proxy ao vivo. O heartbeat prova que a conexão
    # continua válida e renova OAuth antes de expirar.
    if item.sync_mail and capacidades.get("read_mail"):
        algum_aplicavel = True
        try:
            detalhe = _heartbeat_mail(db, item)
            componentes.append(_ok_dict("mail", detalhe))
            teve_sucesso = True
        except ConnectorError as exc:
            db.rollback()
            is_reauth = exc.code in ERROS_REAUTENTICACAO or exc.status_code in {401, 403}
            componentes.append(_erro_dict("mail", exc.code, str(exc), reauth=is_reauth))
            reauth = reauth or is_reauth
        except (yahoo_mail.YahooMailError, apple_mail.AppleMailError) as exc:
            db.rollback()
            status_code = getattr(exc, "status_code", 502)
            is_reauth = status_code in {401, 403, 409}
            codigo = "reauth_required" if is_reauth else "mail_provider_unavailable"
            componentes.append(_erro_dict("mail", codigo, str(exc), reauth=is_reauth))
            reauth = reauth or is_reauth

    # Calendário só é chamado se o conector declara leitura. Isto é o que faz
    # "Sincronizar agora" funcionar também em Yahoo mail-only sem cair em
    # read_not_supported.
    if item.sync_calendar and capacidades.get("read_appointments"):
        algum_aplicavel = True
        try:
            detalhe = sync_integration(db, item, full=full)
            componentes.append(_ok_dict("calendario", detalhe))
            teve_sucesso = True
        except ConnectorError as exc:
            db.rollback()
            is_reauth = exc.code in ERROS_REAUTENTICACAO
            componentes.append(_erro_dict("calendario", exc.code, str(exc), reauth=is_reauth))
            reauth = reauth or is_reauth
        except Exception as exc:  # noqa: BLE001 — conector não derruba conta inteira
            db.rollback()
            componentes.append(_erro_dict("calendario", "sync_failed", str(exc), reauth=False))

    if item.contacts_enabled and capacidades.get("read_contacts"):
        algum_aplicavel = True
        try:
            detalhe = sync_contacts(db, item, full=full)
            componentes.append(_ok_dict("contatos", detalhe))
            teve_sucesso = True
        except ConnectorError as exc:
            db.rollback()
            is_reauth = exc.code in ERROS_REAUTENTICACAO
            componentes.append(_erro_dict("contatos", exc.code, str(exc), reauth=is_reauth))
            reauth = reauth or is_reauth
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            componentes.append(_erro_dict("contatos", "sync_failed", str(exc), reauth=False))

    if not algum_aplicavel:
        return {
            "ok": True,
            "status": item.status,
            "componentes": [],
            "mensagem": "Nenhum componente está habilitado para sincronização nesta conta.",
        }

    item = db.get(CalendarIntegration, item.id) or item
    erros = [c for c in componentes if not c["ok"]]
    if reauth:
        primeiro = next(c for c in erros if c.get("reauth_required"))
        _marcar_erro(db, item, "reauth_required", primeiro["mensagem"], reauth=True)
    elif teve_sucesso and not erros:
        _marcar_sucesso(db, item)
    elif teve_sucesso:
        # Sucesso parcial: conexão continua válida e elegível para o próximo
        # ciclo; preservamos o erro do componente que faltou.
        primeiro = erros[0]
        item.last_success_at = datetime.now(timezone.utc)
        _marcar_erro(db, item, primeiro["codigo"], primeiro["mensagem"], reauth=False)
    else:
        primeiro = erros[0]
        _marcar_erro(db, item, primeiro["codigo"], primeiro["mensagem"], reauth=False)

    return {
        "ok": not erros,
        "status": item.status,
        "reauth_required": item.status == "reauth_required",
        "componentes": componentes,
        "last_success_at": item.last_success_at,
        "mensagem": (
            "Sincronização concluída."
            if not erros
            else "A conta continua conectada, mas um componente teve uma pendência."
            if item.status != "reauth_required"
            else "A autorização precisa ser renovada."
        ),
    }
