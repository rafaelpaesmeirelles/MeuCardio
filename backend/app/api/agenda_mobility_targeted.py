"""Extensão fail-closed da mobilidade para um compromisso específico.

Este router é incluído dentro de `agenda_integrada.router`, portanto não repete o
prefixo `/api/agenda`. Reutiliza o motor de tráfego existente e não grava a
origem do usuário.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.agenda_integrada import _audit, next_locations
from app.core.db import get_db
from app.core.security import current_user
from app.models.agenda import MobilityPreference
from app.models.user import User
from app.services.agenda_integrada.connectors import ConnectorError
from app.services.agenda_integrada.traffic import traffic_eta

router = APIRouter(tags=["agenda-integrada"])


class CommuteAppointmentIn(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    appointment_id: int = Field(gt=0)


@router.post("/mobility/commute-appointment")
def commute_appointment(data: CommuteAppointmentIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    pref = db.query(MobilityPreference).filter(
        MobilityPreference.owner_id == user.id,
        MobilityPreference.enabled.is_(True),
    ).first()
    if not pref:
        raise HTTPException(status_code=403, detail="Ative o consentimento de localização na conta.")

    destination = next((item for item in next_locations(limit=10, professional_id=user.id, db=db, user=user)
                        if item.get("appointment_id") == data.appointment_id and item.get("source") == "appointment"), None)
    if destination is None:
        return {"status": "destination_mismatch", "destination": None, "routes": [], "tips": []}

    location = destination["location"]
    if location.get("latitude") is None or location.get("longitude") is None:
        return {"status": "destination_not_geocoded", "destination": destination, "routes": [], "tips": []}

    try:
        result = traffic_eta(
            origin_latitude=data.latitude,
            origin_longitude=data.longitude,
            destination_latitude=location["latitude"],
            destination_longitude=location["longitude"],
            arrival_buffer_minutes=destination.get("arrival_buffer_minutes", 0),
        )
    except ConnectorError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)}) from exc

    _audit(db, user, "mobility_eta_lookup", "calendar_location", location["id"], {
        "provider": result.get("provider"), "status": result.get("status"),
    })
    db.commit()
    return {**result, "destination": destination}
