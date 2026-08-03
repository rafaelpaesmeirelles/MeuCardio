"""Logs estruturados de requisição com correlação e minimização de dados.

A camada registra apenas metadados operacionais: método, rota normalizada,
status, duração e request ID. Query string, corpo, headers, cookies, IP e
identidade do usuário não entram no log.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

from starlette.datastructures import Headers, MutableHeaders
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.runtime import ambiente_atual

REQUEST_ID_HEADER = "X-Request-ID"
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$")
_UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-"
    r"[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
)
_EMAIL_PATTERN = re.compile(r"^[^/@\s]+@[^/@\s]+\.[^/@\s]+$")
_TOKENISH_PATTERN = re.compile(r"^[A-Za-z0-9_-]{40,}$")

request_id_context: ContextVar[str | None] = ContextVar(
    "corvia_request_id", default=None
)


class JsonRequestFormatter(logging.Formatter):
    """Serializa somente campos operacionais explicitamente permitidos."""

    _fields = (
        "event",
        "request_id",
        "method",
        "path",
        "status_code",
        "duration_ms",
        "environment",
        "error_type",
    )

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname.lower(),
            "service": "corvia-api",
        }
        for field in self._fields:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        return json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )


def _configured_level() -> int:
    level_name = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    return getattr(logging, level_name, logging.INFO)


def _request_logger() -> logging.Logger:
    logger = logging.getLogger("corvia.request")
    logger.setLevel(_configured_level())
    logger.propagate = False

    if not any(getattr(handler, "_corvia_json", False) for handler in logger.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonRequestFormatter())
        handler._corvia_json = True  # type: ignore[attr-defined]
        logger.addHandler(handler)
    return logger


logger = _request_logger()


def current_request_id() -> str | None:
    return request_id_context.get()


def _resolve_request_id(scope: Scope) -> str:
    candidate = Headers(scope=scope).get("x-request-id", "").strip()
    if candidate and _REQUEST_ID_PATTERN.fullmatch(candidate):
        return candidate
    return uuid.uuid4().hex


def normalize_path(path: str) -> str:
    """Remove identificadores e tokens de caminhos ainda não casados por rota."""
    segments = path.split("/")
    normalized: list[str] = []
    previous = ""

    for segment in segments:
        replacement = segment
        if not segment:
            normalized.append(segment)
            continue

        if previous == "documentos-publicos":
            replacement = "{token}"
        elif segment.isdigit() or _UUID_PATTERN.fullmatch(segment):
            replacement = "{id}"
        elif _EMAIL_PATTERN.fullmatch(segment):
            replacement = "{value}"
        elif _TOKENISH_PATTERN.fullmatch(segment):
            replacement = "{token}"

        normalized.append(replacement)
        previous = segment

    return "/".join(normalized)


def _route_path(scope: Scope) -> str:
    route = scope.get("route")
    template = getattr(route, "path", None)
    if isinstance(template, str) and template:
        return template
    return normalize_path(str(scope.get("path", "")))


def _should_log(path: str, status_code: int) -> bool:
    return not (
        status_code < 500 and path in {"/api/health", "/api/ready"}
    )


class StructuredRequestLoggingMiddleware:
    """ASGI middleware de correlação, resposta segura e log operacional."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = _resolve_request_id(scope)
        context_token = request_id_context.set(request_id)
        scope.setdefault("state", {})["request_id"] = request_id

        started_at = time.perf_counter()
        status_code = 500
        response_started = False
        error_type: str | None = None

        async def send_with_request_id(message: Message) -> None:
            nonlocal status_code, response_started
            if message["type"] == "http.response.start":
                response_started = True
                status_code = int(message["status"])
                headers = MutableHeaders(scope=message)
                headers[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        except Exception as exc:
            error_type = type(exc).__name__
            status_code = 500
            if response_started:
                raise

            response = JSONResponse(
                status_code=500,
                content={
                    "detail": "Erro interno. Informe o identificador ao suporte.",
                    "request_id": request_id,
                },
            )
            await response(scope, receive, send_with_request_id)
        finally:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            path = _route_path(scope)
            if _should_log(path, status_code):
                level = (
                    logging.ERROR
                    if status_code >= 500
                    else logging.WARNING
                    if status_code >= 400
                    else logging.INFO
                )
                logger.log(
                    level,
                    "http_request",
                    extra={
                        "event": "http_request",
                        "request_id": request_id,
                        "method": str(scope.get("method", "")),
                        "path": path,
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                        "environment": ambiente_atual(),
                        "error_type": error_type,
                    },
                )
            request_id_context.reset(context_token)
