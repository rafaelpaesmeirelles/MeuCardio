"""Headers defensivos e política de cache das respostas da API."""

from __future__ import annotations

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

CACHEABLE_CONTENT_PREFIXES = (
    "/api/library",
    "/api/calculators",
    "/api/drugs",
    "/api/material-paciente",
    "/api/emergencia",
)

COMMON_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), usb=(), serial=(), payment=()",
    "Cross-Origin-Resource-Policy": "same-origin",
    "X-Permitted-Cross-Domain-Policies": "none",
}


def _cacheable_success(path: str, status_code: int) -> bool:
    return status_code < 400 and path.startswith(CACHEABLE_CONTENT_PREFIXES)


class ApiSecurityHeadersMiddleware:
    """Aplica headers comuns e impede cache de respostas sensíveis.

    Somente conteúdo médico global, explicitamente allowlisted, pode preservar
    sua política de cache. Autenticação, dados de paciente, documentos, e-mail,
    administração e qualquer resposta de erro recebem ``no-store``.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = str(scope.get("path", ""))

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                for name, value in COMMON_SECURITY_HEADERS.items():
                    headers[name] = value

                status_code = int(message["status"])
                if not _cacheable_success(path, status_code):
                    headers["Cache-Control"] = "no-store, max-age=0"
                    headers["Pragma"] = "no-cache"
                    headers["Expires"] = "0"
            await send(message)

        await self.app(scope, receive, send_with_headers)
