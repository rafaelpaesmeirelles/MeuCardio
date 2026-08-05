from datetime import datetime, timedelta, timezone

from app.models.agenda import AppointmentCommunication
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _location(client, token: str, name="Consultório Paulista") -> dict:
    response = client.post("/api/agenda/locations", headers=_headers(token), json={
        "name": name,
        "timezone": "America/Sao_Paulo",
        "address": {"city": "São Paulo", "state": "SP"},
        "latitude": -23.5614,
        "longitude": -46.6559,
        "default_arrival_buffer_minutes": 20,
    })
    assert response.status_code == 201, response.text
    return response.json()


def test_tenant_cannot_read_or_configure_another_professionals_agenda(client, criar_usuario, db):
    owner, owner_token = criar_usuario(email="agenda.owner@teste.local")
    intruder, intruder_token = criar_usuario(email="agenda.intruder@teste.local")
    _subscribe(db, owner.id)
    _subscribe(db, intruder.id)
    _location(client, owner_token)

    listing = client.get(
        f"/api/agenda/locations?professional_id={owner.id}", headers=_headers(intruder_token)
    )
    assert listing.status_code == 403

    creation = client.post(
        f"/api/agenda/locations?professional_id={owner.id}",
        headers=_headers(intruder_token),
        json={"name": "Local indevido"},
    )
    assert creation.status_code == 403


def test_conflict_is_rejected_and_extra_slot_requires_service_permission(client, criar_usuario, db):
    user, token = criar_usuario(email="agenda.conflict@teste.local")
    _subscribe(db, user.id)
    location = _location(client, token)
    service_response = client.post("/api/agenda/services", headers=_headers(token), json={
        "location_id": location["id"], "code": "consulta-cardio",
        "name": "Consulta cardiológica", "duration_minutes": 30,
        "allow_extra_slot": False,
    })
    assert service_response.status_code == 201, service_response.text
    service = service_response.json()
    starts_at = (datetime.now(timezone.utc) + timedelta(days=2)).replace(minute=0, second=0, microsecond=0)
    payload = {
        "patient_name": "Paciente Teste", "starts_at": starts_at.isoformat(),
        "service_id": service["id"], "location_id": location["id"],
    }
    first = client.post("/api/agenda/appointments", headers=_headers(token), json=payload)
    assert first.status_code == 201, first.text
    second = client.post("/api/agenda/appointments", headers=_headers(token), json=payload)
    assert second.status_code == 409
    assert second.json()["detail"]["code"] == "schedule_conflict"
    forced = client.post(
        "/api/agenda/appointments", headers=_headers(token), json={**payload, "allow_extra_slot": True}
    )
    assert forced.status_code == 409


def test_patient_email_requires_explicit_consent_and_is_never_returned(client, criar_usuario, db):
    user, token = criar_usuario(email="agenda.email@teste.local")
    _subscribe(db, user.id)
    starts_at = datetime.now(timezone.utc) + timedelta(days=3)
    rejected = client.post("/api/agenda/appointments", headers=_headers(token), json={
        "patient_name": "Paciente", "patient_email": "paciente@example.com",
        "starts_at": starts_at.isoformat(),
    })
    assert rejected.status_code == 422
    accepted = client.post("/api/agenda/appointments", headers=_headers(token), json={
        "patient_name": "Paciente", "patient_email": "paciente@example.com",
        "email_consent": True, "starts_at": starts_at.isoformat(),
    })
    assert accepted.status_code == 201, accepted.text
    assert accepted.json()["has_patient_email"] is True
    assert "patient_email" not in accepted.json()


def test_mobility_consent_persists_preference_but_not_coordinates(client, criar_usuario, db):
    user, token = criar_usuario(email="agenda.mobility@teste.local")
    _subscribe(db, user.id)
    rejected = client.put("/api/agenda/mobility/preferences", headers=_headers(token), json={
        "enabled": True, "consent_accepted": False,
    })
    assert rejected.status_code == 422
    accepted = client.put("/api/agenda/mobility/preferences", headers=_headers(token), json={
        "enabled": True, "consent_accepted": True,
        "automatic_foreground_refresh": True, "refresh_interval_minutes": 5,
    })
    assert accepted.status_code == 200, accepted.text
    body = accepted.json()
    assert body["enabled"] is True
    assert "latitude" not in body and "longitude" not in body


def test_unverified_feegow_connector_cannot_enable_writes(client, criar_usuario, db):
    user, token = criar_usuario(email="agenda.feegow@teste.local")
    _subscribe(db, user.id)
    response = client.post("/api/agenda/integrations", headers=_headers(token), json={
        "provider": "feegow", "display_name": "Feegow consultório",
        "write_enabled": True, "consent_accepted": True,
    })
    assert response.status_code == 409

    created = client.post("/api/agenda/integrations", headers=_headers(token), json={
        "provider": "feegow", "display_name": "Feegow consultório",
        "consent_accepted": True,
    })
    assert created.status_code == 201, created.text
    integration_id = created.json()["id"]
    diagnostic = client.post(
        f"/api/agenda/integrations/{integration_id}/diagnose", headers=_headers(token)
    )
    assert diagnostic.status_code == 200
    assert diagnostic.json()["code"] == "homologation_required"


