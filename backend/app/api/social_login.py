"""Login social do CorVIA para contas já aprovadas.

Este fluxo autentica identidade; não cria usuário e não contorna cadastro,
revisão profissional, KYC ou assinatura. O e-mail confirmado pelo provedor
precisa corresponder a uma conta CorVIA existente e ativa.

Google/Microsoft podem reutilizar as credenciais OAuth já existentes da Agenda
quando não houver cliente de login dedicado. Apple, Yahoo e GitHub são
habilitados somente quando suas credenciais próprias estiverem configuradas no
ambiente.
"""
from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.runtime import ambiente_atual
from app.core.security import create_access_token, gravar_cookie_sessao
from app.models.user import User

router = APIRouter(prefix="/api/auth/social", tags=["auth"])

_STATE_COOKIE = "corvia_social_state"
_NONCE_COOKIE = "corvia_social_nonce"
_PROVIDER_COOKIE = "corvia_social_provider"
_COOKIE_MAX_AGE = 10 * 60
_SUPPORTED = {"google", "microsoft", "apple", "github"}

_GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
_GOOGLE_USERINFO = "https://openidconnect.googleapis.com/v1/userinfo"
_MICROSOFT_USERINFO = "https://graph.microsoft.com/oidc/userinfo"
_APPLE_AUTH = "https://appleid.apple.com/auth/authorize"
_APPLE_TOKEN = "https://appleid.apple.com/auth/token"
_APPLE_JWKS = "https://appleid.apple.com/auth/keys"
_YAHOO_AUTH = "https://api.login.yahoo.com/oauth2/request_auth"
_YAHOO_TOKEN = "https://api.login.yahoo.com/oauth2/get_token"
_YAHOO_USERINFO = "https://api.login.yahoo.com/openid/v1/userinfo"
_GITHUB_AUTH = "https://github.com/login/oauth/authorize"
_GITHUB_TOKEN = "https://github.com/login/oauth/access_token"
_GITHUB_USER = "https://api.github.com/user"
_GITHUB_EMAILS = "https://api.github.com/user/emails"


def _env(name: str) -> str:
    return (os.getenv(name) or "").strip()


def _google_credentials() -> tuple[str, str]:
    return (
        _env("GOOGLE_SIGNIN_CLIENT_ID") or settings.google_oauth_client_id,
        _env("GOOGLE_SIGNIN_CLIENT_SECRET") or settings.google_oauth_client_secret,
    )


def _microsoft_credentials() -> tuple[str, str]:
    return (
        _env("MICROSOFT_SIGNIN_CLIENT_ID") or settings.microsoft_oauth_client_id,
        _env("MICROSOFT_SIGNIN_CLIENT_SECRET") or settings.microsoft_oauth_client_secret,
    )


def _provider_credentials(provider: str) -> tuple[str, str]:
    if provider == "google":
        return _google_credentials()
    if provider == "microsoft":
        return _microsoft_credentials()
    if provider == "apple":
        return _env("APPLE_SIGNIN_CLIENT_ID"), _env("APPLE_SIGNIN_KEY_ID")
    if provider == "yahoo":
        return _env("YAHOO_SIGNIN_CLIENT_ID"), _env("YAHOO_SIGNIN_CLIENT_SECRET")
    if provider == "github":
        return _env("GITHUB_SIGNIN_CLIENT_ID"), _env("GITHUB_SIGNIN_CLIENT_SECRET")
    return "", ""


def _configured(provider: str) -> bool:
    client_id, client_secret = _provider_credentials(provider)
    if provider == "apple":
        return bool(
            client_id
            and client_secret
            and _env("APPLE_SIGNIN_TEAM_ID")
            and _env("APPLE_SIGNIN_PRIVATE_KEY")
        )
    return bool(client_id and client_secret)


def _redirect_uri(provider: str) -> str:
    return f"{settings.public_url.rstrip('/')}/api/auth/social/{provider}/callback"


def _microsoft_authority() -> str:
    tenant = (_env("MICROSOFT_SIGNIN_TENANT") or settings.microsoft_oauth_tenant or "common").strip()
    if not tenant or not all(ch.isalnum() or ch in {"-", "."} for ch in tenant):
        raise HTTPException(status_code=503, detail="Tenant Microsoft de login inválido.")
    return f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0"


def _cookie_options() -> dict[str, Any]:
    production = ambiente_atual() == "production"
    # Apple retorna por form_post cross-site; SameSite=None é necessário nesse
    # caminho. Em desenvolvimento sem HTTPS usamos Lax porque navegadores
    # rejeitam SameSite=None sem Secure.
    return {
        "max_age": _COOKIE_MAX_AGE,
        "httponly": True,
        "secure": production,
        "samesite": "none" if production else "lax",
        "path": "/api/auth/social",
    }


def _set_flow_cookies(response: RedirectResponse, provider: str, state: str, nonce: str) -> None:
    options = _cookie_options()
    response.set_cookie(_STATE_COOKIE, state, **options)
    response.set_cookie(_NONCE_COOKIE, nonce, **options)
    response.set_cookie(_PROVIDER_COOKIE, provider, **options)


