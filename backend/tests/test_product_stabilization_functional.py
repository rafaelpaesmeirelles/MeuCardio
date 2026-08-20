from __future__ import annotations

import datetime
import hashlib
import io

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from reportlab.pdfgen import canvas

from app.core.config import settings
from app.models.assinatura import DocumentoEmitido
from app.models.email_account import EmailAccount
from app.services import cofre, envio_documento_email, mail360
from app.services.assinatura import emissao, pdf_signer, validacao_publica


def _pfx(senha: str = "senha123") -> bytes:
    chave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nome = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "DR VALIDACAO FARMACIA:12345678900")])
    agora = datetime.datetime.now(datetime.timezone.utc)
    certificado = (
        x509.CertificateBuilder()
        .subject_name(nome)
        .issuer_name(nome)
        .public_key(chave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(agora - datetime.timedelta(days=1))
        .not_valid_after(agora + datetime.timedelta(days=365))
        .sign(chave, hashes.SHA256())
    )
    return pkcs12.serialize_key_and_certificates(
        name=b"teste",
        key=chave,
        cert=certificado,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(senha.encode()),
    )


def _pdf() -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(72, 750, "Receita de teste para validacao publica")
    c.save()
    return buffer.getvalue()


def test_codigo_publico_localiza_e_valida_pdf_pades_sem_expor_arquivo(
    client, db, criar_usuario, tmp_path, monkeypatch,
):
    user, _token = criar_usuario(email="validacao-farmacia@teste.local")
    monkeypatch.setattr(settings, "documentos_dir", str(tmp_path / "documentos"))
    monkeypatch.setattr(settings, "public_url", "https://corvia.med.br")

    codigo = validacao_publica.codigo_documento(
        tipo=emissao.TIPO_RECEITA,
        referencia_id=321,
        criado_por=user.id,
    )
    url = validacao_publica.url_documento(
        tipo=emissao.TIPO_RECEITA,
        referencia_id=321,
        criado_por=user.id,
    )
    assert codigo.startswith("R321-")
    assert url == f"https://corvia.med.br/validar/{codigo}"

    pdf_assinado = pdf_signer.assinar_pdf(
        _pdf(),
        pfx_bytes=_pfx(),
        senha="senha123",
        motivo="Prescricao",
        local="Ribeirao Preto/SP",
        codigo_validacao=codigo,
        url_validacao=url,
    )
    nome = cofre.guardar(pdf_assinado, user.id, raiz=emissao._raiz())
    registro = DocumentoEmitido(
        tipo=emissao.TIPO_RECEITA,
        referencia_id=321,
        metodo="A1_ARQUIVO",
        nivel="qualificada",
        arquivo_nome=nome,
        sha256=hashlib.sha256(pdf_assinado).hexdigest(),
        bytes_tam=len(pdf_assinado),
        assinado_em=datetime.datetime.now(datetime.timezone.utc),
        criado_por=user.id,
    )
    db.add(registro)
    db.commit()

    localizado = validacao_publica.localizar(db, codigo)
    assert localizado is not None
    resultado = validacao_publica.validar(localizado)
    assert resultado.valido is True
    assert resultado.integridade_hash is True
    assert resultado.assinatura_intacta is True
    assert resultado.cobre_documento_inteiro is True
    assert resultado.titular == "DR VALIDACAO FARMACIA:12345678900"

    resposta = client.get(f"/api/documentos-publicos/validar/{codigo}")
    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["valido"] is True
    assert corpo["codigo"] == codigo
    assert corpo["sha256"] == registro.sha256
    assert "arquivo" not in corpo
    assert "pdf" not in corpo

    invalido = client.get("/api/documentos-publicos/validar/R321-0000000000000000")
    assert invalido.status_code == 404


def test_preferencia_smime_nao_bloqueia_mail360_nativo(db, criar_usuario, monkeypatch):
    user, _token = criar_usuario(email="mail360-pades@teste.local")
    user.email_conta_padrao_envio = "corvia"
    user.email_assinatura_digital_ativa = True
    conta = EmailAccount(
        user_id=user.id,
        email_address="mail360-pades@corvia.med.br",
        mail360_account_key=f"key-{user.id}",
        status="ativa",
    )
    db.add(conta)
    db.commit()

    enviados: list[tuple] = []

    def _enviar(*args, **kwargs):
        enviados.append((args, kwargs))
        return {"ok": True}

    monkeypatch.setattr(mail360, "enviar_mensagem", _enviar)

    resultado = envio_documento_email.enviar(
        db,
        user,
        destinatario="paciente@teste.local",
        assunto="Sua receita CorVIA",
        corpo_html="<p>Documento PAdES disponível.</p>",
    )

    assert resultado.enviado is True
    assert resultado.erro is None
    assert resultado.assinado_smime is False
    assert len(enviados) == 1
