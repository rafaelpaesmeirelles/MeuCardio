import io
import json
import logging
import re

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from app.core.observability import (
    CorviaJsonFormatter,
    ObservabilityMiddleware,
    bind_request_id,
)
from app.models.audit import AuditLog


def _event_logger(stream: io.StringIO) -> logging.Logger:
    logger = logging.getLogger(f"test.observability.{id(stream)}")
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(CorviaJsonFormatter())
    logger.addHandler(handler)
    return logger


async def _ok(_request):
    return JSONResponse({"status": "ok"})


async def _boom(_request):
    raise RuntimeError("senha=segredo-absoluto cpf=123.456.789-00")


def _app(route: Route, stream: io.StringIO) -> Starlette:
    app = Starlette(routes=[route])
    app.add_middleware(ObservabilityMiddleware, event_logger=_event_logger(stream))
    return app


def _last_event(stream: io.StringIO) -> dict:
    lines = [line for line in stream.getvalue().splitlines() if line.strip()]
    return json.loads(lines[-1])


def test_request_id_e_template_da_rota_sem_token_ou_query():
    stream = io.StringIO()
    app = _app(Route("/api/documentos-publicos/{token}", _ok), stream)

    with TestClient(app) as client:
        response = client.get(
            "/api/documentos-publicos/token-clinico-secreto?cpf=12345678900",
            headers={"X-Request-ID": "corvia-test-123"},
        )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "corvia-test-123"
    event = _last_event(stream)
    assert event["event"] == "http_request_completed"
    assert event["route"] == "/api/documentos-publicos/{token}"
    assert event["request_id"] == "corvia-test-123"
    assert "token-clinico-secreto" not in stream.getvalue()
    assert "12345678900" not in stream.getvalue()


def test_request_id_invalido_e_substituido_por_identificador_opaco():
    stream = io.StringIO()
    app = _app(Route("/api/health", _ok), stream)

    with TestClient(app) as client:
        response = client.get("/api/health", headers={"X-Request-ID": "ruim com espaços"})

    generated = response.headers["X-Request-ID"]
    assert generated != "ruim com espaços"
    assert re.fullmatch(r"[0-9a-f]{32}", generated)
    assert _last_event(stream)["request_id"] == generated


def test_excecao_devolve_request_id_e_nao_expoe_mensagem_sensivel():
    stream = io.StringIO()
    app = _app(Route("/api/falha/{token}", _boom), stream)

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(
            "/api/falha/token-secreto",
            headers={"X-Request-ID": "erro-test-123"},
        )

    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "erro-test-123"
    assert response.json() == {"detail": "Erro interno. Informe o X-Request-ID ao suporte."}
    event = _last_event(stream)
    assert event["event"] == "http_request_failed"
    assert event["error_type"] == "RuntimeError"
    assert event["error_stack"]
    serialized = stream.getvalue()
    assert "segredo-absoluto" not in serialized
    assert "123.456.789-00" not in serialized
    assert "token-secreto" not in serialized


def test_formatter_ignora_campos_nao_aprovados():
    formatter = CorviaJsonFormatter()
    record = logging.LogRecord(
        name="teste",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="evento_seguro",
        args=(),
        exc_info=None,
    )
    record.event = "evento_seguro"
    record.password = "nao-pode-aparecer"
    record.authorization = "Bearer nao-pode-aparecer"

    output = formatter.format(record)
    assert "evento_seguro" in output
    assert "nao-pode-aparecer" not in output
    assert "authorization" not in output


def test_auditoria_recebe_request_id_do_contexto(db):
    with bind_request_id("audit-request-123"):
        audit = AuditLog(
            user_id=None,
            action="teste_observabilidade",
            entity="infra",
            detail={"resultado": "ok"},
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)

    assert audit.request_id == "audit-request-123"
