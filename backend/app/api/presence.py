from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.user import User
from app.services.professional_profile import council_display

router = APIRouter(prefix="/api/presence", tags=["presença online"])

ONLINE_WINDOW = timedelta(minutes=5)


class PresencePreferenceIn(BaseModel):
    visible: bool


def _public_user(user: User) -> dict:
    nome_conselho, estado_conselho = council_display(user)
    council = " ".join(
        part for part in (nome_conselho, user.council_number) if part
    )
    if estado_conselho:
        council = f"{council}/{estado_conselho}".strip("/")
    return {
        "id": user.id,
        "full_name": user.full_name,
        "profession": user.profession,
        "specialty": user.specialty,
        "council": council or None,
        "last_seen_at": user.last_seen_at,
    }


@router.get("/me")
def my_preference(user: User = Depends(current_user)):
    return {
        "visible": bool(user.show_online_status),
        "online_window_minutes": int(ONLINE_WINDOW.total_seconds() // 60),
    }


@router.put("/me")
def update_preference(
    data: PresencePreferenceIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    user.show_online_status = data.visible
    db.commit()
    return {
        "visible": bool(user.show_online_status),
        "updated_at": datetime.now(timezone.utc),
    }


@router.get("/online")
def online_users(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    threshold = datetime.now(timezone.utc) - ONLINE_WINDOW
    users = (
        db.query(User)
        .filter(
            User.id != user.id,
            User.is_active.is_(True),
            User.status == "aprovado",
            User.show_online_status.is_(True),
            User.last_seen_at.isnot(None),
            User.last_seen_at >= threshold,
        )
        .order_by(User.full_name)
        .all()
    )
    return {
        "online_window_minutes": int(ONLINE_WINDOW.total_seconds() // 60),
        "items": [_public_user(item) for item in users],
    }
