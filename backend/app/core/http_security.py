"""Defesas HTTP aplicadas antes das rotas FastAPI.

- valida a origem de operações autenticadas por cookie em produção;
- limita tentativas em superfícies de autenticação, recuperação, documentos
  públicos e IA;
- usa Redis para manter o limite coerente entre workers e réplicas.

Clientes externos que usam Bearer continuam permitidos sem cabeçalhos de
navegador. A proteção de origem é voltada ao cookie HttpOnly da interface web.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from http.cookies import CookieError, SimpleCookie
from urllib.parse import urlsplit

from redis.asyncio import Redis
from redis.exceptions import RedisError
from starlette.datastructures import Headers, MutableHeaders
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import settings
from app.core.runtime import ambiente_atual
from app.core.security import AUTH_COOKIE_NAME

_UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
_BROWSER_ONLY_PATHS = frozenset({
    "/api/auth/sessao",
    "/api/auth/sair",
    "/api/auth/encerrar-todas-sessoes",
})

_RATE_LIMIT_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
local ttl = redis.call('TTL', KEYS[1])
return {current, ttl}
"""


@dataclass(frozen=True)
class RateLimitRule:
    name: str
    limit: int
    window_seconds: int


# Limites deliberadamente conservadores: bloqueiam automação agressiva sem
# interferir no uso humano normal. A cota diária da IA continua sendo a regra
# de produto; este limite curto é apenas proteção contra rajadas.
_LOGIN_RULE = RateLimitRule("login", limit=10, window_seconds=300)
_RECOVERY_RULE = RateLimitRule("recuperacao", limit=5, window_seconds=3600)
_PUBLIC_DOCUMENT_RULE = RateLimitRule("documento-publico", limit=120, window_seconds=60)
_AI_RULE = RateLimitRule("ia", limit=20, window_seconds=60)


def _normalizar_origem(value: str | None) -> str | None:
    if not value or value == "null":
        return None
    try:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return None
        host = parsed.hostname.lower()
        port = parsed.port
    except (ValueError, TypeError):
        return None

    default_port = 80 if parsed.scheme == "http" else 443
    suffix = f":{port}" if port and port != default_port else ""
    return f"{parsed.scheme}://{host}{suffix}"


def _origens_permitidas(scope: Scope, headers: Headers) -> set[str]:
    allowed = {
        origin
        for origin in (
            _normalizar_origem(settings.public_url),
            *(_normalizar_origem(value) for value in settings.cors_list),
        )
        if origin
    }

    # Inclui o host efetivamente atendido. Isso cobre o domínio com e sem www,
    # além de homologação, sem abrir curingas de origem.
    host = headers.get("host")
    if host:
        proto = headers.get("x-forwarded-proto") or scope.get("scheme", "http")
        current = _normalizar_origem(f"{proto}://{host}")
        if current:
            allowed.add(current)
    return allowed


def _origem_da_requisicao(headers: Headers) -> str | None:
    origin = _normalizar_origem(headers.get("origin"))
    if origin:
        return origin
    return _normalizar_origem(headers.get("referer"))


def _tem_cookie_de_sessao(headers: Headers) -> bool:
    raw = headers.get("cookie")
    if not raw:
        return False
    cookie = SimpleCookie()
    try:
        cookie.load(raw)
    except CookieError:
        return False
    return AUTH_COOKIE_NAME in cookie


def _requer_validacao_de_origem(scope: Scope, headers: Headers) -> bool:
    method = str(scope.get("method", "GET")).upper()
    if method not in _UNSAFE_METHODS:
        return False
    if _tem_cookie_de_sessao(headers):
        return True

    # Login/logout da interface também são protegidos contra login-CSRF quando
    # a chamada tem metadados de navegador. CLI e integrações sem Sec-Fetch-Site
    # continuam usando os endpoints compatíveis.
    path = str(scope.get("path", ""))
    return path in _BROWSER_ONLY_PATHS and headers.get("sec-fetch-site") is not None


def _regra_para(method: str, path: str) -> RateLimitRule | None:
    if method == "POST" and path in {
        "/api/auth/login",
        "/api/auth/sessao",
        "/api/email/entrar",
    }:
        return _LOGIN_RULE
    if method == "POST" and path in {
        "/api/auth/esqueci-senha",
        "/api/auth/reenviar-ativacao",
        "/api/auth/redefinir-senha",
        "/api/auth/solicitar-acesso",
    }:
        return _RECOVERY_RULE
    if method == "GET" and path.startswith("/api/documentos-publicos/"):
        return _PUBLIC_DOCUMENT_RULE
    if method == "POST" and (path.startswith("/api/ai/") or path.endswith("/ai-assist")):
        return _AI_RULE
    return None


def _identificador_cliente(scope: Scope, headers: Headers) -> str:
    forwarded = headers.get("x-forwarded-for")
    if forwarded:
        # Usa o último salto. O proxy de produção substitui/normaliza o header;
        # escolher o último evita confiar no primeiro valor injetado pelo cliente.
        client_ip = forwarded.split(",")[-1].strip()
    else:
        client = scope.get("client")
        client_ip = str(client[0]) if client else "desconhecido"
    return sha256(client_ip.encode("utf-8")).hexdigest()[:24]


class HttpSecurityMiddleware:
    """ASGI middleware sem leitura de body, compatível com streaming e uploads."""

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
        if self.force_enabled is not None:
            return self.force_enabled
        return ambiente_atual() == "production"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not self.enabled:
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        method = str(scope.get("method", "GET")).upper()
        path = str(scope.get("path", ""))

        if _requer_validacao_de_origem(scope, headers):
            request_origin = _origem_da_requisicao(headers)
            if request_origin not in _origens_permitidas(scope, headers):
                response = JSONResponse(
                    {"detail": "Origem da requisição não autorizada."},
                    status_code=403,
                )
                await response(scope, receive, send)
                return

        rule = _regra_para(method, path)
        rate_headers: dict[str, str] = {}
        if rule is not None:
            client_id = _identificador_cliente(scope, headers)
            key = f"corvia:rate:{rule.name}:{client_id}"
            try:
                current, ttl = await self.redis.eval(
                    _RATE_LIMIT_SCRIPT,
                    1,
                    key,
                    rule.window_seconds,
                )
                current = int(current)
                ttl = max(int(ttl), 1)
            except (RedisError, OSError, ValueError, TypeError):
                response = JSONResponse(
                    {"detail": "Proteção contra abuso temporariamente indisponível."},
                    status_code=503,
                    headers={"Retry-After": "5"},
                )
                await response(scope, receive, send)
                return

            remaining = max(rule.limit - current, 0)
            rate_headers = {
                "X-RateLimit-Limit": str(rule.limit),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(ttl),
            }
            if current > rule.limit:
                response = JSONResponse(
                    {"detail": "Muitas tentativas. Aguarde antes de tentar novamente."},
                    status_code=429,
                    headers={**rate_headers, "Retry-After": str(ttl)},
                )
                await response(scope, receive, send)
                return

        async def send_with_rate_headers(message: Message) -> None:
            if message["type"] == "http.response.start" and rate_headers:
                mutable = MutableHeaders(scope=message)
                for name, value in rate_headers.items():
                    mutable[name] = value
            await send(message)

        await self.app(scope, receive, send_with_rate_headers)
