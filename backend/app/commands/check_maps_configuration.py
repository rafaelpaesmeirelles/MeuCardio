"""Preflight não destrutivo das APIs de mapas usadas pelo CorVIA.

Executado pelo deploy antes de qualquer indisponibilidade. Não consulta banco,
não persiste coordenadas e nunca imprime credenciais. Falhas de autorização,
quota ou billing são bloqueantes; indisponibilidade transitória de rede gera
aviso para não transformar uma oscilação do Google em downtime desnecessário.
"""
from __future__ import annotations

import sys

import httpx

from app.core.config import settings


def _google_geocoding(key: str) -> tuple[bool, str]:
    try:
        response = httpx.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={
                "address": "Ribeirão Preto, SP, Brasil",
                "key": key,
                "language": "pt-BR",
                "region": "br",
            },
            timeout=10,
            follow_redirects=False,
        )
    except httpx.HTTPError as exc:
        return True, f"AVISO: Geocoding API não pôde ser alcançada ({exc.__class__.__name__}); preflight não bloqueou o deploy."
    if not response.is_success:
        return False, f"Geocoding API respondeu HTTP {response.status_code}."
    payload = response.json()
    status = str(payload.get("status") or "").upper()
    if status == "OK":
        return True, "Geocoding API: OK"
    detalhe = str(payload.get("error_message") or "").strip()
    if status in {"REQUEST_DENIED", "OVER_DAILY_LIMIT", "OVER_QUERY_LIMIT"}:
        extra = f" — {detalhe}" if detalhe else ""
        return False, (
            f"Geocoding API: {status}{extra}. Confirme billing e autorize a Geocoding API "
            "nas restrições da GOOGLE_ROUTES_API_KEY."
        )
    return False, f"Geocoding API retornou status inesperado {status or 'vazio'}."


def _google_routes(key: str) -> tuple[bool, str]:
    try:
        response = httpx.post(
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            headers={
                "X-Goog-Api-Key": key,
                "X-Goog-FieldMask": "routes.duration,routes.distanceMeters",
                "Content-Type": "application/json",
            },
            json={
                "origin": {"location": {"latLng": {"latitude": -21.180558, "longitude": -47.8139115}}},
                "destination": {"location": {"latLng": {"latitude": -21.1843, "longitude": -47.8059}}},
                "travelMode": "DRIVE",
            },
            timeout=10,
            follow_redirects=False,
        )
    except httpx.HTTPError as exc:
        return True, f"AVISO: Routes API não pôde ser alcançada ({exc.__class__.__name__}); preflight não bloqueou o deploy."
    if response.is_success:
        payload = response.json()
        if payload.get("routes"):
            return True, "Routes API: OK"
        return False, "Routes API respondeu sem rotas para o trajeto de preflight."
    try:
        payload = response.json()
    except ValueError:
        payload = {}
    erro = payload.get("error") or {}
    status = str(erro.get("status") or response.status_code)
    mensagem = str(erro.get("message") or "").strip()
    extra = f" — {mensagem}" if mensagem else ""
    return False, (
        f"Routes API: {status}{extra}. Confirme billing e autorize a Routes API "
        "nas restrições da GOOGLE_ROUTES_API_KEY."
    )


def main() -> int:
    key = (getattr(settings, "google_routes_api_key", "") or "").strip()
    provider = (getattr(settings, "traffic_provider", "") or "").strip().lower()
    if not key:
        print("Maps preflight: GOOGLE_ROUTES_API_KEY ausente; Google Maps não está configurado. SKIP")
        return 0

    checks = [_google_geocoding(key)]
    if provider in {"", "google", "google_maps"}:
        checks.append(_google_routes(key))

    failed = False
    for ok, message in checks:
        print(message)
        if not ok:
            failed = True
    if failed:
        print("Maps preflight: FAIL", file=sys.stderr)
        return 1
    print("Maps preflight: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
