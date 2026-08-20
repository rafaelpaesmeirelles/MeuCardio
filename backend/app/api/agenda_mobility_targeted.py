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
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.agenda_integrada import (
    _audit,
    _commitment_occurrences,
    _dump_location,
    _routine_calendar_occurrences,
    next_locations,
)
from app.core.config import settings
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


class CommuteFromLocationIn(BaseModel):
    origin_location_id: int = Field(gt=0)
    target_key: str = Field(min_length=3, max_length=180)


class CommuteReturnIn(BaseModel):
    origin_target_key: str = Field(min_length=3, max_length=180)
    destination_location_id: int = Field(gt=0)


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


def _day_targets(db: Session, user: User) -> list[dict[str, Any]]:
    """Materializa os pontos presenciais de hoje sem criar eventos novos."""
    now = datetime.now(timezone.utc)
    zone = ZoneInfo(settings.fuso_operacao)
    today = now.astimezone(zone).date()
    day_start = datetime.combine(today, datetime.min.time(), tzinfo=zone).astimezone(timezone.utc)
    day_end = day_start + timedelta(days=1)
    result: list[dict[str, Any]] = []

    for item in _routine_calendar_occurrences(db, user.id, today, today):
        if item.get("visit_mode") == "teleconsulta" or not item.get("location"):
            continue
        result.append(_normalizar_alvo({
            "routine_id": item.get("routine_id"), "appointment_id": None,
            "starts_at": item["starts_at"], "ends_at": item.get("ends_at"),
            "service_name": item.get("title") or "Rotina profissional",
            "title": item.get("title"), "source": "work_routine",
            "arrival_buffer_minutes": item["location"].get("default_arrival_buffer_minutes", 0),
            "location": item["location"],
        }))

    appointments = db.query(Appointment).filter(
        Appointment.owner_id == user.id,
        Appointment.deleted_at.is_(None),
        Appointment.status.notin_(("cancelado", "faltou")),
        Appointment.scheduled_at >= day_start,
        Appointment.scheduled_at < day_end,
        Appointment.location_id.is_not(None),
    ).all()
    for item in appointments:
        if item.visit_mode == "teleconsulta":
            continue
        location = db.get(CalendarLocation, item.location_id)
        if not location or not location.active:
            continue
        result.append(_normalizar_alvo({
            "routine_id": None, "appointment_id": item.id,
            "starts_at": item.scheduled_at, "ends_at": item.ends_at,
            "service_name": item.appointment_type, "title": _appointment_title(db, item),
            "source": "appointment",
            "arrival_buffer_minutes": location.default_arrival_buffer_minutes,
            "location": _dump_location(location),
        }))

    for item in _commitment_occurrences(db, user.id, today, today, include_cancelled=False):
        location = item.get("location")
        if item.get("visit_mode") == "teleconsulta" or not location:
            continue
        commitment_id = str(item.get("id") or "")
        if not commitment_id:
            continue
        result.append({
            "routine_id": None, "appointment_id": None,
            "commitment_id": commitment_id, "target_key": commitment_id,
            "target_type": "commitment", "starts_at": item["starts_at"],
            "ends_at": item.get("ends_at"),
            "service_name": item.get("title") or "Compromisso",
            "title": item.get("title") or "Compromisso", "source": "commitment",
            "arrival_buffer_minutes": location.get("default_arrival_buffer_minutes", 0),
            "location": location,
        })
    return sorted(result, key=lambda item: item["starts_at"])


def _find_day_target(db: Session, user: User, target_key: str) -> dict[str, Any] | None:
    return next((item for item in _day_targets(db, user) if item.get("target_key") == target_key), None)


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


def _mobility_pref(db: Session, user: User) -> MobilityPreference:
    pref = db.query(MobilityPreference).filter(
        MobilityPreference.owner_id == user.id,
        MobilityPreference.enabled.is_(True),
    ).first()
    if pref is None:
        raise HTTPException(status_code=403, detail="Ative o deslocamento inteligente na Agenda.")
    return pref


def _saved_location(db: Session, user: User, location_id: int) -> CalendarLocation:
    location = db.query(CalendarLocation).filter(
        CalendarLocation.id == location_id,
        CalendarLocation.owner_id == user.id,
        CalendarLocation.active.is_(True),
    ).first()
    if location is None:
        raise HTTPException(status_code=404, detail="Local de deslocamento não encontrado.")
    return location


def _geocoded_location(db: Session, user: User, location: CalendarLocation) -> dict[str, Any]:
    target = _ensure_geocoded(db, user, {"location": _dump_location(location)})
    return target["location"]