def _clear_flow_cookies(response: RedirectResponse) -> None:
    options = _cookie_options()
    for name in (_STATE_COOKIE, _NONCE_COOKIE, _PROVIDER_COOKIE):
        response.delete_cookie(
            name,
            httponly=True,
            secure=options["secure"],
            samesite=options["samesite"],
            path=options["path"],
        )


def _login_error(code: str, provider: str = "") -> RedirectResponse:
    query = urlencode({"social_error": code, "provider": provider})
    response = RedirectResponse(url=f"/entrar?{query}", status_code=303)
    _clear_flow_cookies(response)
    return response


def _valid_user(db: Session, email: str) -> User | None:
    normalized = email.strip().lower()
    if not normalized:
        return None
    user = db.query(User).filter(User.email == normalized).first()
    if user is None or not user.is_active or user.status in {"pendente", "rejeitado"}:
        return None
    return user


def _apple_client_secret() -> str:
    raw_key = _env("APPLE_SIGNIN_PRIVATE_KEY").replace("\\n", "\n")
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "iss": _env("APPLE_SIGNIN_TEAM_ID"),
            "iat": now,
            "exp": now + timedelta(minutes=10),
            "aud": "https://appleid.apple.com",
            "sub": _env("APPLE_SIGNIN_CLIENT_ID"),
        },
        raw_key,
        algorithm="ES256",
        headers={"kid": _env("APPLE_SIGNIN_KEY_ID")},
    )


def _auth_url(provider: str, state: str, nonce: str) -> str:
    client_id, _ = _provider_credentials(provider)
    redirect_uri = _redirect_uri(provider)
    if provider == "google":
        return f"{_GOOGLE_AUTH}?{urlencode({'client_id': client_id, 'redirect_uri': redirect_uri, 'response_type': 'code', 'scope': 'openid email profile', 'state': state, 'nonce': nonce, 'prompt': 'select_account'})}"
    if provider == "microsoft":
        return f"{_microsoft_authority()}/authorize?{urlencode({'client_id': client_id, 'redirect_uri': redirect_uri, 'response_type': 'code', 'response_mode': 'query', 'scope': 'openid profile email', 'state': state, 'nonce': nonce, 'prompt': 'select_account'})}"
    if provider == "apple":
        return f"{_APPLE_AUTH}?{urlencode({'client_id': client_id, 'redirect_uri': redirect_uri, 'response_type': 'code', 'response_mode': 'form_post', 'scope': 'name email', 'state': state, 'nonce': nonce})}"
    if provider == "yahoo":
        return f"{_YAHOO_AUTH}?{urlencode({'client_id': client_id, 'redirect_uri': redirect_uri, 'response_type': 'code', 'scope': 'openid profile email', 'state': state, 'nonce': nonce})}"
    if provider == "github":
        return f"{_GITHUB_AUTH}?{urlencode({'client_id': client_id, 'redirect_uri': redirect_uri, 'scope': 'read:user user:email', 'state': state, 'allow_signup': 'false'})}"
    raise HTTPException(status_code=404, detail="Provedor de login não suportado.")


async def _exchange(provider: str, code: str) -> dict[str, Any]:
    client_id, client_secret = _provider_credentials(provider)
    payload: dict[str, str] = {
        "client_id": client_id,
        "code": code,
        "redirect_uri": _redirect_uri(provider),
    }
    headers: dict[str, str] = {"Accept": "application/json"}
    if provider == "google":
        payload.update({"client_secret": client_secret, "grant_type": "authorization_code"})
        url = _GOOGLE_TOKEN
    elif provider == "microsoft":
        payload.update({"client_secret": client_secret, "grant_type": "authorization_code", "scope": "openid profile email"})
        url = f"{_microsoft_authority()}/token"
    elif provider == "apple":
        payload.update({"client_secret": _apple_client_secret(), "grant_type": "authorization_code"})
        url = _APPLE_TOKEN
    elif provider == "yahoo":
        payload.update({"client_secret": client_secret, "grant_type": "authorization_code"})
        url = _YAHOO_TOKEN
    elif provider == "github":
        payload.update({"client_secret": client_secret})
        url = _GITHUB_TOKEN
    else:
        raise HTTPException(status_code=404, detail="Provedor de login não suportado.")

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, data=payload, headers=headers)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Falha ao contactar o provedor de identidade.") from exc
    if response.status_code >= 400:
        raise HTTPException(status_code=400, detail="O provedor recusou a autenticação.")
    body = response.json()
    if not body.get("access_token") and not body.get("id_token"):
        raise HTTPException(status_code=400, detail="Resposta de autenticação incompleta.")
    return body


