"""Rotas de /api/kyc (submeter/status) e /api/admin/kyc (fila, documento,
aprovar/rejeitar) — Trabalho 11 (06/08/2026), com hardening de segurança
(admin-only explícito + audit log completo) na issue #52.
"""
import io

import pytest
from PIL import Image

from app.core.config import settings
from app.models.audit import AuditLog
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


# ---------------------------------------------------------------------------
# Hardening de segurança (issue #52) — admin-only explícito em TODA rota
# sensível de KYC, não só na listagem, e audit log completo.
# ---------------------------------------------------------------------------

def test_admin_ve_documento_bloqueado_para_nao_admin(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    _, token_admin = criar_usuario(email="admin-doc-403@teste.local", role="admin")
    client.post("/api/kyc/submeter", files=_arquivos(), headers=_headers(token))
    item_id = client.get("/api/admin/kyc", headers=_headers(token_admin)).json()[0]["id"]

    # Outro médico comum (não o dono da verificação, não admin) tenta ver.
    _, token_outro = criar_usuario(email="medico-outro-403@teste.local")
    resposta = client.get(f"/api/admin/kyc/{item_id}/documento/selfie", headers=_headers(token_outro))
    assert resposta.status_code == 403

    # O próprio titular da verificação também não pode usar a rota admin
    # para ver o próprio documento — a rota é administrativa, não de posse.
    resposta_titular = client.get(f"/api/admin/kyc/{item_id}/documento/selfie", headers=_headers(token))
    assert resposta_titular.status_code == 403


def test_admin_aprova_bloqueado_para_nao_admin(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    _, token_admin = criar_usuario(email="admin-aprova-403@teste.local", role="admin")
    client.post("/api/kyc/submeter", files=_arquivos(), headers=_headers(token))
    item_id = client.get("/api/admin/kyc", headers=_headers(token_admin)).json()[0]["id"]

    resposta = client.post(f"/api/admin/kyc/{item_id}/aprovar", json={}, headers=_headers(token))
    assert resposta.status_code == 403


def test_admin_rejeita_bloqueado_para_nao_admin(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    _, token_admin = criar_usuario(email="admin-rejeita-403@teste.local", role="admin")
    client.post("/api/kyc/submeter", files=_arquivos(), headers=_headers(token))
    item_id = client.get("/api/admin/kyc", headers=_headers(token_admin)).json()[0]["id"]

    resposta = client.post(
        f"/api/admin/kyc/{item_id}/rejeitar", json={"nota": "x"}, headers=_headers(token),
    )
    assert resposta.status_code == 403


def test_submissao_gera_audit_log_sem_bytes_do_documento(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post("/api/kyc/submeter", files=_arquivos(), headers=_headers(token))
    assert resposta.status_code == 201, resposta.text

    log = (
        db.query(AuditLog)
        .filter(AuditLog.action == "kyc_submissao", AuditLog.user_id == user.id)
        .first()
    )
    assert log is not None
    assert log.entity == "kyc_verifications"
    assert log.detail.get("owner_id") == user.id
    # Nunca bytes/base64 do documento no detalhe da auditoria.
    detalhe_serializado = str(log.detail)
    assert "\\xff\\xd8\\xff" not in detalhe_serializado
    assert len(detalhe_serializado) < 500


def test_reenvio_gera_audit_log_de_reenvio_e_de_exclusao_dos_arquivos_antigos(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    client.post("/api/kyc/submeter", files=_arquivos(), headers=_headers(token))

    resposta = client.post("/api/kyc/submeter", files=_arquivos(), headers=_headers(token))
    assert resposta.status_code == 201, resposta.text

    log_reenvio = (
        db.query(AuditLog)
        .filter(AuditLog.action == "kyc_reenvio", AuditLog.user_id == user.id)
        .first()
    )
    assert log_reenvio is not None

    log_delete = (
        db.query(AuditLog)
        .filter(AuditLog.action == "kyc_delete", AuditLog.user_id == user.id)
        .first()
    )
    assert log_delete is not None
    assert log_delete.detail.get("motivo") == "reenvio_substituiu_arquivos_anteriores"
    # 5 arquivos na primeira submissão (sem doc_pessoal_digital, ver _arquivos()).
    assert log_delete.detail.get("quantidade") == 5


def test_primeira_submissao_nao_gera_audit_log_de_reenvio(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    client.post("/api/kyc/submeter", files=_arquivos(), headers=_headers(token))

    assert db.query(AuditLog).filter(AuditLog.action == "kyc_reenvio").first() is None
    assert db.query(AuditLog).filter(AuditLog.action == "kyc_delete").first() is None
