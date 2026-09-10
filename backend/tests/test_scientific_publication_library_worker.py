import sys
from types import SimpleNamespace

import pytest

from app.services import scientific_publication_library_worker as worker


@pytest.fixture(autouse=True)
def _banco_limpo():
    # Exercita supervisão sem banco/rede/provedores; o serviço persistente é
    # testado separadamente com suas próprias fixtures de fila e carteira.
    yield


class Session:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def test_seed_failure_does_not_starve_existing_publication_queue(monkeypatch):
    calls = []
    def seed(*_args, **_kwargs):
        raise ValueError("malformed source reference")
    service = SimpleNamespace(seed_publication_queue=seed,
                              process_one_publication=lambda: calls.append("processed") or {"processed": 1})
    monkeypatch.setitem(sys.modules, "app.services.scientific_publication_library", service)
    monkeypatch.setattr(worker, "SessionLocal", Session)
    result, last_seed = worker.run_round(now=100)
    assert result == {"processed": 1}
    assert calls == ["processed"]
    assert last_seed is None


def test_each_worker_round_processes_at_most_one_publication_and_seed_is_bounded(monkeypatch):
    seeds, jobs = [], []
    service = SimpleNamespace(
        seed_publication_queue=lambda db, *, limit: seeds.append(limit),
        process_one_publication=lambda: jobs.append(1) or {"processed": 1},
    )
    monkeypatch.setitem(sys.modules, "app.services.scientific_publication_library", service)
    monkeypatch.setattr(worker, "SessionLocal", Session)
    _, last = worker.run_round(now=100)
    _, last = worker.run_round(last, now=160)
    assert seeds == [200]
    assert jobs == [1, 1]
    _, last = worker.run_round(last, now=100 + worker.SEED_INTERVAL_SECONDS)
    assert seeds == [200, 200]
    assert jobs == [1, 1, 1]


def test_metadata_backlog_continues_next_tick_until_complete_without_extra_processing(monkeypatch):
    seeds, jobs = [], []
    def seed(db, *, limit):
        seeds.append(limit)
        return {"has_more": len(seeds) < 2}
    service = SimpleNamespace(seed_publication_queue=seed, process_one_publication=lambda: jobs.append(1))
    monkeypatch.setitem(sys.modules, "app.services.scientific_publication_library", service)
    monkeypatch.setattr(worker, "SessionLocal", Session)
    _, last = worker.run_round(now=100)
    assert last is None
    _, last = worker.run_round(last, now=160)
    assert last == 160
    worker.run_round(last, now=220)
    assert seeds == [200, 200]
    assert jobs == [1, 1, 1]


def test_document_processing_status_is_read_only_and_requires_current_worker_heartbeat(monkeypatch):
    from datetime import datetime, timezone
    from app.services import guideline_radar_runtime as runtime
    queries = []
    class ReadOnlySession:
        def commit(self):
            pytest.fail("status must not commit")
        def add(self, *_):
            pytest.fail("status must not mutate")
    session = ReadOnlySession()
    def queue_status(db):
        assert db is session
        queries.append(1)
        return {"total": 2, "queued": 1, "ready_full_pt": 1}
    monkeypatch.setitem(sys.modules, "app.services.scientific_publication_library", SimpleNamespace(publication_queue_status=queue_status))
    monkeypatch.setenv("DEPLOY_COMMIT", "release-current")
    pulse = {"at": datetime.now(timezone.utc).isoformat(), "commit": "release-previous"}
    def read(key):
        assert key == worker.HEARTBEAT_KEY
        return pulse
    monkeypatch.setattr(runtime, "read_heartbeat", read)
    status = runtime.publication_processing_status(session)
    assert status["health"] == "inactive" and status["enabled"] is False
    pulse["commit"] = "release-current"
    status = runtime.publication_processing_status(session)
    assert status["health"] == "active" and status["ready_full_pt"] == 1
    assert queries == [1, 1]
