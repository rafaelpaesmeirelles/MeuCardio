"""Bounded shared publication jobs; independent from scientific discovery."""
import logging
import signal
import threading
import time

from app.core.db import SessionLocal
from app.services.guideline_radar_runtime import heartbeat, LIBRARY_HEARTBEAT_KEY

log = logging.getLogger(__name__)
STOP = threading.Event()
HEARTBEAT_KEY = LIBRARY_HEARTBEAT_KEY
SEED_INTERVAL_SECONDS = 4 * 60 * 60


def _pulse():
    while not STOP.is_set():
        try:
            heartbeat(HEARTBEAT_KEY)
        except Exception as exc:
            log.warning("Publication library heartbeat unavailable: %s", type(exc).__name__)
        STOP.wait(60)


def run_round(last_seed_at=None, *, now=None):
    from app.services.scientific_publication_library import (
        process_one_publication, seed_publication_queue,
    )
    current = time.monotonic() if now is None else now
    if last_seed_at is None or current - last_seed_at >= SEED_INTERVAL_SECONDS:
        try:
            with SessionLocal() as db:
                seeded = seed_publication_queue(db, limit=200)
            # Drena somente metadados em lotes até cobrir o corpus inteiro.
            # has_more não aumenta frequência ou orçamento do processamento IA.
            last_seed_at = None if isinstance(seeded, dict) and seeded.get("has_more") else current
        except Exception as exc:
            # Uma referência malformada não deve paralisar a fila já criada.
            log.warning("Publication metadata seed failed: %s", type(exc).__name__)
    # O serviço possui a trava/estado persistente, processa no máximo um item
    # e um trecho de IA e preserva o orçamento editorial compartilhado.
    return process_one_publication(), last_seed_at


def run():
    signal.signal(signal.SIGTERM, lambda *_: STOP.set())
    signal.signal(signal.SIGINT, lambda *_: STOP.set())
    heartbeat(HEARTBEAT_KEY)
    threading.Thread(target=_pulse, daemon=True, name="publication-library-heartbeat").start()
    failures = 0
    last_seed_at = None
    while not STOP.is_set():
        try:
            _, last_seed_at = run_round(last_seed_at)
            failures = 0
        except Exception as exc:
            failures += 1
            log.error("Publication library round failed: %s", type(exc).__name__)
            if failures >= 5:
                raise
        STOP.wait(60)


if __name__ == "__main__":
    run()
