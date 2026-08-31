"""Auditoria AUTH/SESSION → AGENDA (issue #52, subfase 4): escrita
bidirecional no calendário externo — `reschedule`/`cancel` dos conectores
Google/Microsoft (`app/services/agenda_integrada/connectors.py`).

Gap encontrado na auditoria: só `.create()` tinha teste (dedup por
idempotency key, id determinístico) — `.reschedule()`/`.cancel()`, que são
o caminho de "atualização/deleção" pedido pela subfase, e o mapeamento de
409/412 do provedor para `external_conflict` (a detecção de conflito de
edição concorrente via `If-Match`/`version`), nunca tinham sido exercitados.
Toda chamada é via `httpx.MockTransport` — nenhuma rede real, mesmo padrão
já usado em `test_agenda_connectors.py`.
"""
import httpx
import pytest

from app.services.agenda_integrada.connectors import (
    ConnectorError,
    GoogleCalendarConnector,
    Microsoft365CalendarConnector,
)

PAYLOAD_BASE = {
    "starts_at": "2026-08-20T14:00:00-03:00",
    "ends_at": "2026-08-20T14:30:00-03:00",
    "service_name": "Consulta de retorno",
    "notes": "Trazer exames anteriores.",
    "location_name": "Consultório 2",
    "appointment_id": 42,
    "patient_name": "Paciente Sigiloso",
}


def _google(handler, configuration=None):
    return GoogleCalendarConnector(
        {"access_token": "token"}, configuration or {"calendar_id": "primary"},
        transport=httpx.MockTransport(handler),
    )


def _microsoft(handler, configuration=None):
    return Microsoft365CalendarConnector(
        {"access_token": "token"}, configuration or {},
        transport=httpx.MockTransport(handler),
    )


# --- timezone -------------------------------------------------------------


def test_google_reschedule_uses_payload_timezone_when_provided():
    capturado = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json
        capturado["body"] = json.loads(request.content)
        return httpx.Response(200, json={"id": "evt-1", "status": "confirmed"})

    conector = _google(handler)
    conector.reschedule("evt-1", {**PAYLOAD_BASE, "timezone": "America/Manaus"}, version=None)
    assert capturado["body"]["start"]["timeZone"] == "America/Manaus"
    assert capturado["body"]["end"]["timeZone"] == "America/Manaus"


def test_google_reschedule_defaults_timezone_to_sao_paulo_when_absent():
    capturado = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json
        capturado["body"] = json.loads(request.content)
        return httpx.Response(200, json={"id": "evt-1"})

    conector = _google(handler)
    conector.reschedule("evt-1", PAYLOAD_BASE, version=None)
    assert capturado["body"]["start"]["timeZone"] == "America/Sao_Paulo"


# --- concurrência / conflito (If-Match / version) --------------------------


def test_google_reschedule_sends_if_match_when_version_known():
    capturado = {}

    def handler(request: httpx.Request) -> httpx.Response:
        capturado["if_match"] = request.headers.get("if-match")
        return httpx.Response(200, json={"id": "evt-1"})

    conector = _google(handler)
    conector.reschedule("evt-1", PAYLOAD_BASE, version='"etag-123"')
    assert capturado["if_match"] == '"etag-123"'


def test_google_reschedule_without_version_omits_if_match():
    capturado = {}

    def handler(request: httpx.Request) -> httpx.Response:
        capturado["if_match"] = request.headers.get("if-match")
        return httpx.Response(200, json={"id": "evt-1"})

    conector = _google(handler)
    conector.reschedule("evt-1", PAYLOAD_BASE, version=None)
    assert capturado["if_match"] is None


@pytest.mark.parametrize(
    "provider_status,esperado_retryable",
    [
        # 409 é conflito genérico (ex.: escrita concorrente no mesmo
        # instante) — pode resolver sozinho numa nova tentativa idêntica.
        # 412 é falha de pré-condição do If-Match — a versão que o médico
        # tinha ficou desatualizada, repetir o MESMO pedido falharia de
        # novo para sempre; quem chama precisa reler o evento antes de
        # tentar de novo, não apenas repetir. Os dois mapeiam para o mesmo
        # código (`external_conflict`), mas com `retryable` diferente —
        # confirmado aqui de propósito, não é bug do código.
        (409, True),
        (412, False),
    ],
)
def test_google_reschedule_conflict_maps_to_external_conflict(provider_status, esperado_retryable):
    """O provedor recusa a edição porque o evento mudou desde a última
    leitura do médico (outra aba, outro dispositivo, ou o próprio paciente
    reagendando pelo Google Agenda) — precisa virar um erro que a UI
    reconhece como conflito, não um 502 genérico."""
    conector = _google(lambda request: httpx.Response(provider_status, json={"error": {"message": "conflict"}}))
    with pytest.raises(ConnectorError) as exc:
        conector.reschedule("evt-1", PAYLOAD_BASE, version='"etag-velho"')
    assert exc.value.code == "external_conflict"
    assert exc.value.retryable is esperado_retryable