def test_work_routine_drives_daily_plan_and_rejects_overlap(client, criar_usuario, db):
    user, token = criar_usuario(email="agenda.routine@teste.local")
    _subscribe(db, user.id)
    location = _location(client, token, name="Hospital Central")
    target_weekday = (datetime.now(timezone.utc) + timedelta(days=1)).weekday()
    payload = {
        "location_id": location["id"],
        "weekdays": [target_weekday],
        "start_time": "08:00:00",
        "end_time": "18:00:00",
        "label": "Consultório diário",
        "routine_type": "atendimento",
        "visit_mode": "presencial",
        "arrival_buffer_minutes": 25,
        "planning_notes": "Entrada pela recepção principal.",
    }
    created = client.post("/api/agenda/work-routines", headers=_headers(token), json=payload)
    assert created.status_code == 201, created.text
    assert created.json()[0]["arrival_buffer_minutes"] == 25

    overlap = client.post("/api/agenda/work-routines", headers=_headers(token), json={
        **payload, "start_time": "17:30:00", "end_time": "19:00:00",
    })
    assert overlap.status_code == 409
    assert overlap.json()["detail"]["code"] == "routine_conflict"

    next_locations = client.get(
        "/api/agenda/workday/next-locations", headers=_headers(token)
    )
    assert next_locations.status_code == 200, next_locations.text
    assert next_locations.json()[0]["source"] == "work_routine"
    assert next_locations.json()[0]["location"]["name"] == "Hospital Central"

    plan = client.get("/api/agenda/workday/plan?days=14", headers=_headers(token))
    assert plan.status_code == 200, plan.text
    assert plan.json()["summary"]["work_periods"] >= 1
    assert plan.json()["routines"][0]["planning_notes"] == "Entrada pela recepção principal."


def test_recurring_commitment_allows_single_occurrence_override(client, criar_usuario, db):
    user, token = criar_usuario(email="agenda.recorrencia@teste.local")
    _subscribe(db, user.id)
    first_date = (datetime.now(timezone.utc) + timedelta(days=3)).date()
    created = client.post("/api/agenda/commitment-series", headers=_headers(token), json={
        "title": "Reunião do corpo clínico",
        "category": "reuniao",
        "timezone": "UTC",
        "starts_on": first_date.isoformat(),
        "start_time": "09:00:00",
        "duration_minutes": 60,
        "recurrence": "weekly",
        "weekdays": [first_date.weekday()],
        "blocks_scheduling": True,
    })
    assert created.status_code == 201, created.text
    series_id = created.json()["id"]

    end_date = first_date + timedelta(days=20)
    occurrences = client.get(
        f"/api/agenda/commitments?start={first_date.isoformat()}&end={end_date.isoformat()}",
        headers=_headers(token),
    )
    assert occurrences.status_code == 200, occurrences.text
    assert len(occurrences.json()) == 3
    assert all(item["calendar_kind"] == "commitment" for item in occurrences.json())

    moved_start = datetime.combine(first_date, datetime.min.time(), tzinfo=timezone.utc).replace(hour=14)
    exception = client.put(
        f"/api/agenda/commitment-series/{series_id}/exceptions",
        headers=_headers(token),
        json={
            "occurrence_date": first_date.isoformat(), "action": "override",
            "starts_at": moved_start.isoformat(),
            "ends_at": (moved_start + timedelta(minutes=90)).isoformat(),
            "title": "Reunião excepcional",
        },
    )
    assert exception.status_code == 200, exception.text

    refreshed = client.get(
        f"/api/agenda/commitments?start={first_date.isoformat()}&end={end_date.isoformat()}",
        headers=_headers(token),
    ).json()
    assert refreshed[0]["title"] == "Reunião excepcional"
    assert refreshed[0]["duration_minutes"] == 90
    assert refreshed[0]["is_exception"] is True
    assert refreshed[1]["title"] == "Reunião do corpo clínico"
    assert refreshed[1]["duration_minutes"] == 60
    assert refreshed[1]["is_exception"] is False


def test_blocking_manual_commitment_rejects_patient_double_booking(client, criar_usuario, db):
    user, token = criar_usuario(email="agenda.bloqueio-manual@teste.local")
    _subscribe(db, user.id)
    commitment_date = (datetime.now(timezone.utc) + timedelta(days=4)).date()
    created = client.post("/api/agenda/commitment-series", headers=_headers(token), json={
        "title": "Plantão externo",
        "category": "plantao",
        "timezone": "UTC",
        "starts_on": commitment_date.isoformat(),
        "start_time": "15:00:00",
        "duration_minutes": 180,
        "recurrence": "none",
        "blocks_scheduling": True,
    })
    assert created.status_code == 201, created.text

    appointment_start = datetime.combine(
        commitment_date, datetime.min.time(), tzinfo=timezone.utc,
    ).replace(hour=16)
    appointment = client.post("/api/agenda/appointments", headers=_headers(token), json={
        "patient_name": "Paciente em conflito",
        "starts_at": appointment_start.isoformat(),
        "duration_minutes": 30,
    })
    assert appointment.status_code == 409, appointment.text
    assert appointment.json()["detail"]["code"] == "schedule_conflict"
    assert appointment.json()["detail"]["conflicts"][0]["reason"] == "manual_commitment"


