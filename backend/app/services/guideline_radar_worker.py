"""Supervised local radar: reliable timing independent of GitHub cron delays."""
import logging
import signal
import threading

from app.core.db import SessionLocal
from app.services.guideline_radar_runtime import heartbeat, run_radar

log = logging.getLogger(__name__)
STOP = threading.Event()


def _pulse():
    while not STOP.is_set():
        try:
            heartbeat()
        except Exception as exc:
            log.warning("Intelligence heartbeat unavailable: %s", type(exc).__name__)
        STOP.wait(60)


def run():
    signal.signal(signal.SIGTERM, lambda *_: STOP.set())
    signal.signal(signal.SIGINT, lambda *_: STOP.set())
    heartbeat()  # A configuração inválida deve falhar visivelmente no startup.
    threading.Thread(target=_pulse, daemon=True, name="intelligence-heartbeat").start()
    failures = 0
    while not STOP.is_set():
        try:
            with SessionLocal() as db:
                result = run_radar(db, origin="local_worker")
            failures = 0
            if not result.get("skipped"):
                log.info("Intelligence scan completed; new publications=%s", result.get("created", 0))
        except Exception as exc:
            failures += 1
            log.error("Intelligence scan failed: %s", type(exc).__name__)
            if failures >= 5:
                raise
        STOP.wait(60)


if __name__ == "__main__":
    run()
