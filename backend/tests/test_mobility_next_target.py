from datetime import datetime, timedelta, timezone

from app.api import agenda_mobility_targeted as targeted
from app.models.agenda import CalendarLocation, MobilityPreference


class _User:
    id = 77


class _Query:
    def __init__(self, result):
        self.result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.result


class _DB:
    def __init__(self, *, preference=None, location=None):
        self.preference = preference if preference is not None else object()
        self.location = location
        self.commits = 0

    def query(self, model):
        if model is MobilityPreference:
            return _Query(self.preference)
        if model is CalendarLocation:
            return _Query(self.location)
        return _Query(None)

    def get(self, model, resource_id):
        return None

    def commit(self):
        self.commits += 1


class _PrepareDB:
    """Prova que preparar o mapa do destino não consulta consentimento de GPS."""

    def query(self, model):
        if model is MobilityPreference:
            raise AssertionError("prepare-next-target não deve consultar consentimento de localização atual")
        return _Query(None)

    def get(self, model, resource_id):
        return None

    def commit(self):
        pass


def _manual_occurrence():
    start = datetime.now(timezone.utc) + timedelta(hours=2)
    return {
        "id": "commitment:9:2026-08-15",
        "calendar_kind": "commitment",
        "series_id": 9,
        "title": "Reunião clínica",
        "starts_at": start,
        "ends_at": start + timedelta(hours=1),
        "appointment_type": "reuniao",
        "status": "confirmado",
        "notes": None,
        "location": {
            "id": 31,
            "name": "Hospital A",
            "address": {"city": "Ribeirão Preto", "state": "SP"},
            "latitude": -21.17,
            "longitude": -47.81,
            "default_arrival_buffer_minutes": 15,
            "active": True,
        },
        "visit_mode": "presencial",
        "source": "corvia_manual",
    }


def test_next_target_inclui_commitment_series(monkeypatch):
    monkeypatch.setattr(targeted, "next_locations", lambda **kwargs: [])
    monkeypatch.setattr(targeted, "_commitment_occurrences", lambda *args, **kwargs: [_manual_occurrence()])

    result = targeted.next_target(db=_DB(), user=_User())

    assert result["target_key"] == "commitment:9:2026-08-15"
    assert result["target_type"] == "commitment"
    assert result["source"] == "commitment"
    assert result["title"] == "Reunião clínica"
    assert result["location"]["name"] == "Hospital A"


def test_next_target_appointment_preserva_nome_do_paciente(monkeypatch):
    start = datetime.now(timezone.utc) + timedelta(hours=1)
    target = {
        "routine_id": None,
        "appointment_id": 42,
        "starts_at": start,
        "ends_at": start + timedelta(minutes=30),
        "service_name": "Consulta cardiológica",
        "source": "appointment",
        "arrival_buffer_minutes": 15,
        "location": {
            "id": 31, "name": "Clínica A", "address": {"city": "Ribeirão Preto", "state": "SP"},
            "latitude": -21.17, "longitude": -47.81,
        },
    }
    appointment = type("Appointment", (), {
        "id": 42,
        "owner_id": 77,
        "deleted_at": None,
        "patient_name_temp": "Paciente Teste",
        "patient_id": None,
    })()

    class _AppointmentDB(_DB):
        def get(self, model, resource_id):
            return appointment if resource_id == 42 else None

    monkeypatch.setattr(targeted, "next_locations", lambda **kwargs: [target])
    monkeypatch.setattr(targeted, "_commitment_occurrences", lambda *args, **kwargs: [])

    result = targeted.next_target(db=_AppointmentDB(), user=_User())

    assert result["target_key"] == "appointment:42"
    assert result["title"] == "Paciente Teste"
    assert result["service_name"] == "Consulta cardiológica"


def test_prepare_next_target_geocodifica_destino_sem_pedir_origem_ou_consentimento_gps(monkeypatch):
    target = {
        "target_key": "commitment:9:2026-08-15",
        "target_type": "commitment",
        "source": "commitment",
        "location": {"id": 31, "name": "Hospital A", "latitude": None, "longitude": None},
    }
    calls = []
    monkeypatch.setattr(targeted, "_upcoming_targets", lambda *args, **kwargs: [target])

    def fake_geocode(db, user, item):
        calls.append(item["target_key"])
        return {**item, "location": {**item["location"], "latitude": -21.175, "longitude": -47.810}}

    monkeypatch.setattr(targeted, "_ensure_geocoded", fake_geocode)
    result = targeted.prepare_next_target(db=_PrepareDB(), user=_User())

    assert calls == [target["target_key"]]
    assert result["location"]["latitude"] == -21.175
    assert result["location"]["longitude"] == -47.810


