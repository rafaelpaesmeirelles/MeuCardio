"""Sincronização periódica automática das contas externas da CorvIA.

O supervisor é tolerante a falhas e respeita cada preferência do usuário.
Calendário e contatos só são sincronizados quando habilitados; e-mail não é
copiado para o banco (a caixa é proxy ao vivo), mas toda conta com e-mail
habilitado recebe um heartbeat de credencial: OAuth para Google/Microsoft e
login IMAP para Yahoo/iCloud.
"""

from __future__ import annotations

import logging
import sys

from app.core.db import SessionLocal
from app.models.agenda import CalendarIntegration
from app.services import apple_mail, yahoo_mail
from app.services.agenda_integrada.connectors import ConnectorError
from app.services.agenda_integrada.contacts import sync_contacts
from app.services.agenda_integrada.domain import integration_credentials, sync_integration
from app.services.agenda_integrada.external_accounts import ensure_fresh_credentials

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("agenda_sync_cli")

ESTADOS_RECUPERAVEIS = ("connected", "error")
ERROS_REAUTENTICACAO = {
    "reauth_required", "invalid_grant", "interaction_required", "consent_required",
}
PROVEDORES_OAUTH = {"google_calendar", "microsoft_365"}
PROVEDORES_IMAP = {"yahoo_mail", "apple_icloud"}


def _registrar_falha(db, integration_id: int, exc: ConnectorError) -> CalendarIntegration | None:
    item = db.get(CalendarIntegration, integration_id)
    if item is None:
        return None
    item.last_error_code = exc.code
    item.last_error_message = str(exc)[:500]
    item.status = "reauth_required" if exc.code in ERROS_REAUTENTICACAO else "connected"
    db.commit()
    return item


def _heartbeat_imap(item: CalendarIntegration) -> dict:
    credenciais = integration_credentials(item)
    if item.provider == "yahoo_mail":
        return yahoo_mail.diagnose(credenciais)
    if item.provider == "apple_icloud":
        return apple_mail.diagnose(credenciais)
    return {"ok": True}


