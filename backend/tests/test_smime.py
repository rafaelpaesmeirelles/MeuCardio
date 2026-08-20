"""app/services/assinatura/smime.py — assinatura S/MIME do e-mail em si
(CMS/PKCS#7 detached), usando o mesmo certificado A1 do Trabalho 7.
Validado manualmente contra `openssl smime -verify` fora da suíte (ver
histórico da sessão) — aqui a conferência é estrutural: parseável,
`multipart/signed`, envelope correto, sem dependência de binário externo.
"""
import datetime
from email import message_from_bytes
from email.policy import default

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

from app.core.config import settings
from app.models.user import User
from app.services.assinatura import certificado_a1, smime


def _gerar_pfx(*, senha: str = "senha123", cn: str = "DR TESTE DA SILVA:12345678900") -> bytes:
    chave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nome = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    certificado = (
        x509.CertificateBuilder()
        .subject_name(nome).issuer_name(nome).public_key(chave.public_key())
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


def _usuario_com_certificado(db, criar_usuario) -> User:
    user, _ = criar_usuario(email="smime@teste.local")
    certificado_a1.salvar(db, user, _gerar_pfx(), "senha123", "AC Teste")
    db.commit()
    return user


def test_sem_certificado_levanta_smime_indisponivel(db, criar_usuario):
    user, _ = criar_usuario(email="sem-cert@teste.local")
    with pytest.raises(smime.SmimeIndisponivel):
        smime.montar_corpo_assinado(db, user, html="<p>oi</p>")


def test_preparar_assinante_devolve_metadados(db, criar_usuario):
    user = _usuario_com_certificado(db, criar_usuario)
    info = smime.preparar_assinante(db, user)
    assert info.titular_cn == "DR TESTE DA SILVA:12345678900"
    assert info.certificadora == "AC Teste"


def test_corpo_assinado_e_multipart_signed_valido(db, criar_usuario):
    user = _usuario_com_certificado(db, criar_usuario)
    corpo = smime.montar_corpo_assinado(db, user, html="<p>Documento anexo.</p>")
    msg = message_from_bytes(corpo)
    assert msg.get_content_type() == "multipart/signed"
    assert msg.get_param("protocol") == "application/x-pkcs7-signature"
    partes = list(msg.walk())
    # multipart/signed em si + o conteúdo original (multipart/alternative,
    # que por sua vez tem 2 sub-partes) + a assinatura = 5 no walk().
    tipos = [p.get_content_type() for p in partes]
    assert "application/x-pkcs7-signature" in tipos
    assert "text/html" in tipos


def test_mensagem_assinada_tem_envelope_correto_e_corpo_assinado_depois(db, criar_usuario):
    user = _usuario_com_certificado(db, criar_usuario)
    bruto = smime.montar_mensagem_assinada(
        db, user, remetente="medico@yahoo.com", para=["paciente@example.com"],
        cc=["copia@example.com"], assunto="Documento assinado", html="<p>Ola</p>",
    )
    msg = message_from_bytes(bruto)
    assert msg["From"] == "medico@yahoo.com"
    assert msg["To"] == "paciente@example.com"
    assert msg["Cc"] == "copia@example.com"
    assert msg["Subject"] == "Documento assinado"
    assert msg.get_content_type() == "multipart/signed"


def test_mensagem_assinada_preserva_bcc_unicode_e_rejeita_injecao(db, criar_usuario):
    user = _usuario_com_certificado(db, criar_usuario)
    bruto = smime.montar_mensagem_assinada(
        db, user, remetente="medico@corvia.med.br", para=["paciente@example.com"],
        cc=None, bcc=["auditoria@example.com"], assunto="Avaliação cardiológica", html="<p>Olá</p>",
    )
    msg = message_from_bytes(bruto, policy=default)
    assert str(msg["Bcc"]) == "auditoria@example.com"
    assert str(msg["Subject"]) == "Avaliação cardiológica"

    with pytest.raises(smime.SmimeIndisponivel, match="Cabeçalho"):
        smime.montar_mensagem_assinada(
            db, user, remetente="medico@corvia.med.br",
            para=["paciente@example.com\r\nBcc: invasor@x.com"],
            cc=None, assunto="Seguro", html="<p>Olá</p>",
        )
