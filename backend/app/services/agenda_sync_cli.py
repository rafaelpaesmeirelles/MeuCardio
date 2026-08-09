"""Sincronização periódica automática das contas externas da CorvIA.

O supervisor é deliberadamente tolerante a falhas: uma indisponibilidade de
rede ou do provedor não pode expulsar uma conta das rodadas seguintes. Contas
``connected`` e ``error`` são candidatas; somente estados que exigem ação do
titular (``reauth_required``/``disconnected``) ficam de fora.
"""

from __future__ import annotations

import logging
import sys

from app.core.db import SessionLocal
from app.models.agenda import CalendarIntegration
from app.services.agenda_integrada.connectors import ConnectorError
from app.services.agenda_integrada.contacts import sync_contacts
from app.services.agenda_integrada.domain import sync_integration

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("agenda_sync_cli")

ESTADOS_RECUPERAVEIS = ("connected", "error")
ERROS_REAUTENTICACAO = {
    "reauth_required", "invalid_grant", "interaction_required", "consent_required",
}


def _registrar_falha_calendario(db, integration_id: int, exc: ConnectorError) -> CalendarIntegration | None:
    """Normaliza o estado depois de uma tentativa de sincronização.

    ``sync_integration`` historicamente grava ``error`` para qualquer exceção.
    Aqui distinguimos erro recuperável de revogação real para que uma falha
    temporária continue sendo tentada automaticamente no próximo cron.
    """
    item = db.get(CalendarIntegration, integration_id)
    if item is None:
        return None
    item.last_error_code = exc.code
    item.last_error_message = str(exc)[:500]
    if exc.code in ERROS_REAUTENTICACAO:
        item.status = "reauth_required"
    else:
        # Rede, rate limit, timeout, 5xx e outros erros operacionais continuam
        # elegíveis para a próxima rodada automática.
        item.status = "connected"
    db.commit()
    return item


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
            erro_calendario = erro_contatos = None
            calendario_aplicavel = True

            try:
                calendario = sync_integration(db, item, full=False)
                db.commit()
            except ConnectorError as exc:
                db.rollback()
                if exc.code == "read_not_supported":
                    calendario_aplicavel = False
                    item = db.get(CalendarIntegration, integration_id) or item
                    # Conta somente de e-mail não está quebrada por não possuir
                    # calendário. Mantém conectada para o CorvIA Mail.
                    if item.status == "error":
                        item.status = "connected"
                        db.commit()
                else:
                    erro_calendario = exc.code
                    item = _registrar_falha_calendario(db, integration_id, exc) or item
            except Exception as exc:  # noqa: BLE001
                db.rollback()
                erro_calendario = "erro_inesperado"
                item = db.get(CalendarIntegration, integration_id) or item
                item.last_error_code = "erro_inesperado"
                item.last_error_message = str(exc)[:500]
                # Também é recuperável: uma exceção inesperada não pode retirar
                # definitivamente a conta do supervisor periódico.
                item.status = "connected"
                db.commit()
                log.exception("Erro inesperado sincronizando calendário de %s", rotulo)

            contatos_aplicavel = bool(item.contacts_enabled)
            if contatos_aplicavel and item.status != "reauth_required":
                item = db.get(CalendarIntegration, integration_id) or item
                try:
                    contatos = sync_contacts(db, item, full=False)
                    db.commit()
                except ConnectorError as exc:
                    db.rollback()
                    erro_contatos = exc.code
                    # Se contatos detectarem revogação verdadeira, isso vale
                    # para a credencial da conta inteira, não apenas contatos.
                    if exc.code in ERROS_REAUTENTICACAO:
                        item = db.get(CalendarIntegration, integration_id) or item
                        item.status = "reauth_required"
                        item.last_error_code = exc.code
                        item.last_error_message = str(exc)[:500]
                        db.commit()
                except Exception:  # noqa: BLE001
                    db.rollback()
                    erro_contatos = "erro_inesperado"
                    log.exception("Erro inesperado sincronizando contatos de %s", rotulo)

            item = db.get(CalendarIntegration, integration_id) or item
            calendario_ok = (not calendario_aplicavel) or erro_calendario is None
            contatos_ok = (not contatos_aplicavel) or erro_contatos is None
            ok = calendario_ok and contatos_ok and item.status != "reauth_required"
            if ok:
                resultado["sincronizadas"] += 1
                # Limpa erro operacional antigo após uma rodada saudável.
                if item.status != "connected" or item.last_error_code:
                    item.status = "connected"
                    item.last_error_code = None
                    item.last_error_message = None
                    db.commit()
                log.info("OK %s — calendario=%s contatos=%s", rotulo, calendario, contatos)
            else:
                resultado["falharam"] += 1
                log.warning(
                    "FALHOU %s — calendario=%s contatos=%s status=%s",
                    rotulo, erro_calendario, erro_contatos, item.status,
                )
            resultado["detalhe"].append({
                "conta": rotulo,
                "ok": ok,
                "status": item.status,
                "calendario": calendario,
                "erro_calendario": erro_calendario,
                "contatos": contatos,
                "erro_contatos": erro_contatos,
            })

        # Somente estados realmente não recuperáveis são "pulados". ``error``
        # deixou de ser limbo permanente e é sempre retentado.
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
