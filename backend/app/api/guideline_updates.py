from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user, require_admin
from app.models.content import Document
from app.models.guideline import Guideline, GuidelineLink, GuidelineNotification
from app.models.user import User
from app.services.guideline_discovery import DISCOVERY_LOOKBACK_DAYS, DISCOVERY_START
from app.services.guideline_discovery_worldwide import discover_and_publish_worldwide
from app.services.guideline_clinical_update import get_analysis, list_impacts
from app.services.guideline_clinical_update_runtime import process_pending_guidelines

router = APIRouter(prefix="/api/guideline-updates", tags=["diretrizes"])

VISIBLE_STATUSES = (
    "detected", "aguardando_revisao", "revisada", "analisada",
    "revisao_necessaria", "aplicada_auto",
)


def _current_cutoff() -> datetime:
    return max(
        DISCOVERY_START,
        datetime.now(timezone.utc) - timedelta(days=DISCOVERY_LOOKBACK_DAYS),
    )


def _summary_slug(db: Session, guideline: Guideline) -> str | None:
    link = db.query(GuidelineLink).filter(
        GuidelineLink.guideline_id == guideline.id,
        GuidelineLink.item_type == "intelligence_document",
    ).first()
    if not link:
        return None
    doc = db.get(Document, link.item_id)
    return doc.slug if doc and doc.published else None


def _guideline(db: Session, guideline: Guideline) -> dict:
    analysis = get_analysis(db, guideline) or {}
    impacts = list_impacts(db, guideline)
    return {
        "id": guideline.id,
        "slug": guideline.slug,
        "org": guideline.org,
        "title": guideline.titulo,
        "title_original": guideline.titulo,
        "title_pt": analysis.get("title_pt"),
        "summary_pt": analysis.get("summary_pt"),
        "theme": analysis.get("theme") or guideline.tema,
        "published_at": guideline.published_at,
        "discovered_at": guideline.discovered_at,
        "url": guideline.url,
        "doi": guideline.doi,
        "status": guideline.detection_status,
        "key_changes": analysis.get("key_changes") or [],
        "limitations": analysis.get("limitations") or [],
        "impacts": impacts,
        "summary_document_slug": _summary_slug(db, guideline),
        "clinical_content_changed": bool(impacts),
        "translation_mode": analysis.get("translation_mode"),
        "analyzed_at": analysis.get("analyzed_at"),
    }


@router.get("")
def list_updates(
    org: str | None = Query(None, max_length=40),
    limit: int = Query(100, ge=1, le=300),
    db: Session = Depends(get_db),
    _: User = Depends(current_user),
):
    cutoff = _current_cutoff()
    query = db.query(Guideline).filter(
        Guideline.published_at.isnot(None),
        Guideline.published_at >= cutoff,
        Guideline.detection_status.in_(VISIBLE_STATUSES),
    )
    if org:
        query = query.filter(Guideline.org == org.upper())
    guidelines = query.order_by(Guideline.published_at.desc(), Guideline.titulo).limit(limit).all()
    return {
        "cutoff": cutoff.date().isoformat(),
        "items": [_guideline(db, guideline) for guideline in guidelines],
    }


@router.get("/me")
def my_notifications(
    include_read: bool = Query(False),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    cutoff = _current_cutoff()
    query = db.query(GuidelineNotification).filter(
        GuidelineNotification.user_id == user.id,
        GuidelineNotification.channel == "in_app",
        GuidelineNotification.status == "disponivel",
    )
    if not include_read:
        query = query.filter(GuidelineNotification.read_at.is_(None))
    notifications = query.order_by(GuidelineNotification.created_at.desc()).limit(200).all()
    items = []
    for notification in notifications:
        guideline = db.get(Guideline, notification.guideline_id)
        if not guideline or not guideline.published_at or guideline.published_at < cutoff:
            continue
        item = _guideline(db, guideline)
        if item["clinical_content_changed"]:
            message = (
                f"Nova publicação analisada. O CorVIA aplicou {len(item['impacts'])} atualização(ões) "
                "clínica(s) rastreável(is); veja abaixo exatamente o que mudou."
            )
        elif item["summary_pt"]:
            message = "Nova publicação analisada e resumida em português. Nenhuma mudança automática de conduta foi aplicada."
        else:
            message = "Nova publicação oficial identificada; análise clínica em processamento."
        items.append({
            "notification_id": notification.id,
            "read_at": notification.read_at,
            "guideline": item,
            "message": message,
        })
    return {"cutoff": cutoff.date().isoformat(), "items": items}


@router.post("/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    notification = db.query(GuidelineNotification).filter(
        GuidelineNotification.id == notification_id,
        GuidelineNotification.user_id == user.id,
    ).first()
    if notification is None:
        raise HTTPException(status_code=404, detail="Alerta não encontrado.")
    notification.read_at = notification.read_at or datetime.now(timezone.utc)
    db.commit()
    return {"notification_id": notification.id, "read_at": notification.read_at}


@router.post("/admin/discover")
def run_discovery(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return discover_and_publish_worldwide(db, analyze_clinical_impact=True)


@router.post("/admin/process-pending")
def run_pending_analysis(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return process_pending_guidelines(db, limit=limit)
