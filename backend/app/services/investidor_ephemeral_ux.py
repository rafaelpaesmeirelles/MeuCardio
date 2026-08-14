"""Estado efêmero de UX para a conta Investidor.

A conta de demonstração não pode produzir efeitos persistentes no banco, mas o
fluxo obrigatório continua sendo login -> tour -> home. Persistir
``onboarding_visto`` só para sair do tour violaria o contrato read-only; não
persistir estado algum faria o reload voltar ao tour para sempre.

A solução é um cookie HttpOnly de sessão vinculado criptograficamente ao token
de autenticação atual. Ele existe apenas no navegador/sessão, não toca banco,
não sobrevive como estado da conta e deixa de valer quando o token muda.
"""
from __future__ import annotations

from hashlib import sha256

from fastapi.encoders import jsonable_encoder
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

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        path = request.url.path
        method = request.method.upper()
        token = _token_da_requisicao(request)

        if token and path.startswith("/api/"):
            db = SessionLocal()
            try:
                user = usuario_por_token_app(db, token)
                investidor = user is not None and bool(getattr(user, "investidor", False))
                if investidor:
                    marcador = _marcador(token)

                    if (
                        method == "GET"
                        and path.startswith("/api/agenda/oauth/")
                        and path.endswith("/start")
                    ):
                        response = JSONResponse(
                            status_code=403,
                            content={"detail": MENSAGEM_MODO_INVESTIDOR},
                            headers={"Cache-Control": "no-store"},
                        )
                        await response(scope, receive, send)
                        return

                    if method == "POST" and path == "/api/auth/me/onboarding-concluido":
                        response = JSONResponse(
                            status_code=200,
                            content={"onboarding_pendente": False},
                            headers={"Cache-Control": "no-store"},
                        )
                        _set_cookie_sessao(response, _COOKIE_ONBOARDING, marcador)
                        await response(scope, receive, send)
                        return

                    if method == "POST" and path == "/api/auth/me/boas-vindas-vista":
                        response = JSONResponse(
                            status_code=200,
                            content={"boas_vindas_pendente": False},
                            headers={"Cache-Control": "no-store"},
                        )
                        _set_cookie_sessao(response, _COOKIE_BOAS_VINDAS, marcador)
                        await response(scope, receive, send)
                        return

                    if method == "GET" and path == "/api/auth/me":
                        tour_concluido = request.cookies.get(_COOKIE_ONBOARDING) == marcador
                        boas_vindas_vistas = request.cookies.get(_COOKIE_BOAS_VINDAS) == marcador
                        if tour_concluido or boas_vindas_vistas:
                            # Import local evita acoplamento/ciclo no carregamento do app.
                            from app.api.auth import _perfil

                            perfil = _perfil(db, user)
                            if tour_concluido:
                                perfil["onboarding_pendente"] = False
                            if boas_vindas_vistas:
                                perfil["boas_vindas_pendente"] = False
                            response = JSONResponse(
                                status_code=200,
                                content=jsonable_encoder(perfil),
                                headers={"Cache-Control": "no-store"},
                            )
                            await response(scope, receive, send)
                            return
            finally:
                db.close()

        await self.app(scope, receive, send)
