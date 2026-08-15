"""Mobilidade fail-closed para o próximo destino real da Agenda.

Este router é incluído dentro de ``agenda_integrada.router`` e, portanto, não
repete o prefixo ``/api/agenda``. Mantém o endpoint direcionado por
``appointment_id`` por compatibilidade e acrescenta um alvo canônico capaz de
representar atendimento, rotina de trabalho ou compromisso manual/recorrente.

A origem do usuário nunca é persistida nem entra na auditoria. Quando o destino
já cadastrado ainda não tem coordenadas, a própria preparação/solicitação do
Próximo Deslocamento pode geocodificá-lo server-side usando os provedores já
configurados no CorVIA; nenhuma coordenada é inventada.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.agenda_integrada import _audit, _commitment_occurrences, next_locations
from app.core.db import get_db
from app.core.security import current_user
from app.models.agenda import CalendarLocation, MobilityPreference
from app.models.clinical_docs import Appointment
from app.models.round import Patient
from app.models.user import User
from app.services.agenda_integrada.connectors import ConnectorError
from app.services.agenda_integrada.geocoding import GeocodingError, geocode_address
from app.services.agenda_integrada.traffic import traffic_eta

router = APIRouter(tags=["agenda-integrada"])


class CommuteAppointmentIn(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    appointment_id: int = Field(gt=0)


class CommuteTargetIn(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    target_key: str = Field(min_length=3, max_length=180)


def _iso(value: Any) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _normalizar_alvo(item: dict[str, Any]) -> dict[str, Any]:
    source = item.get("source")
    if source == "appointment":
        target_key = f"appointment:{item.get('appointment_id')}"
        target_type = "appointment"
    elif source == "work_routine":
        target_key = f"routine:{item.get('routine_id')}:{_iso(item.get('starts_at'))}"
        target_type = "work_routine"
    else:
        target_key = str(item.get("target_key") or item.get("commitment_id") or "")
        target_type = str(item.get("target_type") or source or "commitment")
    return {**item, "target_key": target_key, "target_type": target_type}


def _compromissos_manuais(db: Session, user: User, *, days: int = 14) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc)
    start_date = (now - timedelta(days=1)).date()
    end_date = (now + timedelta(days=days)).date()
    occurrences = _commitment_occurrences(
        db, user.id, start_date, end_date, include_cancelled=False,
    )
    result: list[dict[str, Any]] = []
    for item in occurrences:
        starts_at = item.get("starts_at")
        if starts_at is None or starts_at < now:
            continue
        location = item.get("location")
        commitment_id = str(item.get("id") or "")
        if not commitment_id:
            continue
        result.append({
            "routine_id": None,
            "appointment_id": None,
            "commitment_id": commitment_id,
            "target_key": commitment_id,
            "target_type": "commitment",
            "starts_at": starts_at,
            "ends_at": item.get("ends_at"),
            "service_name": item.get("title") or item.get("appointment_type") or "Compromisso",
            "title": item.get("title") or "Compromisso",
            "routine_type": None,
            "visit_mode": item.get("visit_mode") or "presencial",
            "arrival_buffer_minutes": (location or {}).get("default_arrival_buffer_minutes", 15),
            "planning_notes": item.get("notes"),
            "source": "commitment",
            "location": location,
        })
    return result


def _appointment_title(db: Session, appointment: Appointment) -> str:
    nome = appointment.patient_name_temp
    if appointment.patient_id:
        patient = db.get(Patient, appointment.patient_id)
        if patient:
            nome = f"{patient.initials} (prontuário {patient.record_number})"
    return nome or "Compromisso"


def _upcoming_targets(db: Session, user: User, *, limit: int = 25) -> list[dict[str, Any]]:
    # ``next_locations`` continua sendo a fonte canônica das rotinas e dos
    # atendimentos. Somamos as ocorrências de commitment-series porque elas
    # vivem em outra tabela e, até aqui, eram invisíveis para a Home.
    locations = next_locations(limit=10, professional_id=user.id, db=db, user=user)
    result: list[dict[str, Any]] = []
    for item in locations:
        target = _normalizar_alvo(item)
        # ``next_locations`` foi concebido para mobilidade e não carrega a
        # identidade do paciente. Para não regredir a Home ao trocar a fonte
        # canônica, reaplicamos a mesma apresentação usada pela Agenda.
        if target.get("source") == "appointment" and target.get("appointment_id"):
            appointment = db.get(Appointment, target["appointment_id"])
            if appointment and appointment.owner_id == user.id and appointment.deleted_at is None:
                target["title"] = _appointment_title(db, appointment)
        result.append(target)
    result.extend(_compromissos_manuais(db, user))
    result.sort(key=lambda item: item["starts_at"])
    return result[:limit]


def _find_target(db: Session, user: User, target_key: str) -> dict[str, Any] | None:
    return next((item for item in _upcoming_targets(db, user) if item.get("target_key") == target_key), None)


def _location_query(location: CalendarLocation) -> str:
    address = location.address or {}
    ordered_keys = (
        "street", "number", "complement", "neighborhood", "district",
        "city", "state", "postal_code", "zip", "country",
    )
    parts = [str(address.get(key) or "").strip() for key in ordered_keys]
    parts = [part for part in parts if part]
    if location.name:
        parts.insert(0, location.name.strip())
    return ", ".join(dict.fromkeys(parts))


def _ensure_geocoded(db: Session, user: User, target: dict[str, Any]) -> dict[str, Any]:
    payload = target.get("location") or {}
    location_id = payload.get("id")
    if not location_id:
        return target
    if payload.get("latitude") is not None and payload.get("longitude") is not None:
        return target

    location = db.query(CalendarLocation).filter(
        CalendarLocation.id == location_id,
        CalendarLocation.owner_id == user.id,
        CalendarLocation.active.is_(True),
    ).first()
    if location is None:
        return target

    query = _location_query(location)
    if len(query) < 5:
        return target
    try:
        geocoded = geocode_address(query)
    except GeocodingError:
        return target

    location.latitude = geocoded["latitude"]
    location.longitude = geocoded["longitude"]
    _audit(db, user, "mobility_destination_geocode", "calendar_location", location.id, {
        "provider": geocoded.get("provider"), "status": "ok",
    })
    db.commit()
    return {
        **target,
        "location": {
            **payload,
            "latitude": location.latitude,
            "longitude": location.longitude,
        },
    }


@router.get("/mobility/next-target")
def next_target(db: Session = Depends(get_db), user: User = Depends(current_user)):
    targets = _upcoming_targets(db, user, limit=1)
    if not targets:
        return None
    return targets[0]


@router.post("/mobility/prepare-next-target")
def prepare_next_target(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Prepara somente o destino armazenado do próximo compromisso.

    Um local textual já cadastrado pode ser geocodificado para que a Home abra
    com o mapa do destino, independentemente do consentimento para usar a posição
    atual do profissional. Esse endpoint não recebe, solicita nem processa a
    origem ao vivo e não calcula rota/ETA. O consentimento revogável continua
    obrigatório no POST ``commute-target``, que é a única etapa que usa a
    geolocalização atual para trânsito e deslocamento.
    """
    targets = _upcoming_targets(db, user, limit=1)
    if not targets:
        return None
    target = targets[0]
    if target.get("location"):
        target = _ensure_geocoded(db, user, target)
    return target


@router.post("/mobility/commute-target")
def commute_target(data: CommuteTargetIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    pref = db.query(MobilityPreference).filter(
        MobilityPreference.owner_id == user.id,
        MobilityPreference.enabled.is_(True),
    ).first()
    if not pref:
        raise HTTPException(status_code=403, detail="Ative o consentimento de localização na conta.")

    destination = _find_target(db, user, data.target_key)
    if destination is None:
        return {"status": "destination_mismatch", "destination": None, "routes": [], "tips": []}
    destination = _ensure_geocoded(db, user, destination)
    location = destination.get("location")
    if not location:
        return {"status": "destination_without_location", "destination": destination, "routes": [], "tips": []}
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


@router.post("/mobility/commute-appointment")
def commute_appointment(data: CommuteAppointmentIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Compatibilidade com clientes anteriores, mantendo o contrato estrito por appointment_id."""
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
