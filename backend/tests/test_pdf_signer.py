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
    status = validate_pdf_signature(leitor.embedded_signatures[0])
    assert status.intact is True
    assert status.valid is True


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
