"""Dispensas KYC individuais de Convidado — backend é a fonte da verdade."""
import io

import pytest
from PIL import Image

from app.core.config import settings
from app.models.kyc import KycVerification


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def _diretorio_kyc(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "kyc_dir", str(tmp_path))


def _jpeg(cor: tuple[int, int, int]) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color=cor).save(buf, format="JPEG")
    return buf.getvalue()


def _tornar_convidado(db, user):
    user.convidado = True
    user.investidor = False
    db.commit()
    db.refresh(user)


def test_admin_configura_seis_dispensas_e_backend_aprova_sem_upload(client, db, criar_usuario):
    _, token_admin = criar_usuario(email="admin-waiver@teste.local", role="admin")
    user, token = criar_usuario(email="guest-all-waived@teste.local")
    _tornar_convidado(db, user)

    waivers = {
        "professional_front": True,
        "professional_back": True,
        "personal_front": True,
        "personal_back": True,
        "personal_digital": True,
        "selfie": True,
    }
    resp = client.put(
        f"/api/admin/users/{user.id}/kyc-waivers",
        json=waivers,
        headers=_headers(token_admin),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["waivers"] == waivers
    assert resp.json()["kyc_status"] == "aprovado"

    registro = db.query(KycVerification).filter(KycVerification.owner_id == user.id).one()
    assert registro.selfie is None
    assert registro.doc_profissional_frente is None
    assert registro.status == "aprovado"

    me = client.get("/api/auth/me", headers=_headers(token))
    assert me.status_code == 200
    assert me.json()["kyc_required"] is False


def test_dispensa_parcial_permite_omitir_somente_campos_dispensados(client, db, criar_usuario):
    _, token_admin = criar_usuario(email="admin-waiver2@teste.local", role="admin")
    user, token = criar_usuario(email="guest-partial-waived@teste.local")
    _tornar_convidado(db, user)

    waivers = {
        "professional_front": True,
        "professional_back": False,
        "personal_front": True,
        "personal_back": False,
        "personal_digital": False,
        "selfie": True,
    }
    assert client.put(
        f"/api/admin/users/{user.id}/kyc-waivers", json=waivers, headers=_headers(token_admin)
    ).status_code == 200

    files = {
        "doc_profissional_verso": ("prof-verso.jpg", _jpeg((10, 20, 30)), "image/jpeg"),
        "doc_pessoal_verso": ("pessoal-verso.jpg", _jpeg((40, 50, 60)), "image/jpeg"),
    }
    resp = client.post("/api/kyc/submeter", files=files, headers=_headers(token))
    assert resp.status_code == 201, resp.text
    assert resp.json()["status"] == "aprovado"
    assert resp.json()["liberado"] is True
    assert resp.json()["waivers"] == waivers


def test_sem_dispensa_documento_profissional_e_selfie_continuam_obrigatorios(client, db, criar_usuario):
    user, token = criar_usuario(email="guest-no-waiver@teste.local")
    _tornar_convidado(db, user)

    apenas_pessoal = {
        "doc_pessoal_digital": ("doc.pdf", b"%PDF-1.4\n%%EOF", "application/pdf"),
    }
    resp = client.post("/api/kyc/submeter", files=apenas_pessoal, headers=_headers(token))
    assert resp.status_code == 422
    assert "profissional" in resp.json()["detail"].lower()


def test_dispensa_personal_digital_satisfaz_via_pessoal_sem_upload_pessoal(client, db, criar_usuario):
    _, token_admin = criar_usuario(email="admin-waiver3@teste.local", role="admin")
    user, token = criar_usuario(email="guest-digital-waived@teste.local")
    _tornar_convidado(db, user)

    waivers = {
        "professional_front": False,
        "professional_back": False,
        "personal_front": False,
        "personal_back": False,
        "personal_digital": True,
        "selfie": False,
    }
    client.put(f"/api/admin/users/{user.id}/kyc-waivers", json=waivers, headers=_headers(token_admin))
    files = {
        "doc_profissional_frente": ("pf.jpg", _jpeg((1, 2, 3)), "image/jpeg"),
        "doc_profissional_verso": ("pv.jpg", _jpeg((4, 5, 6)), "image/jpeg"),
        "selfie": ("selfie.jpg", _jpeg((7, 8, 9)), "image/jpeg"),
    }
    resp = client.post("/api/kyc/submeter", files=files, headers=_headers(token))
    assert resp.status_code == 201, resp.text
    assert resp.json()["status"] == "aprovado"


def test_retirar_dispensa_reabre_gate_quando_documento_esta_ausente(client, db, criar_usuario):
    _, token_admin = criar_usuario(email="admin-waiver4@teste.local", role="admin")
    user, token = criar_usuario(email="guest-reopen@teste.local")
    _tornar_convidado(db, user)

    todas = {campo: True for campo in (
        "professional_front", "professional_back", "personal_front",
        "personal_back", "personal_digital", "selfie",
    )}
    client.put(f"/api/admin/users/{user.id}/kyc-waivers", json=todas, headers=_headers(token_admin))
    assert client.get("/api/auth/me", headers=_headers(token)).json()["kyc_required"] is False

    todas["selfie"] = False
    resp = client.put(
        f"/api/admin/users/{user.id}/kyc-waivers", json=todas, headers=_headers(token_admin)
    )
    assert resp.status_code == 200
    assert resp.json()["kyc_status"] == "reenvio_solicitado"
    assert client.get("/api/auth/me", headers=_headers(token)).json()["kyc_required"] is True


def test_dispensas_nao_podem_ser_aplicadas_a_conta_normal_ou_investidor(client, db, criar_usuario):
    _, token_admin = criar_usuario(email="admin-waiver5@teste.local", role="admin")
    normal, _ = criar_usuario(email="normal-waiver@teste.local")
    vazio = {campo: False for campo in (
        "professional_front", "professional_back", "personal_front",
        "personal_back", "personal_digital", "selfie",
    )}
    r_normal = client.put(
        f"/api/admin/users/{normal.id}/kyc-waivers", json=vazio, headers=_headers(token_admin)
    )
    assert r_normal.status_code == 409

    investidor, _ = criar_usuario(email="investidor-waiver@teste.local")
    investidor.investidor = True
    db.commit()
    r_investidor = client.put(
        f"/api/admin/users/{investidor.id}/kyc-waivers", json=vazio, headers=_headers(token_admin)
    )
    assert r_investidor.status_code == 409
