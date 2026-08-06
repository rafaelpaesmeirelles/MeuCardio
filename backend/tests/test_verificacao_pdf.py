"""app/services/assinatura/verificacao_pdf.py — leitura REAL da assinatura
embutida num PDF (pyhanko), pedida pelo Rafael em 06/08/2026 para gerar o
texto de divulgação a partir do que está de fato gravado no arquivo, não
do certificado atual do médico no banco.
"""
import datetime
import io

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from reportlab.pdfgen import canvas

from app.services.assinatura import pdf_signer, verificacao_pdf


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


def _pdf_minimo(texto: str = "Documento de teste — Corvia") -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 750, texto)
    c.save()
    return buf.getvalue()


def test_pdf_nao_assinado_devolve_none():
    assert verificacao_pdf.verificar(_pdf_minimo()) is None


def test_pdf_assinado_extrai_titular_emissor_e_validade():
    pfx = _gerar_pfx(cn="DRA. FULANA DE TAL:98765432100")
    assinado = pdf_signer.assinar_pdf(_pdf_minimo(), pfx_bytes=pfx, senha="senha123", motivo="Receita", local="SP")

    resultado = verificacao_pdf.verificar(assinado)
    assert resultado is not None
    assert resultado.titular_cn == "DRA. FULANA DE TAL:98765432100"
    assert resultado.emissor_cn == "DRA. FULANA DE TAL:98765432100"  # autoassinado no teste
    assert resultado.intacta is True
    assert resultado.cobre_documento_inteiro is True
    assert resultado.valido_de < resultado.valido_ate
    assert resultado.numero_serie
    assert resultado.assinado_em is not None


def test_pdf_adulterado_depois_de_assinado_perde_integridade():
    pfx = _gerar_pfx()
    assinado = pdf_signer.assinar_pdf(_pdf_minimo(), pfx_bytes=pfx, senha="senha123", motivo="x", local="x")

    adulterado = bytearray(assinado)
    alvo = assinado.find(b"Documento de teste")
    adulterado[alvo] = ord("X")

    resultado = verificacao_pdf.verificar(bytes(adulterado))
    assert resultado is not None
    assert resultado.intacta is False
