"""app/services/assinatura/pdf_signer.py — assina de verdade um PDF gerado
pelo reportlab com um certificado de teste, e confere a assinatura de volta
com o próprio pyhanko (não confia só em "não levantou exceção" — reabre o
PDF assinado e valida a assinatura como um leitor real faria).
"""
import datetime
import io

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from reportlab.pdfgen import canvas

from app.services.assinatura import pdf_signer


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


def _gerar_pfx_com_intermediaria(*, senha: str = "senha123") -> tuple[bytes, bytes]:
    agora = datetime.datetime.now(datetime.timezone.utc)
    chave_ca = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nome_ca = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "AC TESTE INTERMEDIARIA")])
    certificado_ca = (
        x509.CertificateBuilder()
        .subject_name(nome_ca)
        .issuer_name(nome_ca)
        .public_key(chave_ca.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(agora - datetime.timedelta(days=1))
        .not_valid_after(agora + datetime.timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(chave_ca, hashes.SHA256())
    )
    chave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nome = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "DR COM CADEIA:12345678900")])
    certificado = (
        x509.CertificateBuilder()
        .subject_name(nome)
        .issuer_name(nome_ca)
        .public_key(chave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(agora - datetime.timedelta(days=1))
        .not_valid_after(agora + datetime.timedelta(days=180))
        .sign(chave_ca, hashes.SHA256())
    )
    pfx = pkcs12.serialize_key_and_certificates(
        name=b"teste-cadeia", key=chave, cert=certificado, cas=[certificado_ca],
        encryption_algorithm=serialization.BestAvailableEncryption(senha.encode()),
    )
    return pfx, certificado_ca.public_bytes(serialization.Encoding.DER)


def _pdf_minimo(texto: str = "Documento de teste — Corvia") -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 750, texto)
    c.save()
    return buf.getvalue()


def test_assinar_pdf_produz_assinatura_integra_e_valida():
    pfx = _gerar_pfx()
    pdf = _pdf_minimo()

    assinado = pdf_signer.assinar_pdf(pdf, pfx_bytes=pfx, senha="senha123", motivo="Receita médica", local="São Paulo")

    assert assinado != pdf
    assert len(assinado) > len(pdf)

    from pyhanko.pdf_utils.reader import PdfFileReader
    from pyhanko.sign.validation import validate_pdf_signature

    leitor = PdfFileReader(io.BytesIO(assinado))
    assert len(leitor.embedded_signatures) == 1
    assinatura = leitor.embedded_signatures[0]
    # O selo visivel e o proprio widget criptografico, nao texto decorativo
    # acrescentado depois. Retangulo nao vazio + appearance stream garantem
    # que qualquer leitor PDF possa exibi-lo na primeira pagina.
    assert list(assinatura.sig_field["/Rect"]) == [170, 20, 425, 88]
    assert assinatura.sig_field.get("/AP") is not None
    status = validate_pdf_signature(assinatura)
    assert status.intact is True
    assert status.valid is True


def test_assinar_pdf_com_url_publica_usa_qr_e_permanece_integro():
    from pyhanko.stamp import QRStampStyle
    from pyhanko.pdf_utils.reader import PdfFileReader
    from pyhanko.sign.validation import validate_pdf_signature

    pfx = _gerar_pfx()
    url = "https://corvia.med.br/validar/R123-0123456789ABCDEF"
    codigo = "R123-0123456789ABCDEF"

    estilo = pdf_signer._selo_visivel(codigo, url)
    assert isinstance(estilo, QRStampStyle)
    assert estilo.qr_inner_size == 36

    assinado = pdf_signer.assinar_pdf(
        _pdf_minimo(), pfx_bytes=pfx, senha="senha123",
        motivo="Receita médica", local="Ribeirão Preto",
        codigo_validacao=codigo, url_validacao=url,
    )
    assinatura = PdfFileReader(io.BytesIO(assinado)).embedded_signatures[0]
    assert assinatura.sig_field.get("/AP") is not None
    status = validate_pdf_signature(assinatura)
    assert status.intact is True
    assert status.valid is True


def test_assinar_pdf_embute_cadeia_e_usa_subfiltro_pades():
    pfx, intermediaria_der = _gerar_pfx_com_intermediaria()
    assinado = pdf_signer.assinar_pdf(
        _pdf_minimo(), pfx_bytes=pfx, senha="senha123",
        motivo="Receita de Controle Especial", local="Ribeirão Preto",
        cadeia_der=[intermediaria_der],
    )

    from pyhanko.pdf_utils.reader import PdfFileReader

    assinatura = PdfFileReader(io.BytesIO(assinado)).embedded_signatures[0]
    assert len(assinatura.other_embedded_certs) >= 1
    assert str(assinatura.sig_object["/SubFilter"]) == "/ETSI.CAdES.detached"


def test_assinar_pdf_posiciona_selo_da_rce_no_quadro_regulamentar():
    pfx = _gerar_pfx()
    assinado = pdf_signer.assinar_pdf(
        _pdf_minimo(), pfx_bytes=pfx, senha="senha123",
        motivo="Receita de Controle Especial", local="Ribeirão Preto",
        layout="RCE",
    )

    from pyhanko.pdf_utils.reader import PdfFileReader

    assinatura = PdfFileReader(io.BytesIO(assinado)).embedded_signatures[0]
    assert list(assinatura.sig_field["/Rect"]) == [285, 220, 545, 270]
    assert assinatura.sig_field.get("/AP") is not None


def test_assinar_pdf_com_senha_errada_falha_alto():
    pfx = _gerar_pfx(senha="senha-certa")
    pdf = _pdf_minimo()
    with pytest.raises(pdf_signer.FalhaAoAssinar):
        pdf_signer.assinar_pdf(pdf, pfx_bytes=pfx, senha="senha-errada", motivo="x", local="x")


def test_assinar_pdf_com_arquivo_corrompido_falha_alto():
    with pytest.raises(pdf_signer.FalhaAoAssinar):
        pdf_signer.assinar_pdf(b"nao e pdf", pfx_bytes=b"nem certificado", senha="x", motivo="x", local="x")


def test_assinatura_detecta_adulteracao_pos_assinatura():
    """Garante que a assinatura é sensível a bytes trocados depois — não é
    só um carimbo cosmético."""
    pfx = _gerar_pfx()
    pdf = _pdf_minimo()
    assinado = pdf_signer.assinar_pdf(pdf, pfx_bytes=pfx, senha="senha123", motivo="x", local="x")

    adulterado = bytearray(assinado)
    # Troca um byte no meio do conteúdo do PDF (fora da área de assinatura,
    # em algum ponto do stream de texto) — qualquer byte no corpo altera o hash.
    alvo = assinado.find(b"Documento de teste")
    adulterado[alvo] = ord("X")

    from pyhanko.pdf_utils.reader import PdfFileReader
    from pyhanko.sign.validation import validate_pdf_signature

    leitor = PdfFileReader(io.BytesIO(bytes(adulterado)))
    status = validate_pdf_signature(leitor.embedded_signatures[0])
    assert status.intact is False
