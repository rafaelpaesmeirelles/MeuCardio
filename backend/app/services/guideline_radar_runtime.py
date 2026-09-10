"""Observable single-flight scheduler; scientific processing remains unchanged."""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone

from redis import Redis
from sqlalchemy import text

from app.core.config import settings
from app.models.audit import AuditLog
from app.models.guideline import Guideline
from app.services.guideline_radar_schedule import decide_radar_run

HEARTBEAT_KEY = "corvia:intelligence:worker:heartbeat:v1"
HEARTBEAT_TTL = 180
LIBRARY_HEARTBEAT_KEY = "corvia:scientific-publication-library:worker:heartbeat:v1"
LOCK_KEY = 71920260910
STARTED = "intelligence_radar_started"
COMPLETED = "intelligence_radar_completed"


def _redis():
    return Redis.from_url(settings.redis_url, decode_responses=True,
                          socket_connect_timeout=2, socket_timeout=2)


def heartbeat(key: str = HEARTBEAT_KEY) -> None:
    with _redis() as client:
        client.set(key, json.dumps({
            "at": datetime.now(timezone.utc).isoformat(),
            "commit": os.getenv("DEPLOY_COMMIT", "unknown"),
        }), ex=HEARTBEAT_TTL)


def read_heartbeat(key: str = HEARTBEAT_KEY) -> dict | None:
    try:
        with _redis() as client:
            raw = client.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        # A página continua mostrando os achados, mas não inventa saúde ativa.
        return None


def _latest(db, action: str, *, successful: bool = False):
    query = db.query(AuditLog).filter(AuditLog.action == action)
    if successful:
        query = query.filter(AuditLog.detail["success"].as_boolean().is_(True))
    return query.order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).first()


def _audit(db, action: str, detail: dict):
    row = AuditLog(action=action, entity="intelligence_radar", entity_id="worldwide",
                   detail=detail)
    db.add(row)
    db.commit()
    return row


def _coverage(result: dict) -> dict | None:
    coverage = result.get("coverage")
    if not isinstance(coverage, dict):
        return None
    keys = ("direct_sources_total", "direct_sources_ok", "direct_sources_failed",
            "structured_total", "structured_ok", "structured_failed")
    return {key: max(0, int(coverage.get(key) or 0)) for key in keys}


def analysis_state(result: dict) -> str:
    if result.get("rate_limited"):
        return "rate_limited"
    if result.get("skipped") == "ai_unavailable":
        return "unavailable"
    if result.get("failures"):
        return "partial"
    return "ok" if "processed" in result else "not_run"


def run_pending_radar_analysis(db, *, limit: int) -> dict:
    with db.get_bind().connect().execution_options(isolation_level="AUTOCOMMIT") as lock:
        acquired = lock.execute(text("SELECT pg_try_advisory_lock(:key)"), {"key": LOCK_KEY}).scalar()
        if not acquired:
            return {"skipped": "already_running", "processed": 0}
        try:
            from app.services.guideline_clinical_update_runtime import process_pending_guidelines
            result = process_pending_guidelines(db, limit=limit)
            _audit(db, "intelligence_analysis_completed", {"analysis_status": analysis_state(result), "analysis_error": result.get("analysis_error")})
            return result
        finally:
            lock.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": LOCK_KEY})


def run_radar(db, *, force: bool = False, origin: str = "scheduler") -> dict:
    # Uma conexão dedicada mantém a trava de sessão mesmo quando o pipeline
    # faz commits. Todas as entradas (worker/CLI/admin) passam por esta trava.
    with db.get_bind().connect().execution_options(isolation_level="AUTOCOMMIT") as lock:
        acquired = lock.execute(text("SELECT pg_try_advisory_lock(:key)"), {"key": LOCK_KEY}).scalar()
        if not acquired:
            return {"skipped": "already_running"}
        try:
            previous = _latest(db, STARTED)
            schedule = decide_radar_run(db, force=force,
                                        last_started_at=previous.created_at if previous else None)
            if not schedule["run"]:
                return {"skipped": "adaptive_schedule", "radar_schedule": schedule}
            start = _audit(db, STARTED, {"origin": origin, "schedule": schedule,
                                        "commit": os.getenv("DEPLOY_COMMIT", "unknown")})
            run_id = start.id
            try:
                from app.services.guideline_discovery_worldwide import discover_and_publish_worldwide
                result = discover_and_publish_worldwide(db)
                # Novas publicações chegam à biblioteca após cada descoberta,
                # inclusive nos picos horários. Falha documental não apaga radar.
                try:
                    from app.services.scientific_publication_library import seed_publication_queue
                    result["publication_library_queue"] = seed_publication_queue(db, limit=200)
                except Exception as exc:
                    db.rollback()
                    result["publication_library_queue"] = {"error_type": type(exc).__name__}
                coverage = _coverage(result)
                successful = bool(coverage and (coverage["direct_sources_ok"] + coverage["structured_ok"]) > 0)
                pipeline = result.get("clinical_update_pipeline") or {}
                _audit(db, COMPLETED, {
                    "run_id": run_id, "success": successful, "coverage": coverage,
                    "created": int(result.get("created") or 0),
                    "analysis_failures": len(pipeline.get("failures") or []),
                    "analysis_status": analysis_state(pipeline),
                    "analysis_error": pipeline.get("analysis_error"),
                    "commit": os.getenv("DEPLOY_COMMIT", "unknown"),
                })
                result["radar_schedule"] = schedule
                return result
            except Exception as exc:
                db.rollback()
                _audit(db, COMPLETED, {"run_id": run_id, "success": False,
                                        "error_type": type(exc).__name__})
                raise
        finally:
            lock.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": LOCK_KEY})


