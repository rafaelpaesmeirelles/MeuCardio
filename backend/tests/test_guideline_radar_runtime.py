from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import text

from app.models.audit import AuditLog
from app.models.guideline import Guideline
from app.services import guideline_radar_runtime as runtime
from app.services import guideline_discovery_worldwide as discovery


def test_single_flight_lock_survives_pipeline_commits_and_reexecution_skips(db, monkeypatch):
    calls = []
    def pipeline(session):
        session.commit()
        with session.get_bind().connect() as other:
            assert other.execute(text("SELECT pg_try_advisory_lock(:key)"), {"key": runtime.LOCK_KEY}).scalar() is False
        calls.append(1)
        return {"created": 0, "coverage": {"direct_sources_total": 2, "direct_sources_ok": 2}}
    monkeypatch.setattr(discovery, "discover_and_publish_worldwide", pipeline)
    assert runtime.run_radar(db)["created"] == 0
    assert runtime.run_radar(db)["skipped"] == "adaptive_schedule"
    assert calls == [1]
    assert db.query(AuditLog).filter(AuditLog.action == runtime.STARTED).count() == 1
    assert runtime._latest(db, runtime.COMPLETED).detail["success"] is True


def test_competing_scheduler_skips_without_audit_or_provider(db, monkeypatch):
    monkeypatch.setattr(discovery, "discover_and_publish_worldwide", lambda *_: pytest.fail("must not run"))
    with db.get_bind().connect() as lock:
        lock.execute(text("SELECT pg_advisory_lock(:key)"), {"key": runtime.LOCK_KEY})
        try:
            assert runtime.run_radar(db, force=True)["skipped"] == "already_running"
            assert db.query(AuditLog).filter(AuditLog.action == runtime.STARTED).count() == 0
        finally:
            lock.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": runtime.LOCK_KEY})


def test_scan_exception_is_audited_without_error_text_and_releases_lock(db, monkeypatch):
    def failing(_):
        raise RuntimeError("private provider response must not appear in public status")
    monkeypatch.setattr(discovery, "discover_and_publish_worldwide", failing)
    with pytest.raises(RuntimeError):
        runtime.run_radar(db)
    detail = runtime._latest(db, runtime.COMPLETED).detail
    assert detail["success"] is False
    assert detail["error_type"] == "RuntimeError"
    assert "private" not in str(detail)
    with db.get_bind().connect() as other:
        assert other.execute(text("SELECT pg_try_advisory_lock(:key)"), {"key": runtime.LOCK_KEY}).scalar() is True
        other.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": runtime.LOCK_KEY})


def test_health_requires_live_heartbeat_and_reports_partial_coverage():
    now = datetime.now(timezone.utc)
    done = SimpleNamespace(id=2, created_at=now, detail={"success": True, "coverage": {"direct_sources_failed": 1}})
    assert runtime.runtime_health(heartbeat_data=None, last_started=None, last_completed=None, now=now) == "unknown"
    assert runtime.runtime_health(heartbeat_data=None, last_started=None, last_completed=done, now=now) == "inactive"
    assert runtime.runtime_health(heartbeat_data={"at": now.isoformat()}, last_started=None, last_completed=done, now=now) == "degraded"
    assert runtime.runtime_health(heartbeat_data={"at": (now-timedelta(minutes=4)).isoformat()}, last_started=None, last_completed=done, now=now) == "inactive"
    done.detail = {"success": True, "coverage": {"direct_sources_failed": 0}}
    assert runtime.runtime_health(heartbeat_data={"at": now.isoformat()}, last_started=None, last_completed=done, now=now) == "active"


def test_status_exposes_bibliography_before_ai_analysis_without_publishing(db, monkeypatch):
    monkeypatch.setattr(runtime, "read_heartbeat", lambda *_args: None)
    item = Guideline(slug="qa-intelligence-visible-without-ai", org="ESC", titulo="Unanalyzed bibliography",
                     ano=2026, published_at=datetime.now(timezone.utc),
                     detection_status="oficial_aprovada", source_fingerprint="9"*64)
    db.add(item); db.commit()
    try:
        status = runtime.radar_status(db)
        assert status["health"] == "unknown"
        assert status["enabled"] is False
        assert status["next_run_at"] is None
        found = next(row for row in status["recent_discoveries"] if row["id"] == item.id)
        assert found["status"] == "oficial_aprovada"
        assert found["title"] == item.titulo
        assert status["pending_analysis"] >= 1
        db.refresh(item)
        assert item.detection_status == "oficial_aprovada"
    finally:
        db.delete(item); db.commit()


def test_pending_analysis_shares_scheduler_lock(db, monkeypatch):
    from app.services import guideline_clinical_update_runtime as clinical
    monkeypatch.setattr(clinical, "process_pending_guidelines", lambda *_args, **_kwargs: pytest.fail("must not run"))
    with db.get_bind().connect() as lock:
        lock.execute(text("SELECT pg_advisory_lock(:key)"), {"key": runtime.LOCK_KEY})
        try:
            assert runtime.run_pending_radar_analysis(db, limit=1) == {"skipped": "already_running", "processed": 0}
        finally:
            lock.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": runtime.LOCK_KEY})


def test_analysis_unavailable_and_rate_limit_are_visible_as_degraded():
    now = datetime.now(timezone.utc)
    for result, state in [({"skipped": "ai_unavailable"}, "unavailable"), ({"rate_limited": True}, "rate_limited")]:
        assert runtime.analysis_state(result) == state
        done = SimpleNamespace(id=2, created_at=now, detail={"success": True, "analysis_status": state})
        assert runtime.runtime_health(heartbeat_data={"at": now.isoformat()}, last_started=None, last_completed=done, now=now) == "degraded"