def test_microsoft_reschedule_sends_if_match_when_version_known():
    capturado = {}

    def handler(request: httpx.Request) -> httpx.Response:
        capturado["if_match"] = request.headers.get("if-match")
        return httpx.Response(200, json={"id": "evt-1"})

    conector = _microsoft(handler)
    conector.reschedule("evt-1", PAYLOAD_BASE, version='W/"changekey-1"')
    assert capturado["if_match"] == 'W/"changekey-1"'


@pytest.mark.parametrize("provider_status,esperado_retryable", [(409, True), (412, False)])
def test_microsoft_reschedule_conflict_maps_to_external_conflict(provider_status, esperado_retryable):
    conector = _microsoft(lambda request: httpx.Response(provider_status, json={"error": {"message": "conflict"}}))
    with pytest.raises(ConnectorError) as exc:
        conector.reschedule("evt-1", PAYLOAD_BASE, version='W/"changekey-velho"')
    assert exc.value.code == "external_conflict"
    assert exc.value.retryable is esperado_retryable


def test_microsoft_cancel_sends_if_match_when_version_known():
    capturado = {}

    def handler(request: httpx.Request) -> httpx.Response:
        capturado["if_match"] = request.headers.get("if-match")
        return httpx.Response(200, json={})

    conector = _microsoft(handler)
    conector.cancel("evt-1", reason="Paciente desmarcou", version='W/"changekey-1"')
    assert capturado["if_match"] == 'W/"changekey-1"'


# --- deleção -------------------------------------------------------------


def test_google_cancel_deletes_and_reports_cancelled():
    chamadas = []

    def handler(request: httpx.Request) -> httpx.Response:
        chamadas.append(request.method)
        return httpx.Response(204)

    conector = _google(handler)
    resultado = conector.cancel("evt-1", reason="Paciente desmarcou", version=None)
    assert chamadas == ["DELETE"]
    assert resultado == {"id": "evt-1", "status": "cancelled"}


def test_microsoft_cancel_uses_cancel_endpoint_not_delete():
    """A Graph API usa POST /events/{id}/cancel, não DELETE — mandar DELETE
    apagaria o evento sem notificar convidados; cancel é o caminho correto
    para reunião/consulta com participante externo."""
    capturado = {}

    def handler(request: httpx.Request) -> httpx.Response:
        capturado["method"] = request.method
        capturado["url"] = str(request.url)
        import json
        capturado["body"] = json.loads(request.content)
        return httpx.Response(202)

    conector = _microsoft(handler)
    conector.cancel("evt-1", reason="Paciente desmarcou", version=None)
    assert capturado["method"] == "POST"
    assert capturado["url"].endswith("/events/evt-1/cancel")
    assert capturado["body"]["comment"] == "Paciente desmarcou"


def test_microsoft_cancel_defaults_reason_when_absent():
    capturado = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json
        capturado["body"] = json.loads(request.content)
        return httpx.Response(202)

    conector = _microsoft(handler)
    conector.cancel("evt-1", reason=None, version=None)
    assert capturado["body"]["comment"] == "Cancelado no CorVIA"


# --- erros --------------------------------------------------------------


def test_google_reschedule_event_not_found_is_external_not_found():
    conector = _google(lambda request: httpx.Response(404, json={"error": {"message": "not found"}}))
    with pytest.raises(ConnectorError) as exc:
        conector.reschedule("evt-inexistente", PAYLOAD_BASE, version=None)
    assert exc.value.code == "external_not_found"


def test_microsoft_reschedule_revoked_token_is_reauth_required():
    conector = _microsoft(lambda request: httpx.Response(401, json={"error": {"message": "unauthorized"}}))
    with pytest.raises(ConnectorError) as exc:
        conector.reschedule("evt-1", PAYLOAD_BASE, version=None)
    assert exc.value.code == "reauth_required"


# --- privacidade do nome do paciente, também na atualização ---------------


def test_google_reschedule_omits_patient_name_when_not_exposed():
    """A privacidade do nome do paciente já era garantida no `create` — este
    teste garante que a mesma regra vale no `reschedule`, que usa o mesmo
    `_event_body` e por isso herda a proteção, mas nunca tinha sido
    verificado diretamente."""
    capturado = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json
        capturado["body"] = json.loads(request.content)
        return httpx.Response(200, json={"id": "evt-1"})

    conector = _google(handler, configuration={"calendar_id": "primary", "expose_patient_name": False})
    conector.reschedule("evt-1", PAYLOAD_BASE, version=None)
    assert "Paciente Sigiloso" not in capturado["body"]["summary"]


def test_google_reschedule_includes_patient_name_when_explicitly_exposed():
    capturado = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json
        capturado["body"] = json.loads(request.content)
        return httpx.Response(200, json={"id": "evt-1"})

    conector = _google(handler, configuration={"calendar_id": "primary", "expose_patient_name": True})
    conector.reschedule("evt-1", PAYLOAD_BASE, version=None)
    assert "Paciente Sigiloso" in capturado["body"]["summary"]
