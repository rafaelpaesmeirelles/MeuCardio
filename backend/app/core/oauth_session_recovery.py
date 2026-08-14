"""Recupera de forma segura a sessão web após o round-trip OAuth.

O navegador usa cookie HttpOnly para a sessão principal. Mesmo com SameSite=Lax,
alguns fluxos reais de Google/Microsoft retornaram do provedor para o callback
sem que a navegação seguinte até o SPA preservasse uma sessão utilizável,
levando o AuthProvider a receber 401 em ``/auth/me`` e redirecionar para
``/entrar``.

O callback OAuth já possui um artefato de alta entropia, uso único e ligado ao
usuário: ``IntegrationOAuthState.state_digest``. Depois de o router concluir a
autorização com sucesso (estado consumido + integração criada), este middleware
usa SOMENTE esse estado já consumido para reemitir o cookie da MESMA conta.
Não há parâmetro de user_id controlado pelo cliente e não há recuperação em
callback com erro.
"""
from __future__ import annotations

import hashlib
from urllib.parse import parse_qs, urlparse

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.db import SessionLocal
from app.core.security import create_access_token, gravar_cookie_sessao
from app.models.agenda import IntegrationOAuthState
from app.models.user import User


_CALLBACKS = {
    "/api/agenda/oauth/google/callback",
    "/api/agenda/oauth/microsoft/callback",
}


def _oauth_sucesso(response) -> bool:
    if response.status_code not in {302, 303, 307, 308}:
        return False
    destino = response.headers.get("location") or ""
    try:
        params = parse_qs(urlparse(destino).query)
    except ValueError:
        return False
    return bool(params.get("conta_conectada")) and not params.get("conta_erro")


class OAuthSessionRecoveryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path not in _CALLBACKS:
            return await call_next(request)

        # Captura antes de chamar o router: complete_oauth() marcará o estado
        # como usado durante a própria requisição.
        state = request.query_params.get("state") or ""
        response = await call_next(request)
        if not state or not _oauth_sucesso(response):
            return response

        digest = hashlib.sha256(state.encode()).hexdigest()
        db = SessionLocal()
        try:
            registro = db.query(IntegrationOAuthState).filter(
                IntegrationOAuthState.state_digest == digest,
                IntegrationOAuthState.used_at.is_not(None),
            ).first()
            if registro is None:
                return response
            user = db.get(User, registro.owner_id)
            if (
                user is None
                or not user.is_active
                or user.status in {"pendente", "rejeitado"}
            ):
                return response
            gravar_cookie_sessao(response, create_access_token(user.email, scope="app"))
            return response
        finally:
            db.close()
