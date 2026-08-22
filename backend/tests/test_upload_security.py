import io
import zipfile
from pathlib import Path

import pytest
from PIL import Image
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from app.core.course_uploads import (
    CourseUploadSecurityMiddleware,
    is_course_upload,
    validate_course_file,
)
from app.core.uploads import (
    UploadRejected,
    UploadSecurityMiddleware,
    atomic_write_bytes,
    policy_for,
    safe_filename,
    validate_file,
)


class FakeRedis:
    def __init__(self) -> None:
        self.counts: dict[str, int] = {}

    async def eval(self, _script, _numkeys, key, window_seconds):
        self.counts[key] = self.counts.get(key, 0) + 1
        return [self.counts[key], int(window_seconds)]


class FailingRedis:
    async def eval(self, *_args, **_kwargs):
        raise OSError("redis indisponível")


async def echo_upload(request: Request):
    form = await request.form()
    upload = form["arquivo"]
    data = await upload.read()
    return JSONResponse({"filename": upload.filename, "size": len(data)})


def _app(redis=None) -> Starlette:
    shared_redis = redis or FakeRedis()
    app = Starlette(
        routes=[
            Route("/api/auth/me/foto", echo_upload, methods=["POST"]),
            Route("/api/auth/me/logo", echo_upload, methods=["POST"]),
            Route("/api/pedidos/{pedido_id:int}/exame", echo_upload, methods=["POST"]),
            Route("/api/email/mensagens/anexos", echo_upload, methods=["POST"]),
            Route("/api/cursos/admin/{slug}/material", echo_upload, methods=["POST"]),
        ]
    )
    app.add_middleware(
        UploadSecurityMiddleware,
        force_enabled=True,
        redis_client=shared_redis,
    )
    app.add_middleware(
        CourseUploadSecurityMiddleware,
        force_enabled=True,
        redis_client=shared_redis,
    )
    return app


def _png(width: int = 4, height: int = 4) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (width, height), color=(10, 20, 30)).save(output, format="PNG")
    return output.getvalue()


def _docx() -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr("word/document.xml", "<document />")
    return output.getvalue()


def test_upload_valido_e_reproduzido_para_o_endpoint():
    data = _png()
    with TestClient(_app()) as client:
        response = client.post(
            "/api/auth/me/foto",
            files={"arquivo": ("foto.png", data, "image/png")},
        )
    assert response.status_code == 200
    assert response.json() == {"filename": "foto.png", "size": len(data)}


def test_magic_bytes_sem_imagem_real_sao_rejeitados():
    with TestClient(_app()) as client:
        response = client.post(
            "/api/auth/me/logo",
            files={"arquivo": ("logo.png", b"\x89PNG\r\n\x1a\nconteudo-falso", "image/png")},
        )
    assert response.status_code == 422
    assert "corrompida" in response.json()["detail"]


def test_limite_e_aplicado_antes_do_router_ler_o_arquivo():
    oversized = b"x" * (3 * 1024 * 1024 + 1)
    with TestClient(_app()) as client:
        response = client.post(
            "/api/auth/me/foto",
            files={"arquivo": ("foto.jpg", oversized, "image/jpeg")},
        )
    assert response.status_code == 413


def test_pdf_clinico_com_javascript_e_rejeitado():
    pdf = b"%PDF-1.4\n1 0 obj<</JavaScript 2 0 R>>endobj\n%%EOF"
    with TestClient(_app()) as client:
        response = client.post(
            "/api/pedidos/42/exame",
            files={"arquivo": ("ecg.pdf", pdf, "application/pdf")},
        )
    assert response.status_code == 422
    assert "scripts" in response.json()["detail"]


def test_anexo_executavel_e_rejeitado_e_docx_valido_e_aceito():
    with TestClient(_app()) as client:
        blocked = client.post(
            "/api/email/mensagens/anexos",
            files={"arquivo": ("programa.exe", b"MZ" + b"x" * 100, "application/octet-stream")},
        )
        allowed = client.post(
            "/api/email/mensagens/anexos",
            files={"arquivo": ("relatorio.docx", _docx(), "application/octet-stream")},
        )
    assert blocked.status_code == 422
    assert allowed.status_code == 200


def test_material_de_curso_tem_politica_propria():
    material = _docx()
    with TestClient(_app()) as client:
        allowed = client.post(
            "/api/cursos/admin/cardiologia/material",
            files={"arquivo": ("apostila.docx", material, "application/octet-stream")},
        )
        blocked = client.post(
            "/api/cursos/admin/cardiologia/material",
            files={"arquivo": ("notas.txt", b"conteudo", "text/plain")},
        )
    assert allowed.status_code == 200
    assert allowed.json() == {"filename": "apostila.docx", "size": len(material)}
    assert blocked.status_code == 422
    assert "Material de curso" in blocked.json()["detail"]


def test_material_de_curso_rejeita_macro():
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr("word/document.xml", "<document />")
        archive.writestr("word/vbaProject.bin", b"macro")
    with pytest.raises(UploadRejected, match="macro"):
        validate_course_file(output.getvalue(), "apostila.docx")


