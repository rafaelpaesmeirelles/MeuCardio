"""Worker contínuo de sincronização de contas externas.

Mantém conexões e calendário atualizados sem depender de o usuário apertar um
botão. O CorVIA Mail externo continua sendo proxy ao vivo; para ele o worker
faz heartbeat/renovação de credencial. Calendário/contatos usam os cursores
incrementais existentes.

O intervalo é propositalmente curto para experiência quase em tempo real, mas
não promete push instantâneo de provedores que não oferecem webhook/IDLE já
homologado no produto. Falha de uma conta ou de uma rodada nunca mata o
processo: a próxima rodada tenta novamente.
"""
from __future__ import annotations

import logging
import os
import signal
import time

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.agenda import CalendarIntegration
from app.services.account_sync import sincronizar_conta
from app.services.agenda_integrada.connectors import ConnectorError

log = logging.getLogger("corvia.agenda_sync_worker")
_PARAR = False
_ESTADOS_ELEGIVEIS = ("connected", "error")


def _parar(_signum, _frame) -> None:  # noqa: ANN001
    global _PARAR
    _PARAR = True


def _intervalo_segundos() -> int:
    bruto = os.getenv("AGENDA_SYNC_INTERVAL_SECONDS", "60")
    try:
        valor = int(bruto)
    except ValueError:
        valor = 60
    return max(15, min(valor, 3600))


def sincronizar_rodada() -> dict:
    db = SessionLocal()
    resultado = {"sincronizadas": 0, "com_pendencia": 0, "puladas": 0}
    try:
        ids = [
            linha[0]
            for linha in db.query(CalendarIntegration.id).filter(
                CalendarIntegration.enabled.is_(True),
                CalendarIntegration.status.in_(_ESTADOS_ELEGIVEIS),
            ).order_by(CalendarIntegration.id.asc()).all()
        ]
        for integration_id in ids:
            item = db.get(CalendarIntegration, integration_id)
            if item is None:
                continue
            try:
                detalhe = sincronizar_conta(db, item, full=False)
                if detalhe.get("ok"):
                    resultado["sincronizadas"] += 1
                else:
                    resultado["com_pendencia"] += 1
                    log.warning(
                        "agenda-sync pendencia integration_id=%s provider=%s status=%s componentes=%s",
                        item.id, item.provider, detalhe.get("status"), detalhe.get("componentes"),
                    )
            except ConnectorError as exc:
                db.rollback()
                # Conta que exige interação humana é retirada das rodadas pela
                # própria mudança de status; transitórios seguem elegíveis.
                resultado["com_pendencia"] += 1
                log.warning(
                    "agenda-sync falha integration_id=%s provider=%s code=%s: %s",
                    item.id, item.provider, exc.code, exc,
                )
            except Exception:  # noqa: BLE001 — isolamento entre contas
                db.rollback()
                resultado["com_pendencia"] += 1
                log.exception(
                    "agenda-sync falha inesperada integration_id=%s provider=%s",
                    item.id, item.provider,
                )

        resultado["puladas"] = db.query(CalendarIntegration).filter(
            CalendarIntegration.enabled.is_(True),
            ~CalendarIntegration.status.in_(_ESTADOS_ELEGIVEIS),
        ).count()
        return resultado
    finally:
        db.close()


def executar() -> None:
    signal.signal(signal.SIGTERM, _parar)
    signal.signal(signal.SIGINT, _parar)

    intervalo = _intervalo_segundos()
    log.info(
        "agenda-sync worker iniciado enabled=%s intervalo=%ss",
        settings.agenda_background_sync_enabled,
        intervalo,
    )

    while not _PARAR:
        inicio = time.monotonic()
        if settings.agenda_background_sync_enabled:
            try:
                resultado = sincronizar_rodada()
                log.info(
                    "agenda-sync rodada concluida sincronizadas=%s pendencias=%s puladas=%s",
                    resultado.get("sincronizadas"),
                    resultado.get("com_pendencia"),
                    resultado.get("puladas"),
                )
            except Exception:  # noqa: BLE001 — supervisor não morre por uma rodada
                log.exception("agenda-sync rodada falhou inesperadamente")
        else:
            log.warning("agenda-sync está desativado por configuração")

        gasto = time.monotonic() - inicio
        restante = max(1.0, intervalo - gasto)
        limite = time.monotonic() + restante
        while not _PARAR and time.monotonic() < limite:
            time.sleep(min(1.0, limite - time.monotonic()))

    log.info("agenda-sync worker encerrado")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    executar()
