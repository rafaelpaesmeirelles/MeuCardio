from unittest.mock import Mock

import pytest
import httpx

from app.services.agenda_integrada import traffic
from app.api.agenda_integrada import get_map_config


@pytest.fixture(autouse=True)
def _banco_limpo():
    """Este módulo testa apenas o adaptador HTTP e não depende do PostgreSQL."""
    yield


def _response(payload: dict) -> Mock:
    response = Mock()
    response.is_success = True
    response.json.return_value = payload
    return response


def test_google_routes_returns_geometry_traffic_and_ranked_alternatives(monkeypatch):
    monkeypatch.setattr(traffic.settings, "google_routes_api_key", "test-key")
    mocked_post = Mock(return_value=_response({
        "routes": [
            {
                "duration": "900s",
                "staticDuration": "600s",
                "distanceMeters": 10500,
                "description": "Av. principal",
                "routeLabels": ["DEFAULT_ROUTE"],
                "polyline": {"encodedPolyline": "_p~iF~ps|U_ulLnnqC"},
                "travelAdvisory": {"speedReadingIntervals": [
                    {"startPolylinePointIndex": 0, "endPolylinePointIndex": 2, "speed": "SLOW"},
                ]},
            },
            {
                "duration": "780s",
                "staticDuration": "720s",
                "distanceMeters": 12100,
                "description": "Via marginal",
                "routeLabels": ["DEFAULT_ROUTE_ALTERNATE"],
                "polyline": {"encodedPolyline": "a~l~Fjk~uOwHJy@P"},
            },
        ],
    }))
    monkeypatch.setattr(traffic.httpx, "post", mocked_post)

    result = traffic._google_routes((-23.5, -46.6), (-23.6, -46.7))

    assert [route["summary"] for route in result["routes"]] == ["Via marginal", "Av. principal"]
    assert result["routes"][0]["recommended"] is True
    assert result["routes"][1]["extra_time_seconds"] == 120
    assert result["routes"][1]["geometry"]["value"] == "_p~iF~ps|U_ulLnnqC"
    assert result["routes"][1]["traffic_segments"][0]["speed"] == "slow"
    assert "routes.polyline.encodedPolyline" in mocked_post.call_args.kwargs["headers"]["X-Goog-FieldMask"]
    assert "routes.travelAdvisory.speedReadingIntervals" in mocked_post.call_args.kwargs["headers"]["X-Goog-FieldMask"]
    assert mocked_post.call_args.kwargs["json"]["extraComputations"] == ["TRAFFIC_ON_POLYLINE"]


def test_mapbox_requests_full_geometry_for_every_alternative(monkeypatch):
    monkeypatch.setattr(traffic.settings, "mapbox_access_token", "test-token")
    mocked_get = Mock(return_value=_response({
        "code": "Ok",
        "routes": [{
            "duration": 600,
            "distance": 8300,
            "geometry": "abc123",
            "legs": [{"duration_typical": 500, "summary": "Centro"}],
        }],
    }))
    monkeypatch.setattr(traffic.httpx, "get", mocked_get)

    result = traffic._mapbox_routes((-23.5, -46.6), (-23.6, -46.7))

    assert result["routes"][0]["geometry"] == {
        "format": "encoded_polyline", "value": "abc123", "precision": 6,
    }
    assert mocked_get.call_args.kwargs["params"]["geometries"] == "polyline6"


def test_map_config_exposes_only_the_domain_restricted_browser_key(monkeypatch):
    monkeypatch.setattr(traffic.settings, "traffic_provider", "google_routes")
    monkeypatch.setattr(traffic.settings, "google_routes_api_key", "private-server-key")
    monkeypatch.setattr(traffic.settings, "google_maps_browser_api_key", "public-referrer-key")

    result = get_map_config(user=Mock())

    assert result == {
        "provider": "google_maps",
        "configured": True,
        "api_key": "public-referrer-key",
    }
    assert "private-server-key" not in str(result)


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
    assert result["provider"] == "Google Maps"
    route = result["routes"][0]
    assert route["rank"] == 1
    assert route["recommended"] is True
    assert route["duration_seconds"] == 900
    assert route["typical_duration_seconds"] == 780
    assert route["traffic_delay_seconds"] == 120
    assert route["distance_meters"] == 5500
    assert route["congestion"] == "normal"
    assert route["summary"] == "Rota de teste"


def _eta(monkeypatch, provider="google_routes"):
    monkeypatch.setattr(traffic.settings, "traffic_provider", provider)
    monkeypatch.setattr(traffic.settings, "google_routes_api_key", "fixture-server-key")
    monkeypatch.setattr(traffic.settings, "mapbox_access_token", "fixture-server-token")
    return traffic.traffic_eta(origin_latitude=1, origin_longitude=2,
        destination_latitude=3, destination_longitude=4)


@pytest.mark.parametrize("provider,payload", [
    ("google_routes", {}), ("google_routes", {"routes": []}),
    ("mapbox", {"code": "Ok", "routes": []}), ("mapbox", {"code": "NoRoute"}),
])
def test_provider_without_routes_is_not_reported_as_live(monkeypatch, provider, payload):
    monkeypatch.setattr(traffic.httpx, "post" if provider == "google_routes" else "get", Mock(return_value=_response(payload)))
    result = _eta(monkeypatch, provider)
    assert result["status"] == "no_route" and result["routes"] == [] and result["tips"] == []


