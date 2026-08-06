"""Rotas de /api/kyc (submeter/status) e /api/admin/kyc (fila, documento,
aprovar/rejeitar) — Trabalho 11 (06/08/2026).
"""
import io

import pytest
from PIL import Image

from app.core.config import settings
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


@pytest.fixture(autouse=True)
def _diretorio_kyc(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "kyc_dir", str(tmp_path))


def _jpeg(cor: tuple[int, int, int]) -> bytes:
    """`_verify_image` (core/uploads.py) decodifica de verdade com PIL —
    magic bytes soltos não bastam, precisa ser um JPEG genuíno."""
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color=cor).save(buf, format="JPEG")
    return buf.getvalue()


def _arquivos(**overrides):
    base = {
        "doc_profissional_frente": ("frente.jpg", _jpeg((255, 0, 0)), "image/jpeg"),
        "doc_profissional_verso": ("verso.jpg", _jpeg((0, 255, 0)), "image/jpeg"),
        "selfie": ("selfie.jpg", _jpeg((0, 0, 255)), "image/jpeg"),
        "doc_pessoal_frente": ("id-frente.jpg", _jpeg((255, 255, 0)), "image/jpeg"),
        "doc_pessoal_verso": ("id-verso.jpg", _jpeg((255, 0, 255)), "image/jpeg"),
    }
    base.update(overrides)
    return base


def test_status_sem_submissao(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.get("/api/kyc/status", headers=_headers(token))
    assert resposta.status_code == 200
    assert resposta.json() == {"status": None, "liberado": False}


def test_submeter_com_sucesso(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post("/api/kyc/submeter", files=_arquivos(), headers=_headers(token))
    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["status"] == "aguardando_revisao"
    assert resposta.json()["liberado"] is False


def test_submeter_sem_documento_profissional_e_422(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    arquivos = _arquivos()
    del arquivos["doc_profissional_frente"]
    resposta = client.post("/api/kyc/submeter", files=arquivos, headers=_headers(token))
    assert resposta.status_code == 422


def test_submeter_arquivo_invalido_e_422(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    arquivos = _arquivos(doc_profissional_frente=("frente.txt", b"nao e imagem nem pdf", "text/plain"))
    resposta = client.post("/api/kyc/submeter", files=arquivos, headers=_headers(token))
    assert resposta.status_code == 422


def test_status_apos_submeter(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    client.post("/api/kyc/submeter", files=_arquivos(), headers=_headers(token))
    resposta = client.get("/api/kyc/status", headers=_headers(token))
    assert resposta.json()["status"] == "aguardando_revisao"


def test_admin_lista_pendentes(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    _, token_admin = criar_usuario(email="admin-kyc-api@teste.local", role="admin")
    client.post("/api/kyc/submeter", files=_arquivos(), headers=_headers(token))

    resposta = client.get("/api/admin/kyc", headers=_headers(token_admin))
    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["user_id"] == user.id


def test_admin_lista_bloqueada_para_nao_admin(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.get("/api/admin/kyc", headers=_headers(token))
    assert resposta.status_code == 403


def test_admin_ve_documento(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    _, token_admin = criar_usuario(email="admin-doc@teste.local", role="admin")
    client.post("/api/kyc/submeter", files=_arquivos(), headers=_headers(token))
    item_id = client.get("/api/admin/kyc", headers=_headers(token_admin)).json()[0]["id"]

    resposta = client.get(f"/api/admin/kyc/{item_id}/documento/selfie", headers=_headers(token_admin))
    assert resposta.status_code == 200
    assert resposta.headers["content-type"] == "image/jpeg"
    assert resposta.content.startswith(b"\xff\xd8\xff")


def test_admin_ve_documento_inexistente_no_registro_e_404(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    _, token_admin = criar_usuario(email="admin-doc2@teste.local", role="admin")
    arquivos = _arquivos()
    del arquivos["doc_pessoal_frente"]
    del arquivos["doc_pessoal_verso"]
    arquivos["doc_pessoal_digital"] = ("doc.pdf", b"%PDF-1.4 conteudo\n%%EOF", "application/pdf")
    client.post("/api/kyc/submeter", files=arquivos, headers=_headers(token))
    item_id = client.get("/api/admin/kyc", headers=_headers(token_admin)).json()[0]["id"]

    resposta = client.get(f"/api/admin/kyc/{item_id}/documento/doc_pessoal_frente", headers=_headers(token_admin))
    assert resposta.status_code == 404


def test_admin_aprova_verificacao(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    _, token_admin = criar_usuario(email="admin-aprova@teste.local", role="admin")
    client.post("/api/kyc/submeter", files=_arquivos(), headers=_headers(token))
    item_id = client.get("/api/admin/kyc", headers=_headers(token_admin)).json()[0]["id"]

    resposta = client.post(f"/api/admin/kyc/{item_id}/aprovar", json={"nota": "tudo confere"}, headers=_headers(token_admin))
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "aprovado"

    status_assinante = client.get("/api/kyc/status", headers=_headers(token))
    assert status_assinante.json()["liberado"] is True


def test_admin_rejeita_verificacao_exige_nota(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    _, token_admin = criar_usuario(email="admin-rejeita@teste.local", role="admin")
    client.post("/api/kyc/submeter", files=_arquivos(), headers=_headers(token))
    item_id = client.get("/api/admin/kyc", headers=_headers(token_admin)).json()[0]["id"]

    sem_nota = client.post(f"/api/admin/kyc/{item_id}/rejeitar", json={}, headers=_headers(token_admin))
    assert sem_nota.status_code == 422

    com_nota = client.post(
        f"/api/admin/kyc/{item_id}/rejeitar", json={"nota": "foto ilegível"}, headers=_headers(token_admin),
    )
    assert com_nota.status_code == 200
    assert com_nota.json()["status"] == "rejeitado"

    status_assinante = client.get("/api/kyc/status", headers=_headers(token))
    assert status_assinante.json()["status"] == "rejeitado"
    assert status_assinante.json()["nota_revisao"] == "foto ilegível"
