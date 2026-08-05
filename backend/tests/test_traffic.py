from unittest.mock import Mock

import pytest

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