def sincronizar_todas() -> dict:
    db = SessionLocal()
    resultado = {"sincronizadas": 0, "falharam": 0, "puladas": 0, "detalhe": []}
    try:
        integracoes = (
            db.query(CalendarIntegration)
            .filter(
                CalendarIntegration.enabled.is_(True),
                CalendarIntegration.status.in_(ESTADOS_RECUPERAVEIS),
            )
            .order_by(CalendarIntegration.id.asc())
            .all()
        )
        for item in integracoes:
            integration_id = item.id
            rotulo = f"{item.provider}:{item.display_name or item.id}"
            calendario = contatos = None
            heartbeat_mail = None
            erro_calendario = erro_contatos = erro_mail = None

            # 1) Heartbeat do CorvIA Mail. Nenhuma mensagem é copiada.
            mail_aplicavel = bool(item.sync_mail and (item.capabilities or {}).get("read_mail"))
            if mail_aplicavel and item.provider in PROVEDORES_OAUTH:
                try:
                    ensure_fresh_credentials(db, item)
                    heartbeat_mail = {"ok": True, "modo": "oauth"}
                except ConnectorError as exc:
                    db.rollback()
                    erro_mail = exc.code
                    item = _registrar_falha(db, integration_id, exc) or item
            elif mail_aplicavel and item.provider in PROVEDORES_IMAP:
                try:
                    heartbeat_mail = {**_heartbeat_imap(item), "modo": "imap"}
                except (yahoo_mail.YahooMailError, apple_mail.AppleMailError) as exc:
                    db.rollback()
                    item = db.get(CalendarIntegration, integration_id) or item
                    # Nos adaptadores IMAP, 401 significa senha de aplicativo
                    # recusada/revogada. Erro de rede/servidor (502/503) é
                    # transitório e não deve tirar a conta do supervisor.
                    status_code = getattr(exc, "status_code", 502)
                    if status_code in {401, 403, 409}:
                        erro_mail = "reauth_required"
                        item.status = "reauth_required"
                        item.last_error_code = "reauth_required"
                        item.last_error_message = str(exc)[:500]
                    else:
                        erro_mail = "mail_provider_unavailable"
                        item.status = "connected"
                        item.last_error_code = erro_mail
                        item.last_error_message = str(exc)[:500]
                    db.commit()

            # 2) Calendário respeita explicitamente sync_calendar.
            item = db.get(CalendarIntegration, integration_id) or item
            calendario_aplicavel = bool(item.sync_calendar and item.status != "reauth_required")
            if calendario_aplicavel:
                try:
                    calendario = sync_integration(db, item, full=False)
                    db.commit()
                except ConnectorError as exc:
                    db.rollback()
                    if exc.code == "read_not_supported":
                        calendario_aplicavel = False
                        item = db.get(CalendarIntegration, integration_id) or item
                        if item.status == "error":
                            item.status = "connected"
                            db.commit()
                    else:
                        erro_calendario = exc.code
                        item = _registrar_falha(db, integration_id, exc) or item
                except Exception as exc:  # noqa: BLE001
                    db.rollback()
                    erro_calendario = "erro_inesperado"
                    item = db.get(CalendarIntegration, integration_id) or item
                    item.last_error_code = "erro_inesperado"
                    item.last_error_message = str(exc)[:500]
                    item.status = "connected"
                    db.commit()
                    log.exception("Erro inesperado sincronizando calendário de %s", rotulo)

            # 3) Contatos são independentes e respeitam contacts_enabled.
            item = db.get(CalendarIntegration, integration_id) or item
            contatos_aplicavel = bool(item.contacts_enabled and item.status != "reauth_required")
            if contatos_aplicavel:
                try:
                    contatos = sync_contacts(db, item, full=False)
                    db.commit()
                except ConnectorError as exc:
                    db.rollback()
                    erro_contatos = exc.code
                    if exc.code in ERROS_REAUTENTICACAO:
                        item = _registrar_falha(db, integration_id, exc) or item
                except Exception:  # noqa: BLE001
                    db.rollback()
                    erro_contatos = "erro_inesperado"
                    log.exception("Erro inesperado sincronizando contatos de %s", rotulo)

            item = db.get(CalendarIntegration, integration_id) or item
            mail_ok = (not mail_aplicavel) or erro_mail is None
            calendario_ok = (not calendario_aplicavel) or erro_calendario is None
            contatos_ok = (not contatos_aplicavel) or erro_contatos is None
            ok = mail_ok and calendario_ok and contatos_ok and item.status != "reauth_required"

            if ok:
                resultado["sincronizadas"] += 1
                if item.status != "connected" or item.last_error_code:
                    item.status = "connected"
                    item.last_error_code = None
                    item.last_error_message = None
                    db.commit()
                log.info(
                    "OK %s — mail=%s calendario=%s contatos=%s",
                    rotulo, heartbeat_mail, calendario, contatos,
                )
            else:
                resultado["falharam"] += 1
                log.warning(
                    "FALHOU %s — mail=%s calendario=%s contatos=%s status=%s",
                    rotulo, erro_mail, erro_calendario, erro_contatos, item.status,
                )

            resultado["detalhe"].append({
                "conta": rotulo,
                "ok": ok,
                "status": item.status,
                "mail": heartbeat_mail,
                "erro_mail": erro_mail,
                "calendario": calendario,
                "erro_calendario": erro_calendario,
                "contatos": contatos,
                "erro_contatos": erro_contatos,
            })

        resultado["puladas"] = (
            db.query(CalendarIntegration)
            .filter(
                CalendarIntegration.enabled.is_(True),
                ~CalendarIntegration.status.in_(ESTADOS_RECUPERAVEIS),
            )
            .count()
        )
        return resultado
    finally:
        db.close()


if __name__ == "__main__":
    r = sincronizar_todas()
    log.info(
        "Resumo: %d sincronizadas, %d falharam, %d puladas (reautenticação/desconectadas)",
        r["sincronizadas"], r["falharam"], r["puladas"],
    )
    sys.exit(0)
