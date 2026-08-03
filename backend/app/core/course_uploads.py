"""Política de upload para materiais administrativos de cursos parceiros.

O material de curso possui limite maior que anexos clínicos e de e-mail, mas
continua com allowlist fechada. Este middleware reutiliza os validadores
estruturais do módulo central de uploads e preserva o multipart aprovado para o
router FastAPI existente.
"""

from __future__ import annotations

import re
from pathlib import Path

from redis.asyncio import Redis
from redis.exceptions import RedisError
from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import settings
from app.core.runtime import ambiente_atual
from app.core.uploads import (
    UploadRejected,
    _CHUNK_OVERHEAD,
    _RATE_SCRIPT,
    _UPLOAD_LIMIT,
    _UPLOAD_WINDOW_SECONDS,
    _client_key,
    _parse_single_file,
    validate_file,
)

_COURSE_PATH = re.compile(r"/api/cursos/admin/[^/]+/material")
_COURSE_MAX_FILE_BYTES = 40 * 1024 * 1024
_ALLOWED_SUFFIXES = {".pdf", ".jpg", ".jpeg", ".png", ".docx", ".xlsx", ".pptx"}


def is_course_upload(method: str, path: str) -> bool:
    return method == "POST" and _COURSE_PATH.fullmatch(path) is not None


def validate_course_file(data: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in _ALLOWED_SUFFIXES:
        raise UploadRejected(
            422,
            "Material de curso deve ser PDF, JPEG, PNG, DOCX, XLSX ou PPTX.",
        )
    if suffix in {".jpg", ".jpeg", ".png"}:
        return validate_file(data, filename, "image")
    return validate_file(data, filename, "email")


async def _read_course_upload(receive: Receive, headers: Headers) -> Receive:
    content_type = headers.get("content-type", "")
    if not content_type.lower().startswith("multipart/form-data;"):
        raise UploadRejected(415, "O upload precisa usar multipart/form-data.")

    max_body = _COURSE_MAX_FILE_BYTES + _CHUNK_OVERHEAD
    raw_length = headers.get("content-length")
    if raw_length:
        try:
            if int(raw_length) > max_body:
                raise UploadRejected(413, "O material excede o limite de 40 MB.")
        except ValueError:
            raise UploadRejected(400, "Content-Length inválido.") from None

    chunks: list[bytes] = []
    total = 0
    while True:
        message = await receive()
        if message["type"] == "http.disconnect":
            raise UploadRejected(400, "Upload interrompido pelo cliente.")
        if message["type"] != "http.request":
            continue
        chunk = message.get("body", b"")
        total += len(chunk)
        if total > max_body:
            raise UploadRejected(413, "O material excede o limite de 40 MB.")
        chunks.append(chunk)
        if not message.get("more_body", False):
            break

    body = b"".join(chunks)
    filename, file_data = _parse_single_file(body, content_type)
    if len(file_data) > _COURSE_MAX_FILE_BYTES:
        raise UploadRejected(413, "O material excede o limite de 40 MB.")
    validate_course_file(file_data, filename)

    delivered = False

    async def replay() -> Message:
        nonlocal delivered
        if delivered:
            return {"type": "http.request", "body": b"", "more_body": False}
        delivered = True
        return {"type": "http.request", "body": body, "more_body": False}

    return replay


class CourseUploadSecurityMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        force_enabled: bool | None = None,
        redis_client: Redis | None = None,
    ) -> None:
        self.app = app
        self.force_enabled = force_enabled
        self.redis = redis_client or Redis.from_url(settings.redis_url, decode_responses=True)

    @property
    def enabled(self) -> bool:
        return self.force_enabled if self.force_enabled is not None else ambiente_atual() == "production"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not self.enabled:
            await self.app(scope, receive, send)
            return

        method = str(scope.get("method", "GET")).upper()
        path = str(scope.get("path", ""))
        if not is_course_upload(method, path):
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        key = _client_key(scope, headers, "material-curso")
        try:
            current, ttl = await self.redis.eval(_RATE_SCRIPT, 1, key, _UPLOAD_WINDOW_SECONDS)
            current, ttl = int(current), max(int(ttl), 1)
        except (RedisError, OSError, TypeError, ValueError):
            response = JSONResponse(
                {"detail": "Proteção de upload temporariamente indisponível."},
                status_code=503,
                headers={"Retry-After": "5"},
            )
            await response(scope, receive, send)
            return

        if current > _UPLOAD_LIMIT:
            response = JSONResponse(
                {"detail": "Muitos uploads. Aguarde antes de tentar novamente."},
                status_code=429,
                headers={"Retry-After": str(ttl)},
            )
            await response(scope, receive, send)
            return

        try:
            replay = await _read_course_upload(receive, headers)
        except UploadRejected as error:
            response = JSONResponse({"detail": error.detail}, status_code=error.status_code)
            await response(scope, receive, send)
            return

        await self.app(scope, replay, send)
