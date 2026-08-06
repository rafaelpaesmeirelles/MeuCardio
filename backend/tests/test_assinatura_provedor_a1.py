"""app/services/assinatura/provedor.py::CertificadoA1 — a costura entre o
certificado guardado e a assinatura de fato, exercitada como
`emissao.assinar_e_persistir()` chamaria (mas direto no provedor, sem
precisar montar um documento completo de receita/laudo)."""
import datetime
import io

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from reportlab.pdfgen import canvas

from app.core.config import settings
from app.services.assinatura import certificado_a1
from app.services.assinatura.provedor import CertificadoA1, obter_provedor


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


def _pdf_minimo() -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 750, "Receita de teste")
    c.save()
    return buf.getvalue()


@pytest.fixture(autouse=True)
def _diretorio_certificados(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "certificados_dir", str(tmp_path))


def test_disponivel_false_sem_certificado(db, criar_usuario):
    user, _ = criar_usuario()
    provedor = CertificadoA1(db, user)
    disponivel, motivo = provedor.disponivel()
    assert disponivel is False
    assert "certificado" in motivo.lower()


def test_disponivel_true_apos_conectar(db, criar_usuario):
    user, _ = criar_usuario()
    certificado_a1.salvar(db, user, _gerar_pfx(), "senha123", None)
    db.commit()
    provedor = CertificadoA1(db, user)
    disponivel, motivo = provedor.disponivel()
    assert disponivel is True
    assert motivo is None


def test_assinar_produz_pdf_assinado_de_verdade(db, criar_usuario):
    user, _ = criar_usuario()
    certificado_a1.salvar(db, user, _gerar_pfx(cn="DR ASSINANTE:44455566677"), "senha123", None)
    db.commit()

    provedor = CertificadoA1(db, user)
    pdf_original = _pdf_minimo()
    resultado = provedor.assinar(pdf_original, {"municipio": "São Paulo"}, {"tipo": "prescription_document"})

    assert resultado.estado == "assinado"
    assert resultado.pdf is not None
    assert resultado.pdf != pdf_original

    from pyhanko.pdf_utils.reader import PdfFileReader
    from pyhanko.sign.validation import validate_pdf_signature

    leitor = PdfFileReader(io.BytesIO(resultado.pdf))
    status = validate_pdf_signature(leitor.embedded_signatures[0])
    assert status.intact is True
    assert status.valid is True


def test_assinar_sem_certificado_devolve_indisponivel_nao_levanta_excecao(db, criar_usuario):
    user, _ = criar_usuario()
    provedor = CertificadoA1(db, user)
    resultado = provedor.assinar(_pdf_minimo(), {}, {"tipo": "generated_document"})
    assert resultado.estado == "indisponivel"
    assert resultado.motivo is not None
    assert resultado.pdf is None


def test_obter_provedor_nao_compartilha_estado_entre_usuarios(db, criar_usuario):
    user1, _ = criar_usuario()
    user2, _ = criar_usuario(email="isolamento-provedor@teste.local")
    certificado_a1.salvar(db, user1, _gerar_pfx(cn="USER1:11111111111"), "senha123", None)
    db.commit()

    provedor_user1 = obter_provedor("A1_ARQUIVO", db=db, user=user1)
    provedor_user2 = obter_provedor("A1_ARQUIVO", db=db, user=user2)

    assert provedor_user1.disponivel()[0] is True
    assert provedor_user2.disponivel()[0] is False
    # Instâncias diferentes — confirma que não veio do cache module-level
    # (que quebraria justamente aqui, misturando o certificado de um médico
    # com a sessão de outro).
    assert provedor_user1 is not provedor_user2


def test_obter_provedor_a1_sem_user_levanta_erro():
    with pytest.raises(ValueError):
        obter_provedor("A1_ARQUIVO")
