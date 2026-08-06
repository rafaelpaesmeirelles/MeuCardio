"""app/services/assinatura/certificado_a1.py — parsing/validação de PKCS#12
real (gerado na hora com `cryptography`, sem depender de certificado ICP-
Brasil de verdade) e o ciclo completo salvar/carregar/remover via cofre.
"""
import datetime

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

from app.core.config import settings
from app.models.assinatura import DigitalCertificate
from app.services.assinatura import certificado_a1


def _gerar_pfx(*, senha: str = "senha123", cn: str = "DR TESTE DA SILVA:12345678900", dias_validade: int = 365) -> bytes:
    chave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nome = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    certificado = (
        x509.CertificateBuilder()
        .subject_name(nome)
        .issuer_name(nome)
        .public_key(chave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=dias_validade))
        .sign(chave, hashes.SHA256())
    )
    return pkcs12.serialize_key_and_certificates(
        name=b"teste", key=chave, cert=certificado, cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(senha.encode()),
    )


@pytest.fixture(autouse=True)
def _diretorio_certificados(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "certificados_dir", str(tmp_path))


def test_analisar_extrai_cn_e_validade():
    pfx = _gerar_pfx(cn="DRA. FULANA DE TAL:98765432100")
    dados = certificado_a1.analisar(pfx, "senha123")
    assert dados.titular_cn == "DRA. FULANA DE TAL:98765432100"
    assert len(dados.numero_serie) > 0
    assert dados.valido_ate > datetime.datetime.now(datetime.timezone.utc)


def test_analisar_senha_errada_e_invalido():
    pfx = _gerar_pfx(senha="senha-certa")
    with pytest.raises(certificado_a1.CertificadoInvalido):
        certificado_a1.analisar(pfx, "senha-errada")


def test_analisar_arquivo_nao_e_pkcs12():
    with pytest.raises(certificado_a1.CertificadoInvalido):
        certificado_a1.analisar(b"isso nao e um certificado", "qualquer")


def test_analisar_certificado_vencido_e_invalido():
    pfx = _gerar_pfx(dias_validade=-1)
    with pytest.raises(certificado_a1.CertificadoInvalido) as excinfo:
        certificado_a1.analisar(pfx, "senha123")
    assert "venceu" in str(excinfo.value)


def test_salvar_persiste_e_obter_devolve(db, criar_usuario):
    user, _ = criar_usuario()
    pfx = _gerar_pfx(cn="DR TESTE:11122233344")
    registro = certificado_a1.salvar(db, user, pfx, "senha123", "Certisign")
    db.commit()

    obtido = certificado_a1.obter(db, user)
    assert obtido is not None
    assert obtido.titular_cn == "DR TESTE:11122233344"
    assert obtido.certificadora == "Certisign"
    assert obtido.id == registro.id


def test_salvar_de_novo_substitui_e_apaga_arquivo_antigo(db, criar_usuario):
    user, _ = criar_usuario()
    pfx1 = _gerar_pfx(cn="PRIMEIRO:11111111111")
    r1 = certificado_a1.salvar(db, user, pfx1, "senha123", None)
    db.commit()
    nome_antigo = r1.arquivo_nome

    pfx2 = _gerar_pfx(cn="SEGUNDO:22222222222", senha="senha456")
    certificado_a1.salvar(db, user, pfx2, "senha456", "Soluti")
    db.commit()

    assert db.query(DigitalCertificate).filter(DigitalCertificate.owner_id == user.id).count() == 1
    atual = certificado_a1.obter(db, user)
    assert atual.titular_cn == "SEGUNDO:22222222222"
    from app.services import cofre
    with pytest.raises(FileNotFoundError):
        cofre.ler(nome_antigo, user.id, raiz=certificado_a1._raiz())


def test_salvar_com_senha_errada_nao_persiste_nada(db, criar_usuario):
    user, _ = criar_usuario()
    pfx = _gerar_pfx(senha="certa")
    with pytest.raises(certificado_a1.CertificadoInvalido):
        certificado_a1.salvar(db, user, pfx, "errada", None)
    assert certificado_a1.obter(db, user) is None


def test_remover_apaga_registro_e_arquivo(db, criar_usuario):
    user, _ = criar_usuario()
    pfx = _gerar_pfx()
    certificado_a1.salvar(db, user, pfx, "senha123", None)
    db.commit()

    assert certificado_a1.remover(db, user) is True
    db.commit()
    assert certificado_a1.obter(db, user) is None


def test_remover_sem_certificado_devolve_false(db, criar_usuario):
    user, _ = criar_usuario()
    assert certificado_a1.remover(db, user) is False


def test_carregar_para_assinar_decifra_arquivo_e_senha(db, criar_usuario):
    user, _ = criar_usuario()
    pfx = _gerar_pfx(cn="DR CARREGAR:55566677788", senha="senha-de-teste")
    certificado_a1.salvar(db, user, pfx, "senha-de-teste", None)
    db.commit()

    carregado = certificado_a1.carregar_para_assinar(db, user)
    assert carregado.senha == "senha-de-teste"
    assert carregado.dados.titular_cn == "DR CARREGAR:55566677788"
    assert carregado.pfx_bytes  # bytes originais recuperados


def test_carregar_para_assinar_sem_certificado_levanta_erro(db, criar_usuario):
    user, _ = criar_usuario()
    with pytest.raises(certificado_a1.CertificadoInvalido):
        certificado_a1.carregar_para_assinar(db, user)


def test_isolamento_entre_usuarios(db, criar_usuario):
    user1, _ = criar_usuario()
    user2, _ = criar_usuario(email="outro-cert@teste.local")
    pfx1 = _gerar_pfx(cn="USER1:11111111111", senha="senha1")
    certificado_a1.salvar(db, user1, pfx1, "senha1", None)
    db.commit()

    assert certificado_a1.obter(db, user2) is None
