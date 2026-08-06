"""Rotas de /api/assinatura — catálogo, certificadoras informativas, e o
ciclo completo de gestão do certificado A1 (upload/status/remover), Trabalho
7 (06/08/2026).
"""
import datetime

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

from app.core.config import settings
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _gerar_pfx(*, senha: str = "senha123", cn: str = "DR TESTE DA SILVA:12345678900") -> bytes:
    chave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nome = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    certificado = (
        x509.CertificateBuilder()
        .subject_name(nome)
        .issuer_name(nome)
        .public_key(chave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
        .sign(chave, hashes.SHA256())
    )
    return pkcs12.serialize_key_and_certificates(
        name=b"teste", key=chave, cert=certificado, cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(senha.encode()),
    )


@pytest.fixture(autouse=True)
def _diretorio_certificados(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "certificados_dir", str(tmp_path))


def test_listar_provedores_inclui_a1_arquivo_indisponivel_sem_certificado(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.get("/api/assinatura/provedores", headers=_headers(token))
    assert resposta.status_code == 200
    a1 = next(p for p in resposta.json() if p["codigo"] == "A1_ARQUIVO")
    assert a1["disponivel"] is False
    assert a1["nivel"] == "qualificada"


def test_provedores_em_nuvem_disponiveis_via_fluxo_manual_iti(client, db, criar_usuario):
    """Trabalho 14 (06/08/2026): VIDAAS e as demais clouds sem credencial
    comercial deixaram de ser "em breve" — passaram a ter o fluxo manual
    do Assinador ITI (o médico assina fora e reenvia), disponível sem
    nenhuma credencial. Substitui o teste antigo, que assumia recusa."""
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.get("/api/assinatura/provedores", headers=_headers(token))
    vidaas = next(p for p in resposta.json() if p["codigo"] == "VIDAAS")
    assert vidaas["disponivel"] is True
    assert vidaas["motivo"] is None


def test_listar_certificadoras_devolve_lista_nao_vazia(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.get("/api/assinatura/certificadoras", headers=_headers(token))
    assert resposta.status_code == 200
    assert len(resposta.json()) >= 3
    assert all("nome" in c and "site" in c for c in resposta.json())


def test_status_sem_certificado_conectado(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.get("/api/assinatura/certificado-a1", headers=_headers(token))
    assert resposta.status_code == 200
    assert resposta.json() == {"conectado": False}


def test_conectar_certificado_a1_com_sucesso(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    pfx = _gerar_pfx(cn="DR API TESTE:99988877766")
    resposta = client.post(
        "/api/assinatura/certificado-a1",
        files={"arquivo": ("certificado.pfx", pfx, "application/x-pkcs12")},
        data={"senha": "senha123", "certificadora": "Certisign"},
        headers=_headers(token),
    )
    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["titular_cn"] == "DR API TESTE:99988877766"
    assert resposta.json()["certificadora"] == "Certisign"


def test_conectar_com_senha_errada_e_422(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    pfx = _gerar_pfx(senha="certa")
    resposta = client.post(
        "/api/assinatura/certificado-a1",
        files={"arquivo": ("certificado.pfx", pfx, "application/x-pkcs12")},
        data={"senha": "errada"},
        headers=_headers(token),
    )
    assert resposta.status_code == 422


def test_conectar_com_arquivo_invalido_e_422(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/assinatura/certificado-a1",
        files={"arquivo": ("certificado.pfx", b"nao e certificado", "application/x-pkcs12")},
        data={"senha": "qualquer"},
        headers=_headers(token),
    )
    assert resposta.status_code == 422


def test_status_apos_conectar_mostra_dados_reais(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    pfx = _gerar_pfx(cn="DR STATUS:12312312312")
    client.post(
        "/api/assinatura/certificado-a1",
        files={"arquivo": ("certificado.pfx", pfx, "application/x-pkcs12")},
        data={"senha": "senha123"},
        headers=_headers(token),
    )
    resposta = client.get("/api/assinatura/certificado-a1", headers=_headers(token))
    assert resposta.json()["conectado"] is True
    assert resposta.json()["titular_cn"] == "DR STATUS:12312312312"


def test_a1_arquivo_fica_disponivel_apos_conectar(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    pfx = _gerar_pfx()
    client.post(
        "/api/assinatura/certificado-a1",
        files={"arquivo": ("certificado.pfx", pfx, "application/x-pkcs12")},
        data={"senha": "senha123"},
        headers=_headers(token),
    )
    resposta = client.get("/api/assinatura/provedores", headers=_headers(token))
    a1 = next(p for p in resposta.json() if p["codigo"] == "A1_ARQUIVO")
    assert a1["disponivel"] is True


def test_remover_certificado(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    pfx = _gerar_pfx()
    client.post(
        "/api/assinatura/certificado-a1",
        files={"arquivo": ("certificado.pfx", pfx, "application/x-pkcs12")},
        data={"senha": "senha123"},
        headers=_headers(token),
    )
    resposta = client.delete("/api/assinatura/certificado-a1", headers=_headers(token))
    assert resposta.status_code == 204
    status = client.get("/api/assinatura/certificado-a1", headers=_headers(token))
    assert status.json() == {"conectado": False}


def test_isolamento_entre_usuarios_na_api(client, db, criar_usuario):
    user1, token1 = criar_usuario()
    _subscribe(db, user1.id)
    user2, token2 = criar_usuario(email="outro-api@teste.local")
    _subscribe(db, user2.id)
    pfx = _gerar_pfx(cn="USER1 API:11111111111")
    client.post(
        "/api/assinatura/certificado-a1",
        files={"arquivo": ("certificado.pfx", pfx, "application/x-pkcs12")},
        data={"senha": "senha123"},
        headers=_headers(token1),
    )
    status_user2 = client.get("/api/assinatura/certificado-a1", headers=_headers(token2))
    assert status_user2.json() == {"conectado": False}
    provedores_user2 = client.get("/api/assinatura/provedores", headers=_headers(token2))
    a1_user2 = next(p for p in provedores_user2.json() if p["codigo"] == "A1_ARQUIVO")
    assert a1_user2["disponivel"] is False
