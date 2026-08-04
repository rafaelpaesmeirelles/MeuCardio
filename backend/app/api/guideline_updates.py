from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user, require_admin
from app.models.guideline import Guideline, GuidelineNotification
from app.models.user import User
from app.services.guideline_discovery import CUTOFF, discover_and_publish

router = APIRouter(prefix="/api/guideline-updates", tags=["diretrizes"])


def _guideline(guideline: Guideline) -> dict:
    return {
        "id": guideline.id,
        "slug": guideline.slug,
        "org": guideline.org,
        "title": guideline.titulo,
        "published_at": guideline.published_at,
        "discovered_at": guideline.discovered_at,
        "url": guideline.url,
        "status": guideline.detection_status,
        "clinical_content_changed": False,
    }


@router.get("")
def list_updates(
    org: str | None = Query(None, max_length=40),
    limit: int = Query(100, ge=1, le=300),
    db: Session = Depends(get_db),
    _: User = Depends(current_user),
):
    query = db.query(Guideline).filter(
        Guideline.published_at.isnot(None),
        Guideline.published_at >= CUTOFF,
        Guideline.detection_status.in_(("detected", "aguardando_revisao", "revisada")),
    )
    if org:
        query = query.filter(Guideline.org == org.upper())
    guidelines = query.order_by(Guideline.published_at.desc(), Guideline.titulo).limit(limit).all()
    return {
        "cutoff": CUTOFF.date().isoformat(),
        "items": [_guideline(guideline) for guideline in guidelines],
    }


@router.get("/me")
def my_notifications(
    include_read: bool = Query(False),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
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
        if not guideline or not guideline.published_at or guideline.published_at < CUTOFF:
            continue
        items.append({
            "notification_id": notification.id,
            "read_at": notification.read_at,
            "guideline": _guideline(guideline),
            "message": (
                "Nova publicação oficial identificada. O conteúdo clínico relacionado "
                "permanece em revisão e não foi modificado automaticamente."
            ),
        })
    return {"cutoff": CUTOFF.date().isoformat(), "items": items}


@router.post("/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    notification = db.query(GuidelineNotification).filter(
        GuidelineNotification.id == notification_id,
        GuidelineNotification.user_id == user.id,
        GuidelineNotification.channel == "in_app",
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
    return discover_and_publish(db)