def _route_between_locations(
    *, origin: dict[str, Any], destination: dict[str, Any], arrival_buffer_minutes: int,
) -> dict[str, Any]:
    if origin.get("latitude") is None or origin.get("longitude") is None:
        return {"status": "origin_not_geocoded", "routes": [], "tips": []}
    if destination.get("latitude") is None or destination.get("longitude") is None:
        return {"status": "destination_not_geocoded", "routes": [], "tips": []}
    try:
        return traffic_eta(
            origin_latitude=origin["latitude"], origin_longitude=origin["longitude"],
            destination_latitude=destination["latitude"],
            destination_longitude=destination["longitude"],
            arrival_buffer_minutes=arrival_buffer_minutes,
        )
    except ConnectorError as exc:
        raise HTTPException(
            status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)},
        ) from exc


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


@router.get("/mobility/day-context")
def day_context(db: Session = Depends(get_db), user: User = Depends(current_user)):
    targets = _day_targets(db, user)
    pref = db.query(MobilityPreference).filter(MobilityPreference.owner_id == user.id).first()
    start_location = db.get(CalendarLocation, pref.day_start_location_id) if pref and pref.day_start_location_id else None
    end_location = db.get(CalendarLocation, pref.day_end_destination_location_id) if pref and pref.day_end_destination_location_id else None
    if start_location and (start_location.owner_id != user.id or not start_location.active):
        start_location = None
    if end_location and (end_location.owner_id != user.id or not end_location.active):
        end_location = None
    if not targets:
        return {"stage": "no_commitments", "first_target": None, "last_target": None,
                "start_location": _dump_location(start_location) if start_location else None,
                "end_location": _dump_location(end_location) if end_location else None}
    first = min(targets, key=lambda item: item["starts_at"])
    last = max(targets, key=lambda item: item.get("ends_at") or item["starts_at"])
    now = datetime.now(timezone.utc)
    stage = "before_first" if now < first["starts_at"] else "at_last" if now >= last["starts_at"] else "active_day"
    return {
        "stage": stage, "first_target": first, "last_target": last,
        "start_location": _dump_location(start_location) if start_location else None,
        "end_location": _dump_location(end_location) if end_location else None,
    }


@router.post("/mobility/commute-target-from-location")
def commute_target_from_location(
    data: CommuteFromLocationIn, db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    pref = _mobility_pref(db, user)
    if pref.day_start_origin_mode != "saved_location" or pref.day_start_location_id != data.origin_location_id:
        raise HTTPException(status_code=409, detail="A origem salva não corresponde à preferência atual.")
    destination = _find_target(db, user, data.target_key)
    if destination is None:
        return {"status": "destination_mismatch", "destination": None, "routes": [], "tips": []}
    destination = _ensure_geocoded(db, user, destination)
    origin_location = _saved_location(db, user, data.origin_location_id)
    origin = _geocoded_location(db, user, origin_location)
    destination_location = destination.get("location")
    if not destination_location:
        return {"status": "destination_without_location", "destination": destination,
                "origin_location": origin, "routes": [], "tips": []}
    result = _route_between_locations(
        origin=origin, destination=destination_location,
        arrival_buffer_minutes=destination.get("arrival_buffer_minutes", 0),
    )
    _audit(db, user, "mobility_saved_origin_eta_lookup", "calendar_location", destination_location["id"], {
        "origin_location_id": origin_location.id, "provider": result.get("provider"),
        "status": result.get("status"),
    })
    db.commit()
    return {**result, "destination": destination, "origin_location": origin}


@router.post("/mobility/commute-return")
def commute_return(
    data: CommuteReturnIn, db: Session = Depends(get_db), user: User = Depends(current_user),
):
    pref = _mobility_pref(db, user)
    if pref.day_end_destination_location_id != data.destination_location_id:
        raise HTTPException(status_code=409, detail="O destino final não corresponde à preferência atual.")
    origin_target = _find_day_target(db, user, data.origin_target_key)
    if origin_target is None:
        return {"status": "origin_mismatch", "destination": None, "routes": [], "tips": []}
    origin_target = _ensure_geocoded(db, user, origin_target)
    origin = origin_target.get("location")
    if not origin:
        return {"status": "origin_without_location", "destination": None, "routes": [], "tips": []}
    destination_model = _saved_location(db, user, data.destination_location_id)
    destination_location = _geocoded_location(db, user, destination_model)
    target_key = f"return:{data.origin_target_key}:{destination_model.id}"
    destination = {
        "target_key": target_key, "target_type": "day_return",
        "appointment_id": None, "routine_id": None, "commitment_id": None,
        "starts_at": origin_target.get("ends_at") or origin_target["starts_at"],
        "ends_at": None, "service_name": "Retorno", "title": f"Retorno para {destination_model.name}",
        "source": "return", "arrival_buffer_minutes": 0, "location": destination_location,
    }
    result = _route_between_locations(
        origin=origin, destination=destination_location, arrival_buffer_minutes=0,
    )
    _audit(db, user, "mobility_return_eta_lookup", "calendar_location", destination_model.id, {
        "origin_location_id": origin["id"], "provider": result.get("provider"),
        "status": result.get("status"),
    })
    db.commit()
    return {**result, "destination": destination, "origin_location": origin}


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
