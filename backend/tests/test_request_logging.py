import json
import logging
import re

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core import request_logging
from app.core.request_logging import (
    JsonRequestFormatter,
    StructuredRequestLoggingMiddleware,
    current_request_id,
    normalize_path,
)


class CaptureHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def _capture_requests():
    handler = CaptureHandler()
    request_logging.logger.addHandler(handler)
    return handler


def test_request_id_is_propagated_and_unknown_path_is_normalized(client):
    handler = _capture_requests()
    try:
        response = client.get(
            "/api/nao-existe/123?token=segredo-na-query",
            headers={
                "X-Request-ID": "corr-frontend-1234",
                "Authorization": "Bearer segredo-no-header",
            },
        )
    finally:
        request_logging.logger.removeHandler(handler)

    assert response.status_code == 404
    assert response.headers["X-Request-ID"] == "corr-frontend-1234"
    assert handler.records

    record = handler.records[-1]
    assert record.request_id == "corr-frontend-1234"
    assert record.path == "/api/nao-existe/{id}"
    assert record.status_code == 404

    rendered = JsonRequestFormatter().format(record)
    assert "segredo-na-query" not in rendered
    assert "segredo-no-header" not in rendered
    assert "authorization" not in rendered.lower()
    assert current_request_id() is None


def test_invalid_request_id_is_replaced(client):
    response = client.get(
        "/api/nao-existe",
        headers={"X-Request-ID": "curto"},
    )

    generated = response.headers["X-Request-ID"]
    assert generated != "curto"
    assert re.fullmatch(r"[0-9a-f]{32}", generated)


def test_successful_health_probe_is_not_logged(client):
    handler = _capture_requests()
    try:
        response = client.get("/api/health")
    finally:
        request_logging.logger.removeHandler(handler)

    assert response.status_code == 200
    assert handler.records == []


def test_unhandled_error_returns_generic_response_and_structured_log():
    app = FastAPI()
    app.add_middleware(StructuredRequestLoggingMiddleware)

    @app.post("/boom/{patient_id}")
    def boom(patient_id: int):
        raise RuntimeError(f"dado sensível não deve sair: {patient_id}")

    handler = _capture_requests()
    try:
        with TestClient(app) as client:
            response = client.post(
                "/boom/987?cpf=30389435848",
                headers={
                    "X-Request-ID": "erro-controlado-123",
                    "Authorization": "Bearer jwt-super-secreto",
                },
                json={"nome": "Paciente Sigiloso"},
            )
    finally:
        request_logging.logger.removeHandler(handler)

    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "erro-controlado-123"
    assert response.json() == {
        "detail": "Erro interno. Informe o identificador ao suporte.",
        "request_id": "erro-controlado-123",
    }

    record = handler.records[-1]
    assert record.levelno == logging.ERROR
    assert record.path == "/boom/{patient_id}"
    assert record.error_type == "RuntimeError"

    payload = json.loads(JsonRequestFormatter().format(record))
    serialized = json.dumps(payload, ensure_ascii=False)
    assert "987" not in serialized
    assert "30389435848" not in serialized
    assert "Paciente Sigiloso" not in serialized
    assert "jwt-super-secreto" not in serialized
    assert "dado sensível" not in serialized


def test_normalize_path_masks_tokens_ids_uuid_and_email():
    assert normalize_path("/api/round/patients/123/notes") == (
        "/api/round/patients/{id}/notes"
    )
    assert normalize_path(
        "/api/items/550e8400-e29b-41d4-a716-446655440000"
    ) == "/api/items/{id}"
    assert normalize_path(
        "/api/documentos-publicos/abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG"
    ) == "/api/documentos-publicos/{token}"
    assert normalize_path("/api/contas/medico@teste.com") == (
        "/api/contas/{value}"
    )