def test_resource_cannot_reference_another_tenant_location(client, criar_usuario, db):
    owner, owner_token = criar_usuario(email="agenda.resource.owner@teste.local")
    other, other_token = criar_usuario(email="agenda.resource.other@teste.local")
    _subscribe(db, owner.id); _subscribe(db, other.id)
    location = _location(client, owner_token, name="Local privado")
    response = client.post("/api/agenda/resources", headers=_headers(other_token), json={
        "location_id": location["id"], "name": "Sala invasiva",
    })
    assert response.status_code == 404


def test_appointment_and_service_update_reject_cross_tenant_references(client, criar_usuario, db):
    owner, owner_token = criar_usuario(email="agenda.reference.owner@teste.local")
    other, other_token = criar_usuario(email="agenda.reference.other@teste.local")
    _subscribe(db, owner.id); _subscribe(db, other.id)
    owner_location = _location(client, owner_token, name="Local confidencial")
    service_response = client.post("/api/agenda/services", headers=_headers(owner_token), json={
        "location_id": owner_location["id"], "code": "privado-cardio",
        "name": "Serviço privado", "duration_minutes": 30,
    })
    assert service_response.status_code == 201, service_response.text
    owner_service = service_response.json()

    appointment = client.post("/api/agenda/appointments", headers=_headers(other_token), json={
        "patient_name": "Paciente", "starts_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        "service_id": owner_service["id"],
    })
    assert appointment.status_code == 404

    other_location = _location(client, other_token, name="Local do segundo profissional")
    other_service = client.post("/api/agenda/services", headers=_headers(other_token), json={
        "location_id": other_location["id"], "code": "servico-outro",
        "name": "Serviço do segundo profissional",
    })
    assert other_service.status_code == 201, other_service.text
    update = client.patch(
        f"/api/agenda/services/{other_service.json()['id']}",
        headers=_headers(other_token),
        json={
            "location_id": owner_location["id"], "code": "servico-outro",
            "name": "Serviço do segundo profissional",
        },
    )
    assert update.status_code == 404


def test_reschedule_rejects_resource_owned_by_another_professional(client, criar_usuario, db):
    owner, owner_token = criar_usuario(email="agenda.reschedule.owner@teste.local")
    other, other_token = criar_usuario(email="agenda.reschedule.other@teste.local")
    _subscribe(db, owner.id); _subscribe(db, other.id)
    owner_location = _location(client, owner_token, name="Centro de procedimentos")
    resource = client.post("/api/agenda/resources", headers=_headers(owner_token), json={
        "location_id": owner_location["id"], "name": "Sala exclusiva",
    })
    assert resource.status_code == 201, resource.text
    start = datetime.now(timezone.utc) + timedelta(days=4)
    appointment = client.post("/api/agenda/appointments", headers=_headers(other_token), json={
        "patient_name": "Paciente", "starts_at": start.isoformat(),
    })
    assert appointment.status_code == 201, appointment.text
    response = client.post(
        f"/api/agenda/appointments/{appointment.json()['id']}/reschedule",
        headers=_headers(other_token),
        json={"starts_at": (start + timedelta(hours=1)).isoformat(), "resource_ids": [resource.json()["id"]]},
    )
    assert response.status_code == 404


def test_integration_without_external_write_confirms_locally_and_queues_email(client, criar_usuario, db):
    user, token = criar_usuario(email="agenda.local-confirmation@teste.local")
    _subscribe(db, user.id)
    integration = client.post("/api/agenda/integrations", headers=_headers(token), json={
        "provider": "google_calendar", "display_name": "Google somente leitura",
        "sync_strategy": "bidirectional", "enabled": True, "write_enabled": False,
        "consent_accepted": True,
    })
    assert integration.status_code == 201, integration.text
    appointment = client.post("/api/agenda/appointments", headers=_headers(token), json={
        "patient_name": "Paciente", "patient_email": "paciente@example.com",
        "email_consent": True, "starts_at": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
        "integration_id": integration.json()["id"],
    })
    assert appointment.status_code == 201, appointment.text
    assert appointment.json()["status"] == "confirmado"
    assert appointment.json()["confirmation_status"] == "confirmed"
    assert appointment.json()["sync_status"] == "write_disabled"
    assert db.query(AppointmentCommunication).filter(
        AppointmentCommunication.appointment_id == appointment.json()["id"],
        AppointmentCommunication.purpose == "confirmation",
    ).count() == 1


def test_integration_rejects_invalid_timezone(client, criar_usuario, db):
    user, token = criar_usuario(email="agenda.invalid-timezone@teste.local")
    _subscribe(db, user.id)
    response = client.post("/api/agenda/integrations", headers=_headers(token), json={
        "provider": "google_calendar", "display_name": "Google inválido",
        "configuration": {"timezone": "Mars/Olympus"}, "consent_accepted": True,
    })
    assert response.status_code == 422
