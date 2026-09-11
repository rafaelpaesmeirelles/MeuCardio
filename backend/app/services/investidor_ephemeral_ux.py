"""Estado efêmero de UX para a conta Investidor.

A conta de demonstração não pode produzir efeitos persistentes no banco, mas o
fluxo obrigatório continua sendo login -> tour -> home. Persistir
``onboarding_visto`` só para sair do tour violaria o contrato read-only; não
persistir estado algum faria o reload voltar ao tour para sempre.

A solução é um cookie HttpOnly de sessão vinculado criptograficamente ao token
de autenticação atual. Ele existe apenas no navegador/sessão, não toca banco,
não sobrevive como estado da conta e deixa de valer quando o token muda.

Regra de produto: toda NOVA sessão autenticada de Investidor deve começar no
tour, mesmo que ``onboarding_visto`` tenha valor legado ``True`` no banco. O
usuário pode assistir ou pular; depois dessa decisão, navega normalmente até a
sessão terminar. No próximo login, um novo token invalida o marcador anterior e
o tour volta a ser obrigatório como primeira tela.
"""
from __future__ import annotations

from hashlib import sha256

from fastapi.encoders import jsonable_encoder
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.db import SessionLocal
from app.core.runtime import ambiente_atual
from app.core.security import AUTH_COOKIE_NAME, usuario_por_token_app
from app.services.investidor_demo import MENSAGEM_MODO_INVESTIDOR

_COOKIE_ONBOARDING = "corvia_investidor_tour_sessao"
_COOKIE_BOAS_VINDAS = "corvia_investidor_boas_vindas_sessao"


def _token_da_requisicao(request: Request) -> str | None:
    authorization = request.headers.get("authorization", "").strip()
    if authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
        if token:
            return token
    return request.cookies.get(AUTH_COOKIE_NAME)


def _marcador(token: str) -> str:
    """Vincula a preferência efêmera ao token sem armazenar o token no cookie."""
    return sha256(token.encode("utf-8")).hexdigest()[:32]


def _set_cookie_sessao(response: JSONResponse, nome: str, valor: str) -> None:
    response.set_cookie(
        key=nome,
        value=valor,
        httponly=True,
        secure=ambiente_atual() == "production",
        samesite="lax",
        path="/",
    )


class InvestidorEphemeralUxMiddleware:
    """Completa o tour da demo sem gravação persistente.

    Também corrige a semântica de OAuth: iniciar conexão externa é uma ação
    operacional e deve receber a mensagem read-only genérica, antes do fallback
    fail-closed da Agenda sintética.
    """

    def __init__(self, app):
        self.app = app

    @staticmethod
    def _intercepta(path: str, method: str) -> bool:
        return (
            (method == "GET" and path == "/api/auth/me")
            or (method == "GET" and path.startswith("/api/agenda/oauth/") and path.endswith("/start"))
            or (method == "POST" and path in {
                "/api/auth/me/onboarding-concluido", "/api/auth/me/boas-vindas-vista",
            })
        )

    @staticmethod
    def _resposta(request: Request, token: str, path: str, method: str):
        # The synchronous pool checkout, queries and close belong to the same
        # worker. Never wait for a database connection on the ASGI event loop:
        # doing so prevents in-flight requests from returning their connections.
        db = SessionLocal()
        try:
            user = usuario_por_token_app(db, token)
            if user is None or not bool(getattr(user, "investidor", False)):
                return None
            marcador = _marcador(token)
            if method == "GET" and path.startswith("/api/agenda/oauth/"):
                return JSONResponse(status_code=403, content={"detail": MENSAGEM_MODO_INVESTIDOR}, headers={"Cache-Control": "no-store"})
            if method == "POST":
                onboarding = path == "/api/auth/me/onboarding-concluido"
                response = JSONResponse(
                    status_code=200,
                    content={"onboarding_pendente" if onboarding else "boas_vindas_pendente": False},
                    headers={"Cache-Control": "no-store"},
                )
                _set_cookie_sessao(response, _COOKIE_ONBOARDING if onboarding else _COOKIE_BOAS_VINDAS, marcador)
                return response

            from app.api.auth import _perfil

            perfil = _perfil(db, user)
            perfil["onboarding_pendente"] = request.cookies.get(_COOKIE_ONBOARDING) != marcador
            if request.cookies.get(_COOKIE_BOAS_VINDAS) == marcador:
                perfil["boas_vindas_pendente"] = False
            return JSONResponse(status_code=200, content=jsonable_encoder(perfil), headers={"Cache-Control": "no-store"})
        finally:
            # No ORM object or live transaction crosses back into async code.
            db.close()

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        path = request.url.path
        method = request.method.upper()
        token = _token_da_requisicao(request)

        if token and self._intercepta(path, method):
            response = await run_in_threadpool(self._resposta, request, token, path, method)
            if response is not None:
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)