async def _identity(provider: str, token: dict[str, Any], nonce: str) -> tuple[str, str]:
    if provider == "apple":
        id_token = str(token.get("id_token") or "")
        try:
            signing_key = jwt.PyJWKClient(_APPLE_JWKS).get_signing_key_from_jwt(id_token)
            claims = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=_env("APPLE_SIGNIN_CLIENT_ID"),
                issuer="https://appleid.apple.com",
            )
        except (jwt.PyJWTError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Identidade Apple inválida.") from exc
        if claims.get("nonce") and not secrets.compare_digest(str(claims["nonce"]), nonce):
            raise HTTPException(status_code=400, detail="Nonce Apple inválido.")
        verified = str(claims.get("email_verified", "")).lower() in {"true", "1"}
        email = str(claims.get("email") or "")
        if not email or not verified:
            raise HTTPException(status_code=400, detail="A Apple não confirmou um e-mail utilizável.")
        return email, str(claims.get("sub") or email)

    access_token = str(token.get("access_token") or "")
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
            if provider == "google":
                response = await client.get(_GOOGLE_USERINFO)
                body = response.json() if response.status_code < 400 else {}
                if response.status_code >= 400 or not body.get("email_verified"):
                    raise HTTPException(status_code=400, detail="O Google não confirmou o e-mail desta conta.")
                return str(body.get("email") or ""), str(body.get("sub") or body.get("email") or "")
            if provider == "microsoft":
                response = await client.get(_MICROSOFT_USERINFO)
                body = response.json() if response.status_code < 400 else {}
                email = str(body.get("email") or body.get("preferred_username") or "")
                if response.status_code >= 400 or not email:
                    raise HTTPException(status_code=400, detail="A Microsoft não devolveu um e-mail utilizável.")
                return email, str(body.get("sub") or email)
            if provider == "yahoo":
                response = await client.get(_YAHOO_USERINFO)
                body = response.json() if response.status_code < 400 else {}
                email = str(body.get("email") or body.get("preferred_username") or "")
                if response.status_code >= 400 or not email or body.get("email_verified") is not True:
                    raise HTTPException(status_code=400, detail="O Yahoo não confirmou o e-mail desta conta.")
                return email, str(body.get("sub") or email)
            if provider == "github":
                user_response = await client.get(_GITHUB_USER)
                email_response = await client.get(_GITHUB_EMAILS)
                if user_response.status_code >= 400 or email_response.status_code >= 400:
                    raise HTTPException(status_code=400, detail="O GitHub não confirmou a identidade desta conta.")
                emails = email_response.json()
                verified = [item for item in emails if item.get("verified") and item.get("email")]
                primary = next((item for item in verified if item.get("primary")), verified[0] if verified else None)
                if primary is None:
                    raise HTTPException(status_code=400, detail="O GitHub não possui e-mail verificado disponível.")
                user_body = user_response.json()
                return str(primary["email"]), str(user_body.get("id") or primary["email"])
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Falha ao consultar a identidade externa.") from exc
    raise HTTPException(status_code=404, detail="Provedor de login não suportado.")


@router.get("/providers")
def providers() -> dict[str, list[dict[str, Any]]]:
    catalog = [
        ("google", "Google"),
        ("microsoft", "Microsoft"),
        ("apple", "Apple"),
        ("github", "GitHub"),
    ]
    return {"providers": [{"id": key, "label": label, "enabled": _configured(key)} for key, label in catalog]}


@router.get("/{provider}/start")
def start(provider: str) -> RedirectResponse:
    provider = provider.lower().strip()
    if provider not in _SUPPORTED:
        raise HTTPException(status_code=404, detail="Provedor de login não suportado.")
    if not _configured(provider):
        raise HTTPException(status_code=503, detail="Este provedor ainda não está configurado no CorVIA.")
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    response = RedirectResponse(url=_auth_url(provider, state, nonce), status_code=302)
    _set_flow_cookies(response, provider, state, nonce)
    return response


@router.api_route("/{provider}/callback", methods=["GET", "POST"])
async def callback(provider: str, request: Request, db: Session = Depends(get_db)) -> RedirectResponse:
    provider = provider.lower().strip()
    if provider not in _SUPPORTED:
        return _login_error("unsupported_provider", provider)
    if request.method == "POST":
        form = await request.form()
        code = str(form.get("code") or "")
        state = str(form.get("state") or "")
        provider_error = str(form.get("error") or "")
    else:
        code = request.query_params.get("code") or ""
        state = request.query_params.get("state") or ""
        provider_error = request.query_params.get("error") or ""

    expected_state = request.cookies.get(_STATE_COOKIE) or ""
    expected_nonce = request.cookies.get(_NONCE_COOKIE) or ""
    expected_provider = request.cookies.get(_PROVIDER_COOKIE) or ""
    if provider_error:
        return _login_error("provider_denied", provider)
    if not code or not state or not expected_state or not expected_nonce:
        return _login_error("invalid_callback", provider)
    if expected_provider != provider or not secrets.compare_digest(state, expected_state):
        return _login_error("invalid_state", provider)

    try:
        token = await _exchange(provider, code)
        email, _subject = await _identity(provider, token, expected_nonce)
    except HTTPException:
        return _login_error("identity_failed", provider)

    user = _valid_user(db, email)
    if user is None:
        return _login_error("account_not_linked", provider)

    response = RedirectResponse(url=f"/?login_social={provider}", status_code=303)
    gravar_cookie_sessao(response, create_access_token(user.email, scope="app"))
    _clear_flow_cookies(response)
    return response
