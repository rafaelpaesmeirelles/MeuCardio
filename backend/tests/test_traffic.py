from app.services.agenda_integrada import traffic


class _GoogleRoutesResponse:
    is_success = True
    status_code = 200

    @staticmethod
    def json() -> dict:
        return {
            "routes": [{
                "duration": "900s",
                "staticDuration": "780s",
                "distanceMeters": 5500,
                "description": "Rota de teste",
            }]
        }


def test_google_routes_uses_implicit_departure_time_for_live_traffic(monkeypatch):
    captured: dict = {}

    def fake_post(url, *, headers, json, timeout, follow_redirects):
        captured.update({"url": url, "headers": headers, "body": json})
        return _GoogleRoutesResponse()

    monkeypatch.setattr(traffic.settings, "google_routes_api_key", "test-key")
    monkeypatch.setattr(traffic.httpx, "post", fake_post)

    result = traffic._google_routes((-23.5614, -46.6565), (-23.5874, -46.6576))

    assert captured["url"].endswith("/directions/v2:computeRoutes")
    assert captured["headers"]["X-Goog-Api-Key"] == "test-key"
    assert captured["body"]["routingPreference"] == "TRAFFIC_AWARE_OPTIMAL"
    assert "departureTime" not in captured["body"]
    assert result["provider"] == "Google Routes"
    assert result["routes"][0] == {
        "rank": 1,
        "duration_seconds": 900,
        "typical_duration_seconds": 780,
        "traffic_delay_seconds": 120,
        "distance_meters": 5500,
        "congestion": "normal",
        "summary": "Rota de teste",
        "incidents": [],
    }