def runtime_health(*, heartbeat_data, last_started, last_completed, now=None):
    current = now or datetime.now(timezone.utc)
    live = False
    if heartbeat_data:
        try:
            at = datetime.fromisoformat(heartbeat_data["at"])
            live = 0 <= (current - at).total_seconds() <= HEARTBEAT_TTL
        except (KeyError, TypeError, ValueError):
            pass
    if not live:
        return "inactive" if last_started or last_completed else "unknown"
    if last_completed:
        detail = last_completed.detail or {}
        coverage = detail.get("coverage") or {}
        if (not detail.get("success") or detail.get("analysis_failures") or
                detail.get("analysis_status") in {"rate_limited", "unavailable", "partial"} or
                coverage.get("direct_sources_failed") or coverage.get("structured_failed")):
            return "degraded"
    # Um processo vivo não basta quando uma varredura ficou presa.
    if last_started and (not last_completed or last_started.id > last_completed.id):
        if current - last_started.created_at > timedelta(hours=2):
            return "degraded"
    return "active"


def publication_processing_status(db) -> dict:
    from app.services.scientific_publication_library import publication_queue_status
    queue = publication_queue_status(db)
    pulse = read_heartbeat(LIBRARY_HEARTBEAT_KEY)
    health = runtime_health(heartbeat_data=pulse, last_started=None, last_completed=None)
    if health == "active" and pulse.get("commit") != os.getenv("DEPLOY_COMMIT", "unknown"):
        health = "inactive"
    if health == "unknown" and queue.get("total", 0):
        health = "inactive"
    return {
        **queue, "health": health, "enabled": health == "active",
        "last_heartbeat_at": pulse.get("at") if pulse else None,
    }


def radar_status(db) -> dict:
    started = _latest(db, STARTED)
    completed = _latest(db, COMPLETED)
    succeeded = _latest(db, COMPLETED, successful=True)
    pulse = read_heartbeat()
    schedule = decide_radar_run(db, last_started_at=started.created_at if started else None)
    health = runtime_health(heartbeat_data=pulse, last_started=started, last_completed=completed)
    publications = db.query(Guideline).filter(Guideline.published_at.isnot(None),
                                              Guideline.source_fingerprint.isnot(None))
    recent = publications.order_by(Guideline.discovered_at.desc(), Guideline.id.desc()).limit(8).all()
    # O monitor bibliográfico independe da análise paga e não promove conteúdo.
    return {
        "health": health,
        "enabled": health in {"active", "degraded"},
        "cadence_hours": schedule["interval_hours"],
        "normal_interval_hours": 4, "surge_interval_hours": 1,
        "schedule_reason": schedule["reason"], "high_frequency_window": schedule["window"],
        "last_heartbeat_at": pulse.get("at") if pulse else None,
        "last_started_at": started.created_at if started else None,
        "last_completed_at": completed.created_at if completed else None,
        "last_success_at": succeeded.created_at if succeeded else None,
        "next_run_at": schedule["next_run_at"] if health in {"active", "degraded"} else None,
        "coverage": (completed.detail or {}).get("coverage") if completed else None,
        "analysis_status": (completed.detail or {}).get("analysis_status", "not_run") if completed else "not_run",
        "total_discovered": publications.count(),
        "pending_analysis": publications.filter(Guideline.detection_status.in_(
            ("detected", "aguardando_revisao", "oficial_aprovada"))).count(),
        "document_processing": publication_processing_status(db),
        "recent_discoveries": [{
            "id": item.id, "slug": item.slug, "title": item.titulo, "org": item.org,
            "url": item.url, "doi": item.doi, "discovered_at": item.discovered_at,
            "published_at": item.published_at, "status": item.detection_status,
        } for item in recent],
    }