def test_commute_target_mismatch_nao_consulta_provider(monkeypatch):
    chamado = False
    monkeypatch.setattr(targeted, "_find_target", lambda *args, **kwargs: None)

    def nao_deve_chamar(**kwargs):
        nonlocal chamado
        chamado = True
        raise AssertionError("provider não deve ser consultado em mismatch")

    monkeypatch.setattr(targeted, "traffic_eta", nao_deve_chamar)
    result = targeted.commute_target(
        targeted.CommuteTargetIn(latitude=-21.17, longitude=-47.81, target_key="commitment:404:2026-08-15"),
        db=_DB(), user=_User(),
    )

    assert result == {"status": "destination_mismatch", "destination": None, "routes": [], "tips": []}
    assert chamado is False


def test_commute_target_usa_exatamente_destino_selecionado(monkeypatch):
    target = {
        "target_key": "commitment:9:2026-08-15",
        "target_type": "commitment",
        "source": "commitment",
        "arrival_buffer_minutes": 15,
        "location": {"id": 31, "name": "Hospital A", "latitude": -21.20, "longitude": -47.82},
    }
    monkeypatch.setattr(targeted, "_find_target", lambda *args, **kwargs: target)
    monkeypatch.setattr(targeted, "_ensure_geocoded", lambda db, user, item: item)
    calls = []
    audits = []

    def fake_eta(**kwargs):
        calls.append(kwargs)
        return {
            "status": "ok", "provider": "teste", "updated_at": "2026-08-15T12:00:00+00:00",
            "routes": [{"rank": 1, "duration_seconds": 900, "traffic_delay_seconds": 60,
                        "distance_meters": 8000, "congestion": "leve", "summary": "Rota real"}],
            "tips": [],
        }

    monkeypatch.setattr(targeted, "traffic_eta", fake_eta)
    monkeypatch.setattr(targeted, "_audit", lambda db, user, action, resource, resource_id, metadata: audits.append(metadata))
    db = _DB()
    result = targeted.commute_target(
        targeted.CommuteTargetIn(latitude=-21.10, longitude=-47.80, target_key=target["target_key"]),
        db=db, user=_User(),
    )

    assert result["destination"]["target_key"] == target["target_key"]
    assert calls == [{
        "origin_latitude": -21.10,
        "origin_longitude": -47.80,
        "destination_latitude": -21.20,
        "destination_longitude": -47.82,
        "arrival_buffer_minutes": 15,
    }]
    assert audits == [{"provider": "teste", "status": "ok"}]
    assert "latitude" not in audits[0] and "longitude" not in audits[0]
    assert db.commits == 1


def test_geocodifica_destino_existente_sem_inventar_coordenadas(monkeypatch):
    location = type("Location", (), {
        "id": 31, "owner_id": 77, "active": True, "name": "Hospital A",
        "address": {"city": "Ribeirão Preto", "state": "SP"},
        "latitude": None, "longitude": None,
    })()
    db = _DB(location=location)
    audits = []
    monkeypatch.setattr(targeted, "geocode_address", lambda query: {
        "provider": "google_geocoding", "formatted_address": query,
        "latitude": -21.175, "longitude": -47.810,
    })
    monkeypatch.setattr(targeted, "_audit", lambda db, user, action, resource, resource_id, metadata: audits.append(metadata))
    target = {
        "target_key": "commitment:9:2026-08-15",
        "location": {"id": 31, "name": "Hospital A", "address": location.address,
                     "latitude": None, "longitude": None},
    }

    result = targeted._ensure_geocoded(db, _User(), target)

    assert result["location"]["latitude"] == -21.175
    assert result["location"]["longitude"] == -47.810
    assert location.latitude == -21.175 and location.longitude == -47.810
    assert db.commits == 1
    assert audits == [{"provider": "google_geocoding", "status": "ok"}]
