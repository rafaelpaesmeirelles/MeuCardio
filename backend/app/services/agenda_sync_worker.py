"""Worker contínuo de sincronização de contas externas.

Mantém conexões e calendário atualizados sem depender de o usuário apertar um
botão. O CorVIA Mail externo continua sendo proxy ao vivo; para ele o worker
faz heartbeat/renovação de credencial. Calendário/contatos usam os cursores
incrementais existentes.

O intervalo é propositalmente curto para experiência quase em tempo real, mas
não promete push instantâneo de provedores que não oferecem webhook/IDLE já
homologado no produto. Falha de uma rodada nunca mata o processo: a próxima
rodada tenta novamente.
"""
from __future__ import annotations

import logging
import os
import signal
import time

from app.core.config import settings
from app.services.agenda_sync_cli import sincronizar_todas

log = logging.getLogger("corvia.agenda_sync_worker")
_PARAR = False


def _parar(_signum, _frame) -> None:  # noqa: ANN001
    global _PARAR
    _PARAR = True


def _intervalo_segundos() -> int:
    # Mantém compatibilidade com instalações cujo Settings ainda não exponha
    # um campo próprio; o compose de produção injeta a variável explicitamente.
    bruto = os.getenv("AGENDA_SYNC_INTERVAL_SECONDS", "60")
    try:
        valor = int(bruto)
    except ValueError:
        valor = 60
    return max(15, min(valor, 3600))


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
                resultado = sincronizar_todas()
                log.info(
                    "agenda-sync rodada concluida sincronizadas=%s falharam=%s puladas=%s",
                    resultado.get("sincronizadas"),
                    resultado.get("falharam"),
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
