"""app/services/assinatura/divulgacao_email.py — texto de divulgação da
assinatura para o corpo do e-mail, a partir da verificação REAL do PDF.
"""
import datetime
import io

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from reportlab.pdfgen import canvas

from app.services.assinatura import divulgacao_email, pdf_signer


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


def test_documento_sem_assinatura_nao_gera_texto():
    assert divulgacao_email.texto_divulgacao(_pdf_minimo()) is None


def test_documento_assinado_intacto_gera_texto_afirmativo():
    pfx = _gerar_pfx(cn="DR TESTE DA SILVA:12345678900")
    assinado = pdf_signer.assinar_pdf(_pdf_minimo(), pfx_bytes=pfx, senha="senha123", motivo="x", local="x")

    texto = divulgacao_email.texto_divulgacao(assinado)
    assert texto is not None
    assert "DR TESTE DA SILVA:12345678900" in texto
    assert "integridade do arquivo foi conferida" in texto
    assert "⚠️" not in texto


def _gerar_pfx_com_emissor_proprio(*, senha: str, cn_titular: str, cn_emissor: str) -> bytes:
    """Monta um par emissor→titular (em vez do autoassinado de
    `_gerar_pfx`), para provar que `divulgacao_email` lê o emissor QUE
    ESTÁ NO CERTIFICADO — nunca uma lista fixa de certificadoras — e por
    isso já reconhece qualquer AC credenciada ICP-Brasil que assine pelo
    Assinador ITI (VIDaaS, Bird ID, SafeID, NeoID, RemoteID, gov.br...),
    sem precisar de nenhum código novo por certificadora (Trabalho 14,
    06/08/2026)."""
    chave_emissor = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nome_emissor = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn_emissor)])
    cert_emissor = (
        x509.CertificateBuilder()
        .subject_name(nome_emissor).issuer_name(nome_emissor).public_key(chave_emissor.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(chave_emissor, hashes.SHA256())
    )

    chave_titular = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nome_titular = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn_titular)])
    cert_titular = (
        x509.CertificateBuilder()
        .subject_name(nome_titular).issuer_name(nome_emissor).public_key(chave_titular.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
        .sign(chave_emissor, hashes.SHA256())
    )

    return pkcs12.serialize_key_and_certificates(
        name=b"teste", key=chave_titular, cert=cert_titular, cas=[cert_emissor],
        encryption_algorithm=serialization.BestAvailableEncryption(senha.encode()),
    )


def test_reconhece_qualquer_certificadora_pelo_que_esta_no_certificado():
    """Nenhuma menção a VIDaaS/Bird ID/SafeID/NeoID/RemoteID/gov.br existe
    em `divulgacao_email.py` nem em `verificacao_pdf.py` — e não precisa:
    o emissor exibido vem sempre do campo `issuer` do certificado X.509
    embutido no PDF, então qualquer AC credenciada ICP-Brasil que assine
    pelo Assinador ITI já é reconhecida sem alteração de código."""
    pfx = _gerar_pfx_com_emissor_proprio(
        senha="senha123",
        cn_titular="DR TESTE DA SILVA:12345678900",
        cn_emissor="AC VIDaaS Multipla ICP-Brasil - Instituto Fiscal",
    )
    assinado = pdf_signer.assinar_pdf(_pdf_minimo(), pfx_bytes=pfx, senha="senha123", motivo="x", local="x")

    texto = divulgacao_email.texto_divulgacao(assinado)
    assert texto is not None
    assert "DR TESTE DA SILVA:12345678900" in texto
    assert "AC VIDaaS Multipla ICP-Brasil - Instituto Fiscal" in texto


def test_documento_adulterado_gera_aviso_em_vez_de_afirmacao():
    pfx = _gerar_pfx()
    assinado = pdf_signer.assinar_pdf(_pdf_minimo(), pfx_bytes=pfx, senha="senha123", motivo="x", local="x")
    adulterado = bytearray(assinado)
    adulterado[assinado.find(b"Documento de teste")] = ord("X")

    texto = divulgacao_email.texto_divulgacao(bytes(adulterado))
    assert texto is not None
    assert "⚠️" in texto
    assert "NÃO confirmou a integridade" in texto
