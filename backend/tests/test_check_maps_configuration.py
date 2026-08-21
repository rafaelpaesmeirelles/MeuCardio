from __future__ import annotations

from types import SimpleNamespace

from app.commands import check_maps_configuration as command


class Response:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.is_success = 200 <= status_code < 300

    def json(self):
        return self._payload


def test_google_geocoding_request_denied_is_actionable(monkeypatch):
    monkeypatch.setattr(
        command.httpx,
        "get",
        lambda *args, **kwargs: Response(
            payload={
                "status": "REQUEST_DENIED",
                "error_message": "API key is not authorized to use this service.",
            }
        ),
    )
    ok, message = command._google_geocoding("secret")
    assert ok is False
    assert "REQUEST_DENIED" in message
    assert "Geocoding API" in message
    assert "GOOGLE_ROUTES_API_KEY" in message
    assert "secret" not in message


def test_google_geocoding_ok(monkeypatch):
    monkeypatch.setattr(
        command.httpx,
        "get",
        lambda *args, **kwargs: Response(payload={"status": "OK", "results": [{"geometry": {}}]}),
    )
    assert command._google_geocoding("secret") == (True, "Geocoding API: OK")


def test_main_passes_google_geocoding_and_routes(monkeypatch, capsys):
    monkeypatch.setattr(command, "settings", SimpleNamespace(google_routes_api_key="secret", traffic_provider="google"))
    monkeypatch.setattr(command, "_google_geocoding", lambda key: (True, "Geocoding API: OK"))
    monkeypatch.setattr(command, "_google_routes", lambda key: (True, "Routes API: OK"))
    assert command.main() == 0
    output = capsys.readouterr().out
    assert "Maps preflight: PASS" in output


def test_main_fails_on_authorization_problem(monkeypatch, capsys):
    monkeypatch.setattr(command, "settings", SimpleNamespace(google_routes_api_key="secret", traffic_provider="google"))
    monkeypatch.setattr(command, "_google_geocoding", lambda key: (False, "Geocoding API: REQUEST_DENIED"))
    monkeypatch.setattr(command, "_google_routes", lambda key: (True, "Routes API: OK"))
    assert command.main() == 1
    captured = capsys.readouterr()
    assert "REQUEST_DENIED" in captured.out
    assert "Maps preflight: FAIL" in captured.err
