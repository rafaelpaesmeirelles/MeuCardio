"""ETA com trânsito para o próximo local de trabalho.

As coordenadas de origem são usadas apenas durante a requisição. Este módulo
não persiste, não registra em log e não inclui a localização atual em
AuditLog. Chaves de provedor ficam exclusivamente no servidor.
"""

from __future__ import annotations

from datetime import datetime, timezone
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
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return max(0, round(value))
    if isinstance(value, str) and value.endswith("s"):
        try:
            return max(0, round(float(value[:-1])))
        except ValueError:
            return None
    return None


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
        "languageCode": "pt-BR",
        "units": "METRIC",
    }
    field_mask = ",".join((
        "routes.duration", "routes.staticDuration", "routes.distanceMeters",
        "routes.description", "routes.routeLabels", "routes.localizedValues",
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
        raise ConnectorError("traffic_provider_error", f"Google Routes HTTP {response.status_code}.", retryable=response.status_code >= 500)
    parsed = response.json()
    routes: list[dict[str, Any]] = []
    for index, route in enumerate(parsed.get("routes", [])[:3]):
        duration = _seconds(route.get("duration")) or 0
        typical = _seconds(route.get("staticDuration"))
        delay = max(0, duration - (typical or duration))
        routes.append({
            "rank": index + 1,
            "duration_seconds": duration,
            "typical_duration_seconds": typical,
            "traffic_delay_seconds": delay,
            "distance_meters": route.get("distanceMeters"),
            "congestion": _congestion(delay, typical),
            "summary": route.get("description") or ("Rota principal" if index == 0 else f"Alternativa {index}"),
            "incidents": [],
        })
    routes.sort(key=lambda item: item["duration_seconds"])
    return {"provider": "Google Routes", "routes": routes}


def _mapbox_routes(origin: tuple[float, float], destination: tuple[float, float]) -> dict[str, Any]:
    coordinates = f"{origin[1]},{origin[0]};{destination[1]},{destination[0]}"
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving-traffic/{quote(coordinates, safe=',;.')}"
    response = httpx.get(
        url,
        params={
            "access_token": settings.mapbox_access_token,
            "alternatives": "true",
            "overview": "full",
            "steps": "false",
            "annotations": "congestion,closure",
            "depart_at": "now",
            "language": "pt-BR",
        },
        timeout=15,
        follow_redirects=False,
    )
    if not response.is_success:
        raise ConnectorError("traffic_provider_error", f"Mapbox HTTP {response.status_code}.", retryable=response.status_code >= 500)
    parsed = response.json()
    if parsed.get("code") != "Ok":
        raise ConnectorError("traffic_provider_error", str(parsed.get("message") or parsed.get("code"))[:300])
    routes: list[dict[str, Any]] = []
    for index, route in enumerate(parsed.get("routes", [])[:3]):
        duration = _seconds(route.get("duration")) or 0
        legs = route.get("legs") or []
        typical_values = [leg.get("duration_typical") for leg in legs if leg.get("duration_typical") is not None]
        typical = _seconds(sum(typical_values)) if typical_values else None
        delay = max(0, duration - (typical or duration))
        incidents = [
            {"type": incident.get("type"), "description": incident.get("description")}
            for leg in legs for incident in (leg.get("incidents") or [])[:5]
        ]
        routes.append({
            "rank": index + 1,
            "duration_seconds": duration,
            "typical_duration_seconds": typical,
            "traffic_delay_seconds": delay,
            "distance_meters": round(route.get("distance") or 0),
            "congestion": _congestion(delay, typical),
            "summary": ", ".join(filter(None, (leg.get("summary") for leg in legs))) or f"Rota {index + 1}",
            "incidents": incidents,
        })
    routes.sort(key=lambda item: item["duration_seconds"])
    return {"provider": "Mapbox", "routes": routes}


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
    if settings.traffic_provider == "google_routes":
        result = _google_routes(origin, destination)
    elif settings.traffic_provider == "mapbox":
        result = _mapbox_routes(origin, destination)
    else:
        raise ConnectorError("unsupported_traffic_provider", "Provedor de trânsito inválido.", status_code=409)
    result.update({
        "status": "live",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "tips": _tips(result["routes"], arrival_buffer_minutes),
    })
    return result