@pytest.mark.parametrize("polyline", [None, {}, {"encodedPolyline": ""}, {"encodedPolyline": "abc123"}])
def test_real_eta_is_preserved_when_provider_geometry_is_unavailable(monkeypatch, polyline):
    monkeypatch.setattr(traffic.httpx, "post", Mock(return_value=_response({"routes": [{
        "duration": "900s", "staticDuration": "780s", "distanceMeters": 5500, "polyline": polyline,
    }]})))
    result = _eta(monkeypatch)
    assert result["status"] == "geometry_unavailable"
    assert len(result["routes"]) == 1
    route = result["routes"][0]
    assert (route["duration_seconds"], route["distance_meters"], route["traffic_delay_seconds"]) == (900, 5500, 120)
    assert route["geometry_available"] is False


def test_mixed_route_geometry_preserves_metrics_order_and_flags_each_item(monkeypatch):
    monkeypatch.setattr(traffic.httpx, "post", Mock(return_value=_response({"routes": [
        {"duration": "900s", "distanceMeters": 5500, "polyline": {"encodedPolyline": "_p~iF~ps|U_ulLnnqC"}},
        {"duration": "600s", "distanceMeters": 6000},
    ]})))
    result = _eta(monkeypatch)
    assert result["status"] == "live"
    assert [route["duration_seconds"] for route in result["routes"]] == [600, 900]
    assert [route["geometry_available"] for route in result["routes"]] == [False, True]
    assert result["routes"][0]["recommended"] is True
    assert result["routes"][1]["geometry"]["value"] == "_p~iF~ps|U_ulLnnqC"


@pytest.mark.parametrize("provider", ["google_routes", "mapbox"])
@pytest.mark.parametrize("error_type", [httpx.ReadTimeout, httpx.ConnectError])
def test_transport_errors_are_retryable_without_echoing_request_details(monkeypatch, provider, error_type):
    monkeypatch.setattr(traffic.httpx, "post" if provider == "google_routes" else "get",
        Mock(side_effect=error_type("fixture-private-key and synthetic-coordinate must not escape")))
    with pytest.raises(traffic.ConnectorError) as exc:
        _eta(monkeypatch, provider)
    assert exc.value.code == "traffic_provider_unavailable" and exc.value.status_code == 503
    assert exc.value.retryable is True and exc.value.__cause__ is None
    assert "fixture-private" not in str(exc.value) and "synthetic-coordinate" not in str(exc.value)


@pytest.mark.parametrize("provider", ["google_routes", "mapbox"])
def test_invalid_provider_json_is_a_controlled_error(monkeypatch, provider):
    response = _response({})
    response.json.side_effect = ValueError("fixture-private-response")
    monkeypatch.setattr(traffic.httpx, "post" if provider == "google_routes" else "get", Mock(return_value=response))
    with pytest.raises(traffic.ConnectorError) as exc:
        _eta(monkeypatch, provider)
    assert exc.value.code == "traffic_invalid_response" and exc.value.status_code == 502
    assert "fixture-private" not in str(exc.value)


@pytest.mark.parametrize("route", [
    {"distanceMeters": 100}, {"duration": "30s"}, {"duration": "NaNs", "distanceMeters": 100},
    {"duration": "-5s", "distanceMeters": 100}, {"duration": "30s", "distanceMeters": float("inf")},
])
def test_missing_or_invalid_metrics_are_not_fabricated_as_zero(monkeypatch, route):
    monkeypatch.setattr(traffic.httpx, "post", Mock(return_value=_response({"routes": [route]})))
    with pytest.raises(traffic.ConnectorError) as exc:
        _eta(monkeypatch)
    assert exc.value.code == "traffic_invalid_response"


@pytest.mark.parametrize("value,precision,available", [
    ("_p~iF~ps|U_ulLnnqC", 5, True), ("_izlhA~rlgdF_{geC~ywl@", 6, True),
    ("??AA", 5, True), ("??", 5, False), ("????", 5, False),
    ("_p~iF~ps|U_ulLnnq", 5, False), ("~~~~~~~", 5, False), ("\x00", 5, False),
    ("??AA", 4, False),
])
def test_only_complete_geographical_provider_polylines_are_usable(value, precision, available):
    assert traffic._geometry_available({"format": "encoded_polyline", "value": value, "precision": precision}) is available


def test_unconfigured_provider_never_calls_network(monkeypatch):
    monkeypatch.setattr(traffic.settings, "traffic_provider", "google_routes")
    monkeypatch.setattr(traffic.settings, "google_routes_api_key", "")
    post = Mock(side_effect=AssertionError("network must not be called"))
    monkeypatch.setattr(traffic.httpx, "post", post)
    result = traffic.traffic_eta(origin_latitude=1, origin_longitude=2, destination_latitude=3, destination_longitude=4)
    assert result["status"] == "not_configured" and result["routes"] == []
    post.assert_not_called()
