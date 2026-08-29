from __future__ import annotations

import re
from hashlib import sha256

from redis.asyncio import Redis
from redis.exceptions import RedisError
from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import settings
from app.core.runtime import ambiente_atual
from app.core.uploads import UploadPolicy, UploadRejected, _read_and_validate

_UPLOAD_LIMIT = 20
_UPLOAD_WINDOW_SECONDS = 600
_RATE_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
local ttl = redis.call('TTL', KEYS[1])
return {current, ttl}
"""

_PATIENT_MULTIMODAL = UploadPolicy(
    "prontuario-multimodal",
    20 * 1024 * 1024,
    "clinical_exam",
    max_files=1,
    max_total_file_bytes=20 * 1024 * 1024,
)
_SCIENTIFIC_DOCUMENT = UploadPolicy(
    "documento-cientifico-ia",
    25 * 1024 * 1024,
    "email",
    max_files=1,
    max_total_file_bytes=25 * 1024 * 1024,
)


def _policy(method: str, path: str) -> UploadPolicy | None:
    if method != "POST":
        return None
    if re.fullmatch(r"/api/pacientes/\d+/exames-multimodais", path):
        return _PATIENT_MULTIMODAL
    if path == "/api/documentos-cientificos-ia":
        return _SCIENTIFIC_DOCUMENT
    return None


def _key(scope: Scope, headers: Headers, name: str) -> str:
    forwarded = headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[-1].strip()
    else:
        client = scope.get("client")
        ip = str(client[0]) if client else "desconhecido"
    digest = sha256(ip.encode("utf-8")).hexdigest()[:24]
    return f"corvia:upload:{name}:{digest}"


class NewFeatureUploadSecurityMiddleware:
    """Barreira de body/rate-limit dos uploads introduzidos na release.

    Reusa exatamente o validador central de MIME/conteúdo. O middleware geral
    continua responsável pelos endpoints legados; esta camada é deliberadamente
    restrita às duas rotas novas para não alterar contratos existentes.
    """

    def __init__(self, app: ASGIApp, *, force_enabled: bool | None = None) -> None:
        self.app = app
        self.force_enabled = force_enabled
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    @property
    def enabled(self) -> bool:
        return self.force_enabled if self.force_enabled is not None else ambiente_atual() == "production"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not self.enabled:
            await self.app(scope, receive, send)
            return
        policy = _policy(str(scope.get("method", "GET")).upper(), str(scope.get("path", "")))
        if policy is None:
            await self.app(scope, receive, send)
            return
        headers = Headers(scope=scope)
        try:
            current, ttl = await self.redis.eval(_RATE_SCRIPT, 1, _key(scope, headers, policy.name), _UPLOAD_WINDOW_SECONDS)
            current, ttl = int(current), max(int(ttl), 1)
        except (RedisError, OSError, TypeError, ValueError):
            response = JSONResponse({"detail": "Proteção de upload temporariamente indisponível."}, status_code=503, headers={"Retry-After": "5"})
            await response(scope, receive, send)
            return
        if current > _UPLOAD_LIMIT:
            response = JSONResponse({"detail": "Muitos uploads. Aguarde antes de tentar novamente."}, status_code=429, headers={"Retry-After": str(ttl)})
            await response(scope, receive, send)
            return
        try:
            replay = await _read_and_validate(scope, receive, headers, policy)
        except UploadRejected as error:
            response = JSONResponse({"detail": error.detail}, status_code=error.status_code)
            await response(scope, receive, send)
            return
        await self.app(scope, replay, send)
