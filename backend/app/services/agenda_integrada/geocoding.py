"""Geocodificação server-side para locais da Agenda Integrada.

Objetivo: transformar um endereço informado em conversa/tela em coordenadas
persistíveis de ``CalendarLocation`` para que a camada de deslocamento consiga
calcular rota depois sem exigir que o médico descubra/cole latitude e longitude.

Fail-closed: nenhum endereço ou coordenada é inventado. Se o provedor não
estiver configurado, recusar, ficar indisponível ou não devolver resultado, a
função levanta ``GeocodingError`` e o chamador decide se cria o local apenas
com o endereço textual.

Não há logging do endereço consultado. Chaves permanecem exclusivamente no
servidor. Google usa a Geocoding API v3 (endpoint HTTPS documentado e estável,
com API key); Mapbox usa Geocoding v6 com ``permanent=true`` porque o resultado
será armazenado em ``CalendarLocation``.
"""
from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings


class GeocodingError(RuntimeError):
    pass


def _texto_endereco(valor: str) -> str:
    texto = " ".join((valor or "").strip().split())
    if len(texto) < 5:
        raise GeocodingError("Informe um endereço mais completo para localizar no mapa.")
    if len(texto) > 256:
        raise GeocodingError("O endereço informado é longo demais para geocodificação.")
    return texto


def _google(address: str) -> dict[str, Any]:
    chave = (getattr(settings, "google_routes_api_key", "") or "").strip()
    if not chave:
        raise GeocodingError("Google Maps não está configurado para geocodificação.")
    try:
        response = httpx.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={
                "address": address,
                "key": chave,
                "language": "pt-BR",
                "region": "br",
            },
            timeout=12,
            follow_redirects=False,
        )
    except httpx.HTTPError as exc:
        raise GeocodingError("O serviço de geocodificação do Google está indisponível.") from exc
    if not response.is_success:
        raise GeocodingError(f"Google Geocoding respondeu HTTP {response.status_code}.")
    payload = response.json()
    status = str(payload.get("status") or "").upper()
    if status != "OK":
        if status == "ZERO_RESULTS":
            raise GeocodingError("O endereço não foi localizado pelo Google Maps.")
        raise GeocodingError("O Google Maps não conseguiu geocodificar este endereço.")
    resultados = payload.get("results") or []
    if not resultados:
        raise GeocodingError("O endereço não foi localizado pelo Google Maps.")
    primeiro = resultados[0]
    localizacao = (primeiro.get("geometry") or {}).get("location") or {}
    lat = localizacao.get("lat")
    lng = localizacao.get("lng")
    if lat is None or lng is None:
        raise GeocodingError("O Google Maps não devolveu coordenadas para este endereço.")
    return {
        "provider": "google_geocoding",
        "formatted_address": str(primeiro.get("formatted_address") or address),
        "latitude": float(lat),
        "longitude": float(lng),
        "place_id": primeiro.get("place_id"),
    }


def _mapbox(address: str) -> dict[str, Any]:
    token = (getattr(settings, "mapbox_access_token", "") or "").strip()
    if not token:
        raise GeocodingError("Mapbox não está configurado para geocodificação.")
    try:
        response = httpx.get(
            "https://api.mapbox.com/search/geocode/v6/forward",
            params={
                "q": address,
                "access_token": token,
                "autocomplete": "false",
                "limit": 1,
                "language": "pt",
                # Resultado será salvo no CalendarLocation; não usar o modo
                # temporário (que não permite persistência do resultado).
                "permanent": "true",
            },
            timeout=12,
            follow_redirects=False,
        )
    except httpx.HTTPError as exc:
        raise GeocodingError("O serviço de geocodificação do Mapbox está indisponível.") from exc
    if not response.is_success:
        raise GeocodingError(f"Mapbox Geocoding respondeu HTTP {response.status_code}.")
    payload = response.json()
    features = payload.get("features") or []
    if not features:
        raise GeocodingError("O endereço não foi localizado pelo Mapbox.")
    primeiro = features[0]
    coordenadas = (primeiro.get("geometry") or {}).get("coordinates") or []
    if len(coordenadas) < 2:
        raise GeocodingError("O Mapbox não devolveu coordenadas para este endereço.")
    properties = primeiro.get("properties") or {}
    contexto = properties.get("context") or {}
    formatado = (
        properties.get("full_address")
        or primeiro.get("place_name")
        or properties.get("name")
        or address
    )
    return {
        "provider": "mapbox_geocoding",
        "formatted_address": str(formatado),
        "latitude": float(coordenadas[1]),
        "longitude": float(coordenadas[0]),
        "mapbox_id": properties.get("mapbox_id") or primeiro.get("id"),
        "context": contexto,
    }


def geocode_address(address: str) -> dict[str, Any]:
    """Geocodifica um endereço usando provedores já configurados no CorVIA.

    Preferimos o mesmo ecossistema do provedor de trânsito ativo, mas há
    fallback para o outro provedor quando ambas as credenciais existem. Isso
    evita transformar uma indisponibilidade pontual de geocoding em pergunta
    manual de latitude/longitude ao médico.
    """
    texto = _texto_endereco(address)
    preferencia = getattr(settings, "traffic_provider", "")
    provedores = [_mapbox, _google] if preferencia == "mapbox" else [_google, _mapbox]
    erros: list[str] = []
    algum_configurado = False
    for provedor in provedores:
        if provedor is _google and not (getattr(settings, "google_routes_api_key", "") or "").strip():
            continue
        if provedor is _mapbox and not (getattr(settings, "mapbox_access_token", "") or "").strip():
            continue
        algum_configurado = True
        try:
            return provedor(texto)
        except GeocodingError as exc:
            erros.append(str(exc))
    if not algum_configurado:
        raise GeocodingError("Nenhum provedor de geocodificação está configurado no servidor.")
    raise GeocodingError(erros[-1] if erros else "Não foi possível geocodificar o endereço.")
