"""Observabilidade HTTP com minimização deliberada de dados.

Os logs desta camada nunca incluem query string, headers, cookies, body, e-mail,
CPF, nome do paciente ou conteúdo clínico. Cada requisição recebe um identificador
opaco que também pode ser persistido na auditoria do banco.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
import traceback
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from starlette.datastructures import Headers, MutableHeaders
from starlette.responses import JSONResponse
from starlette.routing import Match
from starlette.types import ASGIApp, Message, Receive, Scope, Send

_REQUEST_ID: ContextVar[str | None] = ContextVar("corvia_request_id", default=None)
_VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")
_ALLOWED_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
_LOG_FIELDS = (
    "event",
    "request_id",
    "method",
    "route",
    "status_code",
    "duration_ms",
    "error_type",
    "error_stack",
    "components",
    "operation",
    "result",
)


def current_request_id() -> str | None:
    """Identificador da requisição atual, quando o código roda dentro do HTTP."""
    return _REQUEST_ID.get()


@contextmanager
def bind_request_id(value: str) -> Iterator[None]:
    """Permite propagar o identificador em comandos/testes fora do middleware."""
    token = _REQUEST_ID.set(value)
    try:
        yield
    finally:
        _REQUEST_ID.reset(token)


class CorviaJsonFormatter(logging.Formatter):
    """Serializa somente campos previamente aprovados, nunca o ``record`` inteiro."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "service": "corvia-api",
            "environment": os.getenv("ENVIRONMENT", "development").strip().lower(),
            "message": record.getMessage(),
        }
        for field in _LOG_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        # ``logging.exception`` carrega o traceback em ``exc_info``. Mantemos
        # apenas tipo e frames (arquivo/linha/função), sem mensagem nem locais,
        # para diagnosticar produção sem registrar PHI, tokens ou payloads.
        if record.exc_info and record.exc_info[1] is not None:
            exc = record.exc_info[1]
            payload.setdefault("error_type", type(exc).__name__)
            payload.setdefault("error_stack", _stack_summary(exc))
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str)


def configure_observability_logging(level: str | None = None) -> logging.Logger:
    """Configura uma única saída JSON para os eventos próprios da Corvia."""
    selected = (level or os.getenv("LOG_LEVEL", "INFO")).strip().upper()
    if selected not in _ALLOWED_LEVELS:
        selected = "INFO"

    logger = logging.getLogger("corvia")
    logger.setLevel(selected)
    logger.propagate = False

    if not any(getattr(handler, "_corvia_json", False) for handler in logger.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(CorviaJsonFormatter())
        handler._corvia_json = True  # type: ignore[attr-defined]
        logger.addHandler(handler)

    # O middleware abaixo substitui o access log por um evento estruturado e
    # evita duas linhas para a mesma requisição.
    logging.getLogger("uvicorn.access").disabled = True
    return logger


def _request_id(headers: Headers) -> str:
    supplied = (headers.get("x-request-id") or "").strip()
    if _VALID_REQUEST_ID.fullmatch(supplied):
        return supplied
    return uuid.uuid4().hex


def _route_template(app: ASGIApp, scope: Scope) -> str | None:
    """Encontra o template sem depender de dados adicionados depois pelo router.

    O middleware é a camada mais externa, portanto ``scope['route']`` pode não
    existir mesmo após a resposta. Desembrulhar as camadas e usar ``matches``
    permite obter o padrão registrado sem registrar o caminho real do usuário.
    """
    current: object | None = app
    visited: set[int] = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        routes = getattr(current, "routes", None)
        if routes:
            for route in routes:
                try:
                    match, _ = route.matches(dict(scope))
                except Exception:
                    continue
                if match == Match.FULL:
                    template = getattr(route, "path", None)
                    if isinstance(template, str) and template:
                        return template
        current = getattr(current, "app", None)
    return None


def _safe_route(scope: Scope, app: ASGIApp) -> str:
    """Prefere o template da rota e nunca registra query ou parâmetros reais."""
    route = scope.get("route")
    template = getattr(route, "path", None)
    if isinstance(template, str) and template:
        return template

    resolved = _route_template(app, scope)
    if resolved:
        return resolved

    path = str(scope.get("path") or "/")
    parts = [part for part in path.split("/") if part]
    if not parts:
        return "/"
    if parts[0] == "api":
        safe = parts[:2]
        if len(parts) > 2:
            safe.append("{unresolved}")
        return "/" + "/".join(safe)
    return "/{unresolved}"


def _stack_summary(exc: Exception) -> list[str]:
    """Stack sem mensagem da exceção e sem variáveis locais potencialmente sensíveis."""
    frames = traceback.extract_tb(exc.__traceback__)[-20:]
    return [f"{Path(frame.filename).name}:{frame.lineno}:{frame.name}" for frame in frames]


class ObservabilityMiddleware:
    def __init__(self, app: ASGIApp, *, event_logger: logging.Logger | None = None) -> None:
        self.app = app
        self.logger = event_logger or logging.getLogger("corvia.http")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        request_id = _request_id(headers)
        token = _REQUEST_ID.set(request_id)
        scope.setdefault("state", {})["request_id"] = request_id
        started = time.perf_counter()
        status_code = 500
        response_started = False

        async def send_with_request_id(message: Message) -> None:
            nonlocal status_code, response_started
            if message["type"] == "http.response.start":
                response_started = True
                status_code = int(message["status"])
                MutableHeaders(scope=message)["X-Request-ID"] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        except Exception as exc:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            self.logger.error(
                "http_request_failed",
                extra={
                    "event": "http_request_failed",
                    "request_id": request_id,
                    "method": str(scope.get("method", "GET")).upper(),
                    "route": _safe_route(scope, self.app),
                    "status_code": 500,
                    "duration_ms": duration_ms,
                    "error_type": type(exc).__name__,
                    "error_stack": _stack_summary(exc),
                },
            )
            if response_started:
                # Streaming já iniciado não pode ser substituído por outra
                # resposta. O header de correlação já foi enviado nesse caso.
                raise
            response = JSONResponse(
                {"detail": "Erro interno. Informe o X-Request-ID ao suporte."},
                status_code=500,
                headers={"X-Request-ID": request_id},
            )
            await response(scope, receive, send)
        else:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            log = self.logger.warning if status_code >= 500 else self.logger.info
            log(
                "http_request_completed",
                extra={
                    "event": "http_request_completed",
                    "request_id": request_id,
                    "method": str(scope.get("method", "GET")).upper(),
                    "route": _safe_route(scope, self.app),
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                },
            )
        finally:
            _REQUEST_ID.reset(token)