def test_documento_ooxml_com_macro_e_rejeitado():
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr("word/document.xml", "<document />")
        archive.writestr("word/vbaProject.bin", b"macro")
    with pytest.raises(UploadRejected, match="macro"):
        validate_file(output.getvalue(), "laudo.docx", "email")


def test_nome_de_arquivo_nao_aceita_path_header_ou_controle():
    assert safe_filename("Laudo João 2026.pdf") == "Laudo João 2026.pdf"
    for unsafe in ("../../etc/passwd", "arquivo\\malicioso.pdf", 'x".pdf', "x\r\nInjected.pdf"):
        with pytest.raises(UploadRejected):
            safe_filename(unsafe)


def test_redis_indisponivel_bloqueia_upload_sensivel():
    with TestClient(_app(FailingRedis())) as client:
        response = client.post(
            "/api/auth/me/foto",
            files={"arquivo": ("foto.png", _png(), "image/png")},
        )
    assert response.status_code == 503
    assert response.headers["Retry-After"] == "5"


def test_rate_limit_de_upload_e_compartilhado_por_cliente():
    redis = FakeRedis()
    headers = {"X-Forwarded-For": "203.0.113.80"}
    with TestClient(_app(redis)) as client:
        for _ in range(20):
            response = client.post(
                "/api/auth/me/foto",
                headers=headers,
                files={"arquivo": ("foto.png", _png(), "image/png")},
            )
            assert response.status_code == 200
        blocked = client.post(
            "/api/auth/me/foto",
            headers=headers,
            files={"arquivo": ("foto.png", _png(), "image/png")},
        )
        other_client = client.post(
            "/api/auth/me/foto",
            headers={"X-Forwarded-For": "203.0.113.81"},
            files={"arquivo": ("foto.png", _png(), "image/png")},
        )
    assert blocked.status_code == 429
    assert blocked.headers["Retry-After"] == "600"
    assert other_client.status_code == 200


def test_escrita_atomica_publica_apenas_arquivo_final(tmp_path: Path):
    destination = atomic_write_bytes(tmp_path, "arquivo.bin", b"conteudo", mode=0o600)
    assert destination.read_bytes() == b"conteudo"
    assert oct(destination.stat().st_mode & 0o777) == "0o600"
    assert not list(tmp_path.glob(".upload-*.tmp"))


def test_inventario_de_rotas_upload_exige_politica_central():
    api_dir = Path(__file__).resolve().parents[1] / "app" / "api"
    upload_modules = {
        path.name
        for path in api_dir.glob("*.py")
        if "UploadFile" in path.read_text(encoding="utf-8")
    }
    assert upload_modules == {
        "auth.py",
        "email.py",
        "partner_courses.py",
        "patient_profiles.py",
        "service_orders.py",
        # Trabalho 7 (assinatura.py, certificado A1) e Trabalho 11 (kyc.py,
        # documento/selfie) — os dois já fazem leitura limitada por tamanho
        # (`await arquivo.read(LIMITE + 1)`) e validação de conteúdo real
        # (PKCS#12 genuíno via `certificado_a1.analisar()`; imagem/PDF real
        # via `core.uploads.validate_file()`), só que fora do registro
        # `policy_for()` — esse registro é para o subconjunto de rotas que
        # também precisam do corte de tamanho na camada ASGI, antes do
        # FastAPI montar o multipart; nenhum dos dois exige isso.
        "assinatura.py",
        "kyc.py",
        # Trabalho 14 (06/08/2026): upload do PDF assinado de volta pelo
        # fluxo manual do Assinador ITI (.../assinatura-externa, em
        # receituario.py e documents.py) — mesmo padrão de assinatura.py/
        # kyc.py, leitura capada (TAMANHO_MAXIMO_PDF_ASSINADO + 1) e
        # validação de conteúdo real (validate_file(), depois a assinatura
        # digital embutida é conferida de verdade em verificacao_pdf.py).
        "receituario.py",
        "documents.py",
        # Prescrição livre especial: a devolução do PDF assinado também usa
        # o fluxo externo existente, com leitura limitada a 15 MB + 1 byte,
        # validação real do PDF por validate_file() e conferência criptográfica
        # da assinatura antes da persistência. Não é upload genérico da app.
        "prescricao_especial.py",
    }

    assert policy_for("POST", "/api/auth/me/foto") is not None
    assert policy_for("POST", "/api/auth/me/logo") is not None
    assert policy_for("POST", "/api/pedidos/1/exame") is not None
    assert policy_for("POST", "/api/pacientes/1/ecgs") is not None
    assert policy_for("POST", "/api/email/mensagens/anexos") is not None
    assert is_course_upload("POST", "/api/cursos/admin/cardiologia/material")
    assert policy_for("GET", "/api/auth/me/foto") is None
    assert not is_course_upload("GET", "/api/cursos/admin/cardiologia/material")
