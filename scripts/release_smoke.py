#!/usr/bin/env python3
"""Smoke test de release contra uma API Corvia em execução.

Usa apenas a biblioteca padrão para poder rodar na CI e no servidor depois do
deploy, sem instalar um cliente de testes separado.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from typing import Any


class SmokeFailure(RuntimeError):
    pass


class ApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        parsed = urllib.parse.urlsplit(self.base_url)
        self.origin = f"{parsed.scheme}://{parsed.netloc}"
        self.cookies = CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookies))

    def request(
        self,
        method: str,
        path: str,
        *,
        form: dict[str, str] | None = None,
        expected: tuple[int, ...] = (200,),
    ) -> tuple[int, Any, urllib.response.addinfourl]:
        data = None
        headers = {"Accept": "application/json"}
        if method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
            # O smoke representa a interface web real e, portanto, envia a
            # origem do próprio ambiente nas operações que mudam estado.
            headers["Origin"] = self.origin
        if form is not None:
            data = urllib.parse.urlencode(form).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            response = self.opener.open(request, timeout=5)
            status = response.status
            raw = response.read()
        except urllib.error.HTTPError as error:
            response = error
            status = error.code
            raw = error.read()
        except OSError as error:
            raise SmokeFailure(f"Falha de conexão em {method} {path}: {error}") from error

        if status not in expected:
            body = raw.decode("utf-8", errors="replace")
            raise SmokeFailure(f"{method} {path}: esperado {expected}, recebido {status}: {body}")

        if not raw:
            payload: Any = None
        else:
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as error:
                raise SmokeFailure(f"{method} {path}: resposta não é JSON válido") from error
        return status, payload, response


def wait_for_api(client: ApiClient, timeout_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error = "API ainda não respondeu"
    while time.monotonic() < deadline:
        try:
            _, payload, _ = client.request("GET", "/api/health")
            if payload == {"status": "ok"}:
                return
            last_error = f"liveness inesperado: {payload!r}"
        except SmokeFailure as error:
            last_error = str(error)
        time.sleep(1)
    raise SmokeFailure(f"API não ficou disponível em {timeout_seconds}s: {last_error}")


def run(args: argparse.Namespace) -> None:
    client = ApiClient(args.base_url)
    wait_for_api(client, args.timeout)

    _, ready, _ = client.request("GET", "/api/ready")
    if ready.get("status") != "ready" or ready.get("components") != {"database": "ok", "redis": "ok"}:
        raise SmokeFailure(f"readiness inesperado: {ready!r}")

    client.request("GET", "/api/auth/me", expected=(401,))

    _, login, response = client.request(
        "POST",
        "/api/auth/sessao",
        form={"username": args.email, "password": args.password},
    )
    # Checagem por campo, não por igualdade do dict inteiro: a resposta
    # ganhou o campo `persistent` (09/08/2026, "permanecer conectado") sem
    # que este smoke fosse atualizado — igualdade estrita quebrava o release
    # flow da CI a cada login bem-sucedido, mesmo com o backend saudável.
    # Achado de auditoria, issue #52 subfase 8.
    if login.get("authenticated") is not True:
        raise SmokeFailure(f"resposta de login inesperada: {login!r}")

    set_cookie = response.headers.get("Set-Cookie", "")
    cookie_lower = set_cookie.lower()
    required_cookie_attributes = {
        "corvia_session=": "corvia_session=",
        "httponly": "HttpOnly",
        # SameSite=Lax, não Strict, desde a correção do bug de reconexão
        # OAuth de 09/08/2026 (Strict retinha o cookie no retorno do
        # consentimento Google/Microsoft, devolvendo o médico à tela de
        # login no meio do fluxo — ver app/core/security.py,
        # gravar_cookie_sessao()). Achado de auditoria, issue #52 subfase 8:
        # este smoke ainda exigia o valor antigo.
        "samesite=lax": "SameSite=Lax",
    }
    missing = [label for attribute, label in required_cookie_attributes.items() if attribute not in cookie_lower]
    if args.expect_secure_cookie and "secure" not in cookie_lower:
        missing.append("Secure")
    if missing:
        raise SmokeFailure(f"cookie de sessão sem atributos obrigatórios: {', '.join(missing)}")

    _, profile, _ = client.request("GET", "/api/auth/me")
    if profile.get("email") != args.email.lower():
        raise SmokeFailure(f"sessão autenticou identidade inesperada: {profile.get('email')!r}")

    _, logout, _ = client.request("POST", "/api/auth/sair")
    if logout != {"authenticated": False}:
        raise SmokeFailure(f"resposta de logout inesperada: {logout!r}")
    client.request("GET", "/api/auth/me", expected=(401,))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Valida liveness, readiness e ciclo real de sessão web.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--expect-secure-cookie", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    try:
        run(parse_args())
    except SmokeFailure as error:
        print(f"SMOKE FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
    print("Release smoke aprovado: health, readiness, sessão HttpOnly e logout.")
