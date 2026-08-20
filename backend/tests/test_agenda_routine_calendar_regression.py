from datetime import date, timedelta
from pathlib import Path

from app.models.agenda import AvailabilityRule, CalendarLocation, MobilityPreference
from app.models.subscription import Subscription


ROOT = Path(__file__).resolve().parents[2]


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_work_routine_is_materialized_in_calendar_without_duplicate_rows(client, criar_usuario, db):
    user, token = criar_usuario(email="agenda.routine-calendar@teste.local")
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()

    location_response = client.post("/api/agenda/locations", headers=_headers(token), json={
        "name": "Hospital da rotina",
        "timezone": "America/Sao_Paulo",
        "address": {"city": "Ribeirão Preto", "state": "SP"},
    })
    assert location_response.status_code == 201, location_response.text

    target = date.today() + timedelta(days=2)
    routine_response = client.post("/api/agenda/work-routines", headers=_headers(token), json={
        "location_id": location_response.json()["id"],
        "weekdays": [target.weekday()],
        "start_time": "09:00:00",
        "end_time": "12:00:00",
        "label": "Enfermaria de Cardiologia",
        "routine_type": "atendimento",
        "valid_from": target.isoformat(),
        "valid_until": target.isoformat(),
    })
    assert routine_response.status_code == 201, routine_response.text
    routine_id = routine_response.json()[0]["id"]
    row_count = db.query(AvailabilityRule).filter(AvailabilityRule.owner_id == user.id).count()

    occurrences = client.get(
        "/api/agenda/work-routines/occurrences",
        headers=_headers(token),
        params={"start": target.isoformat(), "end": target.isoformat()},
    )
    assert occurrences.status_code == 200, occurrences.text
    assert len(occurrences.json()) == 1
    item = occurrences.json()[0]
    assert item["calendar_kind"] == "work_routine"
    assert item["routine_id"] == routine_id
    assert item["occurrence_date"] == target.isoformat()
    assert item["title"] == "Enfermaria de Cardiologia"
    assert item["source"] == "work_routine"
    assert item["status"] == "rotina"
    assert item["location"]["name"] == "Hospital da rotina"
    assert db.query(AvailabilityRule).filter(AvailabilityRule.owner_id == user.id).count() == row_count


def test_agenda_accounts_menu_is_viewport_bounded_and_does_not_stretch_checkboxes():
    page = (ROOT / "frontend/src/pages/Agenda.tsx").read_text(encoding="utf-8")
    home = (ROOT / "frontend/src/pages/PainelClinicalOS.tsx").read_text(encoding="utf-8")
    assistant = (ROOT / "frontend/src/components/PersonalAssistantPanel.tsx").read_text(encoding="utf-8")
    css = (ROOT / "frontend/src/styles/clinical-agenda-final-polish.css").read_text(encoding="utf-8")

    assert "/agenda/work-routines/occurrences" in page
    assert 'calendar_kind?: "appointment" | "commitment" | "work_routine"' in page
    assert 'className="agenda-filtro-contas__menu"' in page
    assert "right:0; left:auto" in css
    assert "max-width:calc(100vw - 2rem)" in css
    assert 'input[type="checkbox"]' in css
    assert "width:16px!important" in css
    assert "position:fixed" in css
    assert "/agenda/locations/home" in page
    assert "Destino após o último compromisso" in page
    assert "/agenda/mobility/commute-return" in home
    assert "/agenda/mobility/commute-target-from-location" in home
    assert "/agenda/mobility/commute-return" in assistant
    assert "/agenda/mobility/commute-target-from-location" in assistant


def test_home_location_is_imported_and_daily_preferences_remain_user_owned(client, criar_usuario, db):
    user, token = criar_usuario(email="agenda.home-route@teste.local")
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    user.home_street = "Rua Teste"
    user.home_number = "123"
    user.home_city = "Ribeirão Preto"
    user.home_state = "SP"
    user.home_zip = "14000-000"
    db.commit()

    imported = client.post("/api/agenda/locations/home", headers=_headers(token), json={})
    assert imported.status_code == 200, imported.text
    home = imported.json()
    assert home["name"] == "Casa"
    assert home["address"]["street"] == "Rua Teste"
    assert home["address"]["number"] == "123"

    preferences = client.get("/api/agenda/mobility/preferences", headers=_headers(token))
    assert preferences.status_code == 200, preferences.text
    assert preferences.json()["day_start_origin_mode"] == "current_location"
    assert preferences.json()["day_start_location_id"] == home["id"]
    assert preferences.json()["day_end_destination_location_id"] == home["id"]

    hotel = CalendarLocation(
        owner_id=user.id, name="Hotel", timezone="America/Sao_Paulo",
        address={"street": "Rua Hotel", "city": "Ribeirão Preto", "state": "SP"},
    )
    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    updated = client.put("/api/agenda/mobility/preferences", headers=_headers(token), json={
        "enabled": True,
        "consent_accepted": True,
        "day_start_origin_mode": "saved_location",
        "day_start_location_id": home["id"],
        "day_end_destination_location_id": hotel.id,
    })
    assert updated.status_code == 200, updated.text
    body = updated.json()
    assert body["day_start_location"]["name"] == "Casa"
    assert body["day_end_destination_location"]["name"] == "Hotel"
    assert db.query(MobilityPreference).filter(MobilityPreference.owner_id == user.id).count() == 1

    other, _ = criar_usuario(email="agenda.other-home@teste.local")
    foreign = CalendarLocation(
        owner_id=other.id, name="Casa alheia", timezone="America/Sao_Paulo",
        address={"street": "Rua Alheia", "city": "Ribeirão Preto", "state": "SP"},
    )
    db.add(foreign)
    db.commit()
    db.refresh(foreign)
    rejected = client.put("/api/agenda/mobility/preferences", headers=_headers(token), json={
        "enabled": True,
        "consent_accepted": True,
        "day_start_origin_mode": "saved_location",
        "day_start_location_id": foreign.id,
        "day_end_destination_location_id": hotel.id,
    })
    assert rejected.status_code == 404
