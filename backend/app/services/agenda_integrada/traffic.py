"""ETA com trânsito para o próximo local de trabalho.

As coordenadas de origem são usadas apenas durante a requisição. Este módulo
não persiste, não registra em log e não inclui a localização atual em
AuditLog. Chaves de provedor ficam exclusivamente no servidor.
"""

from __future__ import annotations

from datetime import datetime, timezone
import math
from typing import Any
from urllib.parse import quote

import httpx

from app.core.config import settings
from app.services.agenda_integrada.connectors import ConnectorError


def _coordinates(latitude: float, longitude: float) -> tuple[float, float]:
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise ValueError("Coordenadas inválidas.")
    return latitude, longitude


def _seconds(value: str | int | float | None) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str) and value.endswith("s"):
        try:
            value = float(value[:-1])
        except ValueError:
            return None
    if isinstance(value, (int, float)) and math.isfinite(value) and value >= 0:
        return round(value)
    return None


def _provider_json(response: httpx.Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError:
        raise ConnectorError("traffic_invalid_response", "O provedor de trânsito retornou uma resposta inválida.") from None
    if not isinstance(payload, dict) or not isinstance(payload.get("routes", []), list):
        raise ConnectorError("traffic_invalid_response", "O provedor de trânsito retornou uma resposta inválida.")
    return payload


def _route_metrics(route: dict[str, Any], distance_field: str) -> tuple[int, int]:
    duration = _seconds(route.get("duration"))
    distance = route.get(distance_field)
    if (duration is None or isinstance(distance, bool)
            or not isinstance(distance, (int, float)) or not math.isfinite(distance) or distance < 0):
        raise ConnectorError("traffic_invalid_response", "O provedor não retornou duração e distância válidas para a rota.")
    return duration, round(distance)


def _geometry_available(geometry: dict[str, Any]) -> bool:
    """Validate the provider polyline without synthesizing or persisting a path."""
    if geometry.get("format") != "encoded_polyline" or geometry.get("precision") not in (5, 6):
        return False
    value = geometry.get("value")
    if not isinstance(value, str) or not value:
        return False
    scale = 10 ** geometry["precision"]
    index, latitude, longitude = 0, 0, 0
    first, distinct = None, False
    while index < len(value):
        delta = []
        for _ in range(2):
            number, shift = 0, 0
            while True:
                if index >= len(value) or shift > 30:
                    return False
                byte = ord(value[index]) - 63
                index += 1
                if not 0 <= byte <= 63:
                    return False
                number |= (byte & 31) << shift
                if byte < 32:
                    break
                shift += 5
            delta.append(~(number >> 1) if number & 1 else number >> 1)
        latitude += delta[0]
        longitude += delta[1]
        if not (-90 * scale <= latitude <= 90 * scale and -180 * scale <= longitude <= 180 * scale):
            return False
        point = (latitude, longitude)
        if first is None:
            first = point
        elif point != first:
            distinct = True
    return distinct


def _congestion(delay_seconds: int, typical_seconds: int | None) -> str:
    if not typical_seconds or delay_seconds <= 120:
        return "normal"
    ratio = delay_seconds / typical_seconds
    if ratio >= 0.35:
        return "intenso"
    if ratio >= 0.15:
        return "moderado"
    return "leve"


def _tips(routes: list[dict[str, Any]], buffer_minutes: int) -> list[str]:
    if not routes:
        return []
    best = routes[0]
    tips = [f"Reserve {buffer_minutes} min de margem antes do atendimento."]
    if best.get("traffic_delay_seconds", 0) >= 600:
        tips.append("O trânsito acrescenta pelo menos 10 min; antecipe a saída.")
    if len(routes) > 1 and routes[1]["duration_seconds"] <= best["duration_seconds"] + 300:
        tips.append("Há rota alternativa com tempo semelhante; confira antes de iniciar a navegação.")
    incidents = best.get("incidents") or []
    if incidents:
        tips.append("A rota possui incidente ou interdição reportada pelo provedor.")
    return tips


def _finalize_routes(routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ordena as opções e acrescenta comparadores úteis para a interface.

    O provedor nem sempre devolve a rota padrão como a mais rápida. A ordem que
    chega ao profissional precisa refletir o trânsito atual, mas o índice
    original é preservado para diagnóstico e rastreabilidade.
    """
    routes.sort(key=lambda item: (item["duration_seconds"], item["distance_meters"]))
    if not routes:
        return routes
    fastest = routes[0]["duration_seconds"]
    for index, route in enumerate(routes):
        route["rank"] = index + 1
        route["recommended"] = index == 0
        route["extra_time_seconds"] = max(0, route["duration_seconds"] - fastest)
        route["geometry_available"] = _geometry_available(route.get("geometry") or {})
    return routes


def _google_routes(origin: tuple[float, float], destination: tuple[float, float]) -> dict[str, Any]:
    # Para uma saída imediata, a própria Routes API usa o instante da
    # requisição. Enviar datetime.now() como departureTime é instável: quando
    # o Google valida o payload, o timestamp já pode estar no passado e a API
    # responde INVALID_ARGUMENT.
    body = {
        "origin": {"location": {"latLng": {"latitude": origin[0], "longitude": origin[1]}}},
        "destination": {"location": {"latLng": {"latitude": destination[0], "longitude": destination[1]}}},
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE_OPTIMAL",
        "computeAlternativeRoutes": True,
        "extraComputations": ["TRAFFIC_ON_POLYLINE"],
        "languageCode": "pt-BR",
        "units": "METRIC",
    }
    field_mask = ",".join((
        "routes.duration", "routes.staticDuration", "routes.distanceMeters",
        "routes.description", "routes.routeLabels", "routes.localizedValues",
        "routes.polyline.encodedPolyline",
        "routes.travelAdvisory.speedReadingIntervals",
    ))
    response = httpx.post(
        "https://routes.googleapis.com/directions/v2:computeRoutes",
        headers={
            "X-Goog-Api-Key": settings.google_routes_api_key,
            "X-Goog-FieldMask": field_mask,
            "Content-Type": "application/json",
        },
        json=body,
        timeout=15,
        follow_redirects=False,
    )
    if not response.is_success:
        raise ConnectorError("traffic_provider_error", f"Google Routes HTTP {response.status_code}.", retryable=response.status_code >= 500 or response.status_code in (408, 429))
    parsed = _provider_json(response)
    routes: list[dict[str, Any]] = []
    for index, route in enumerate(parsed.get("routes", [])[:3]):
        duration, distance = _route_metrics(route, "distanceMeters")
        typical = _seconds(route.get("staticDuration"))
        delay = max(0, duration - (typical or duration))
        advisory = route.get("travelAdvisory") or {}
        intervals = advisory.get("speedReadingIntervals") or []
        polyline = route.get("polyline")
        routes.append({
            "provider_rank": index + 1,
            "duration_seconds": duration,
            "typical_duration_seconds": typical,
            "traffic_delay_seconds": delay,
            "distance_meters": distance,
            "congestion": _congestion(delay, typical),
            "summary": route.get("description") or ("Rota principal" if index == 0 else f"Alternativa {index}"),
            "labels": route.get("routeLabels") or [],
            "geometry": {
                "format": "encoded_polyline",
                "value": (polyline.get("encodedPolyline") or "") if isinstance(polyline, dict) else "",
                "precision": 5,
            },
            "traffic_segments": [
                {
                    "start_index": interval.get("startPolylinePointIndex", 0),
                    "end_index": interval.get("endPolylinePointIndex"),
                    "speed": str(interval.get("speed") or "NORMAL").lower(),
                }
                for interval in intervals
            ],
            "incidents": [],
        })
    return {"provider": "Google Maps", "routes": _finalize_routes(routes)}


def _mapbox_routes(origin: tuple[float, float], destination: tuple[float, float]) -> dict[str, Any]:
    coordinates = f"{origin[1]},{origin[0]};{destination[1]},{destination[0]}"
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving-traffic/{quote(coordinates, safe=',;.')}"
    response = httpx.get(
        url,
        params={
            "access_token": settings.mapbox_access_token,
            "alternatives": "true",
            "overview": "full",
            "geometries": "polyline6",
            "steps": "false",
            "annotations": "congestion,closure",
            "depart_at": "now",
            "language": "pt-BR",
        },
        timeout=15,
        follow_redirects=False,
    )
    if not response.is_success:
        raise ConnectorError("traffic_provider_error", f"Mapbox HTTP {response.status_code}.", retryable=response.status_code >= 500 or response.status_code in (408, 429))
    parsed = _provider_json(response)
    if parsed.get("code") == "NoRoute":
        return {"provider": "Mapbox", "routes": []}
    if parsed.get("code") != "Ok":
        raise ConnectorError("traffic_provider_error", "O Mapbox não conseguiu calcular a rota solicitada.")
    routes: list[dict[str, Any]] = []
    for index, route in enumerate(parsed.get("routes", [])[:3]):
        duration, distance = _route_metrics(route, "distance")
        legs = route.get("legs") or []
        typical_values = [leg.get("duration_typical") for leg in legs if leg.get("duration_typical") is not None]
        typical = _seconds(sum(typical_values)) if typical_values else None
        delay = max(0, duration - (typical or duration))
        incidents = [
            {"type": incident.get("type"), "description": incident.get("description")}
            for leg in legs for incident in (leg.get("incidents") or [])[:5]
        ]
        routes.append({
            "provider_rank": index + 1,
            "duration_seconds": duration,
            "typical_duration_seconds": typical,
            "traffic_delay_seconds": delay,
            "distance_meters": distance,
            "congestion": _congestion(delay, typical),
            "summary": ", ".join(filter(None, (leg.get("summary") for leg in legs))) or f"Rota {index + 1}",
            "labels": [],
            "geometry": {
                "format": "encoded_polyline",
                "value": route.get("geometry") or "",
                "precision": 6,
            },
            "traffic_segments": [],
            "incidents": incidents,
        })
    return {"provider": "Mapbox", "routes": _finalize_routes(routes)}


def traffic_eta(
    *,
    origin_latitude: float,
    origin_longitude: float,
    destination_latitude: float,
    destination_longitude: float,
    arrival_buffer_minutes: int = 15,
) -> dict[str, Any]:
    origin = _coordinates(origin_latitude, origin_longitude)
    destination = _coordinates(destination_latitude, destination_longitude)
    if not settings.traffic_configured:
        return {
            "status": "not_configured",
            "provider": settings.traffic_provider,
            "updated_at": None,
            "routes": [],
            "tips": [],
        }
    try:
        if settings.traffic_provider == "google_routes":
            result = _google_routes(origin, destination)
        elif settings.traffic_provider == "mapbox":
            result = _mapbox_routes(origin, destination)
        else:
            raise ConnectorError("unsupported_traffic_provider", "Provedor de trânsito inválido.", status_code=409)
    except httpx.HTTPError:
        # HTTP exception text can contain the requested URL and coordinates.
        raise ConnectorError("traffic_provider_unavailable", "O provedor de trânsito está temporariamente indisponível.", retryable=True, status_code=503) from None
    except (ValueError, TypeError, AttributeError, OverflowError):
        raise ConnectorError("traffic_invalid_response", "O provedor de trânsito retornou uma resposta inválida.") from None
    result.update({
        "status": ("no_route" if not result["routes"] else "live"
                   if any(route["geometry_available"] for route in result["routes"]) else "geometry_unavailable"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "tips": _tips(result["routes"], arrival_buffer_minutes),
    })
    return result
