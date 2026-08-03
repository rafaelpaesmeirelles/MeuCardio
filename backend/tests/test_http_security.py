from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from app.core.http_security import (
    HttpSecurityMiddleware,
    _normalizar_origem,
    _regra_para,
)
from app.core.security import AUTH_COOKIE_NAME


class FakeRedis:
    def __init__(self) -> None:
        self.counts: dict[str, int] = {}
        self.windows: dict[str, int] = {}

    async def eval(self, _script, _numkeys, key, window_seconds):
        self.counts[key] = self.counts.get(key, 0) + 1
        self.windows[key] = int(window_seconds)
        return [self.counts[key], self.windows[key]]


class FailingRedis:
    async def eval(self, *_args, **_kwargs):
        raise OSError("redis indisponível")


async def ok(_request: Request):
    return JSONResponse({"ok": True})


def _app(redis_client=None) -> Starlette:
    app = Starlette(
        routes=[
            Route("/write", ok, methods=["POST"]),
            Route("/api/auth/sessao", ok, methods=["POST"]),
            Route("/api/documentos-publicos/{token}", ok, methods=["GET"]),
            Route("/api/ai/perguntar", ok, methods=["POST"]),
        ]
    )
    app.add_middleware(
        HttpSecurityMiddleware,
        force_enabled=True,
        redis_client=redis_client or FakeRedis(),
    )
    return app


def test_normaliza_origem_sem_caminho_e_porta_padrao():
    assert _normalizar_origem("https://CORVIA.med.br/qualquer") == "https://corvia.med.br"
    assert _normalizar_origem("https://corvia.med.br:443") == "https://corvia.med.br"
    assert _normalizar_origem("http://localhost:5173") == "http://localhost:5173"
    assert _normalizar_origem("null") is None
    assert _normalizar_origem("javascript:alert(1)") is None


def test_cookie_rejeita_origem_cruzada_em_mutacao():
    with TestClient(_app()) as client:
        client.cookies.set(AUTH_COOKIE_NAME, "jwt-falso")
        response = client.post("/write", headers={"Origin": "https://evil.example"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Origem da requisição não autorizada."


def test_cookie_aceita_origem_do_host_atual():
    with TestClient(_app()) as client:
        client.cookies.set(AUTH_COOKIE_NAME, "jwt-falso")
        response = client.post("/write", headers={"Origin": "http://testserver"})
    assert response.status_code == 200


def test_cookie_sem_origem_e_rejeitado_mas_bearer_externo_permanece_compativel():
    with TestClient(_app()) as client:
        client.cookies.set(AUTH_COOKIE_NAME, "jwt-falso")
        blocked = client.post("/write")
        client.cookies.clear()
        bearer = client.post("/write", headers={"Authorization": "Bearer externo"})
    assert blocked.status_code == 403
    assert bearer.status_code == 200


def test_login_de_navegador_rejeita_login_csrf():
    with TestClient(_app()) as client:
        response = client.post(
            "/api/auth/sessao",
            headers={
                "Origin": "https://evil.example",
                "Sec-Fetch-Site": "cross-site",
                "X-Forwarded-For": "203.0.113.10",
            },
        )
    assert response.status_code == 403


def test_login_tem_limite_compartilhado_por_ip():
    redis = FakeRedis()
    headers = {"X-Forwarded-For": "203.0.113.20"}
    with TestClient(_app(redis)) as client:
        responses = [client.post("/api/auth/sessao", headers=headers) for _ in range(10)]
        blocked = client.post("/api/auth/sessao", headers=headers)
        other_ip = client.post(
            "/api/auth/sessao",
            headers={"X-Forwarded-For": "203.0.113.21"},
        )

    assert all(response.status_code == 200 for response in responses)
    assert responses[0].headers["X-RateLimit-Limit"] == "10"
    assert responses[-1].headers["X-RateLimit-Remaining"] == "0"
    assert blocked.status_code == 429
    assert blocked.headers["Retry-After"] == "300"
    assert other_ip.status_code == 200


def test_endpoint_sensivel_falha_controladamente_sem_redis():
    with TestClient(_app(FailingRedis())) as client:
        response = client.post(
            "/api/auth/sessao",
            headers={"X-Forwarded-For": "203.0.113.30"},
        )
    assert response.status_code == 503
    assert response.headers["Retry-After"] == "5"


def test_regras_cobrem_superficies_sensiveis():
    assert _regra_para("POST", "/api/auth/login").name == "login"
    assert _regra_para("POST", "/api/auth/esqueci-senha").name == "recuperacao"
    assert _regra_para("GET", "/api/documentos-publicos/token").name == "documento-publico"
    assert _regra_para("POST", "/api/ai/perguntar").name == "ia"
    assert _regra_para("POST", "/api/round/patients/1/ai-assist").name == "ia"
    assert _regra_para("GET", "/api/health") is None


def test_proxy_de_producao_define_politicas_essenciais():
    repo_root = Path(__file__).resolve().parents[2]
    caddy = (repo_root / "infra" / "Caddyfile").read_text(encoding="utf-8")
    assert "Content-Security-Policy" in caddy
    assert "frame-ancestors 'none'" in caddy
    assert "object-src 'none'" in caddy
    assert "Permissions-Policy" in caddy
    assert "Strict-Transport-Security" in caddy
    assert "-Server" in caddy
