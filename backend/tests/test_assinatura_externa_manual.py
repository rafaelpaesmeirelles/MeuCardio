"""Fluxo manual de assinatura via Assinador ITI (Trabalho 14, 06/08/2026) —
GOVBR e as clouds sem credencial comercial (VIDAAS/BIRDID/SAFEID/NEOID/
REMOTEID): a Corvia nunca assina nada sozinha, só emite o PDF pra
assinatura externa e depois CONFERE uma assinatura real embutida antes de
aceitar o reenvio.
"""
import datetime

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID, ObjectIdentifier
from sqlalchemy import text

from app.models.receituario import PrescriptionType
from app.services.assinatura import pdf_signer
from app.services.assinatura.provedor import AssinaturaExternaManual, obter_provedor

_TABELAS = (
    "documentos_emitidos", "prescription_documents", "prescription_recipients",
    "prescriptions", "generated_documents", "document_templates", "prescription_types",
)


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def _seed(db):
    db.execute(text(f"TRUNCATE {', '.join(_TABELAS)} RESTART IDENTITY CASCADE"))
    db.add(PrescriptionType(codigo="COMUM", nome="Receituário comum", ativo=True))
    db.commit()


def _gerar_pfx(*, cn: str = "DR TESTE:12345678900", politica: str | None = None) -> bytes:
    chave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nome = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    construtor = (
        x509.CertificateBuilder()
        .subject_name(nome).issuer_name(nome).public_key(chave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
    )
    if politica:
        construtor = construtor.add_extension(
            x509.CertificatePolicies([
                x509.PolicyInformation(ObjectIdentifier(politica), None),
            ]),
            critical=False,
        )
    certificado = construtor.sign(chave, hashes.SHA256())
    return pkcs12.serialize_key_and_certificates(
        name=b"t", key=chave, cert=certificado, cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(b"senha123"),
    )


def _assinar_de_verdade(pdf: bytes, *, politica: str | None = None) -> bytes:
    """Simula o que o médico faz FORA da Corvia: assina o PDF de verdade
    com um certificado (aqui, um autoassinado de teste, mas o mecanismo de
    assinatura é o mesmo pyhanko/PAdES real)."""
    pfx = _gerar_pfx(politica=politica)
    return pdf_signer.assinar_pdf(pdf, pfx_bytes=pfx, senha="senha123", motivo="teste", local="SP")


def _emitir_rce(client, db, criar_usuario, *, metodo: str):
    user, token = criar_usuario(full_name="Dr. Teste RCE", role="admin")
    user.council_name = "CRM"
    user.council_number = "123456"
    user.council_state = "SP"
    user.practice_street = "Rua Clínica"
    user.practice_number = "100"
    user.practice_city = "Ribeirão Preto"
    user.practice_state = "SP"
    db.add(PrescriptionType(
        codigo="RCE", nome="Receita de Controle Especial", ativo=True,
        exige_numeracao_sncr=False,
    ))
    db.commit()
    criada = client.post(
        "/api/receituario", headers=_headers(token),
        json={
            "destinatario": {
                "nome": "Paciente Teste",
                "endereco": "Rua do Paciente, 10, Ribeirão Preto/SP",
                "documento": "123.456.789-00",
            },
            "itens": [{
                "descricao": "Medicamento de teste",
                "apresentacao": "comprimidos",
                "quantidade": "30",
                "quantidade_extenso": "trinta comprimidos",
                "posologia": "Tomar um comprimido ao dia.",
            }],
        },
    )
    assert criada.status_code == 201, criada.text
    doc_id = criada.json()["documentos"][0]["id"]
    revisada = client.post(
        f"/api/receituario/documentos/{doc_id}/revisar", headers=_headers(token),
        json={
            "confirmar": True,
            "corrigir_para": "RCE",
            "motivo": "Teste de assinatura qualificada.",
        },
    )
    assert revisada.status_code == 200, revisada.text
    emitida = client.post(
        f"/api/receituario/documentos/{doc_id}/emitir", headers=_headers(token),
        json={"metodo": metodo},
    )
    return token, doc_id, emitida


class TestCatalogo:
    @pytest.mark.parametrize("codigo,nivel_esperado", [
        ("GOVBR", "avancada"),
        ("VIDAAS", "qualificada"),
        ("BIRDID", "qualificada"),
        ("SAFEID", "qualificada"),
        ("NEOID", "qualificada"),
        ("REMOTEID", "qualificada"),
        ("A3_TOKEN", "qualificada"),
    ])
    def test_provedor_disponivel_sem_nenhuma_credencial(self, db, codigo, nivel_esperado):
        provedor = obter_provedor(codigo)
        assert isinstance(provedor, AssinaturaExternaManual)
        disponivel, motivo = provedor.disponivel()
        assert disponivel is True
        assert motivo is None
        assert provedor.nivel == nivel_esperado

    def test_assinar_nao_assina_nada_devolve_pdf_como_veio(self, db):
        provedor = obter_provedor("GOVBR")
        pdf = b"%PDF-1.4 conteudo\n%%EOF"
        resultado = provedor.assinar(pdf, {}, {})
        assert resultado.estado == "nao_assinado"
        assert resultado.pdf == pdf


class TestEmitirComGovbr(object):
    def _criar_receita(self, client, token):
        r = client.post(
            "/api/receituario", headers=_headers(token),
            json={"destinatario": {"nome": "Paciente Teste"}, "itens": [{"descricao": "Dipirona"}]},
        )
        assert r.status_code == 201, r.text
        return r.json()["documentos"][0]["id"]

    def test_emitir_com_govbr_nao_assina_e_libera_upload(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        doc_id = self._criar_receita(client, token)
        client.post(f"/api/receituario/documentos/{doc_id}/revisar", headers=_headers(token), json={"confirmar": True})

        r = client.post(
            f"/api/receituario/documentos/{doc_id}/emitir", headers=_headers(token), json={"metodo": "GOVBR"},
        )
        assert r.status_code == 200, r.text
        assert r.headers["content-type"] == "application/pdf"
        assert r.content.startswith(b"%PDF-")


class TestAssinaturaExterna:
    def _emitir_govbr(self, client, token):
        r = client.post(
            "/api/receituario", headers=_headers(token),
            json={"destinatario": {"nome": "Paciente Teste"}, "itens": [{"descricao": "Dipirona"}]},
        )
        doc_id = r.json()["documentos"][0]["id"]
        client.post(f"/api/receituario/documentos/{doc_id}/revisar", headers=_headers(token), json={"confirmar": True})
        emitir = client.post(
            f"/api/receituario/documentos/{doc_id}/emitir", headers=_headers(token), json={"metodo": "GOVBR"},
        )
        return doc_id, emitir.content

    def test_upload_com_pdf_sem_assinatura_e_rejeitado(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        doc_id, pdf_original = self._emitir_govbr(client, token)

        r = client.post(
            f"/api/receituario/documentos/{doc_id}/assinatura-externa",
            headers=_headers(token),
            files={"arquivo": ("assinado.pdf", pdf_original, "application/pdf")},
        )
        assert r.status_code == 422, r.text
        assert "não contém" in r.json()["detail"]

    def test_upload_com_pdf_assinado_de_verdade_e_aceito(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        doc_id, pdf_original = self._emitir_govbr(client, token)
        pdf_assinado = _assinar_de_verdade(pdf_original)

        r = client.post(
            f"/api/receituario/documentos/{doc_id}/assinatura-externa",
            headers=_headers(token),
            files={"arquivo": ("assinado.pdf", pdf_assinado, "application/pdf")},
        )
        assert r.status_code == 200, r.text
        assert r.json()["assinado"] is True
        assert r.json()["assinado_em"] is not None

    def test_upload_duplicado_e_recusado(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        doc_id, pdf_original = self._emitir_govbr(client, token)
        pdf_assinado = _assinar_de_verdade(pdf_original)

        primeiro = client.post(
            f"/api/receituario/documentos/{doc_id}/assinatura-externa",
            headers=_headers(token), files={"arquivo": ("a.pdf", pdf_assinado, "application/pdf")},
        )
        assert primeiro.status_code == 200

        segundo = client.post(
            f"/api/receituario/documentos/{doc_id}/assinatura-externa",
            headers=_headers(token), files={"arquivo": ("a.pdf", pdf_assinado, "application/pdf")},
        )
        assert segundo.status_code == 409
        assert "já está assinado" in segundo.json()["detail"]

    def test_upload_de_pdf_adulterado_depois_de_assinado_e_rejeitado(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        doc_id, pdf_original = self._emitir_govbr(client, token)
        pdf_assinado = bytearray(_assinar_de_verdade(pdf_original))
        # O texto do receituário vem comprimido no stream do PDF (reportlab
        # usa FlateDecode) — buscar por texto literal como "Dipirona" não
        # acha nada. Um byte no meio do arquivo está garantidamente dentro
        # do intervalo coberto pela assinatura, em qualquer documento deste
        # tamanho.
        meio = len(pdf_assinado) // 2
        pdf_assinado[meio] ^= 0xFF

        r = client.post(
            f"/api/receituario/documentos/{doc_id}/assinatura-externa",
            headers=_headers(token),
            files={"arquivo": ("adulterado.pdf", bytes(pdf_assinado), "application/pdf")},
        )
        assert r.status_code == 422, r.text

    def test_upload_de_outro_pdf_assinado_e_rejeitado(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        doc_id, _ = self._emitir_govbr(client, token)
        pdf_de_outro_documento = _assinar_de_verdade(b"%PDF-1.4\noutro documento\n%%EOF")

        r = client.post(
            f"/api/receituario/documentos/{doc_id}/assinatura-externa",
            headers=_headers(token),
            files={"arquivo": ("outro.pdf", pdf_de_outro_documento, "application/pdf")},
        )
        assert r.status_code == 422, r.text
        assert "não corresponde exatamente" in r.json()["detail"]

    def test_documento_de_outro_usuario_e_404(self, client, criar_usuario):
        dono, token_dono = criar_usuario(email="dono@teste.local", role="admin")
        _, token_intruso = criar_usuario(email="intruso@teste.local", role="admin")
        doc_id, pdf_original = self._emitir_govbr(client, token_dono)
        pdf_assinado = _assinar_de_verdade(pdf_original)

        r = client.post(
            f"/api/receituario/documentos/{doc_id}/assinatura-externa",
            headers=_headers(token_intruso),
            files={"arquivo": ("a.pdf", pdf_assinado, "application/pdf")},
        )
        assert r.status_code == 404


class TestRceAssinaturaQualificada:
    def test_rce_bloqueia_govbr_avancada(self, client, db, criar_usuario):
        _, _, emitida = _emitir_rce(client, db, criar_usuario, metodo="GOVBR")
        assert emitida.status_code == 409, emitida.text
        bloqueios = " ".join(emitida.json()["detail"]["bloqueios"])
        assert "gov.br comum" in bloqueios
        assert "qualificada ICP-Brasil" in bloqueios

    def test_rce_aceita_a3_com_politica_icp_brasil_real(self, client, db, criar_usuario):
        token, doc_id, emitida = _emitir_rce(
            client, db, criar_usuario, metodo="A3_TOKEN",
        )
        assert emitida.status_code == 200, emitida.text
        pdf_assinado = _assinar_de_verdade(
            emitida.content, politica="2.16.76.1.2.3.999",
        )

        concluida = client.post(
            f"/api/receituario/documentos/{doc_id}/assinatura-externa",
            headers=_headers(token),
            files={"arquivo": ("assinado-a3.pdf", pdf_assinado, "application/pdf")},
        )
        assert concluida.status_code == 200, concluida.text
        assert concluida.json()["assinado"] is True

    def test_rce_rejeita_metodo_qualificado_assinado_sem_politica_icp(
        self, client, db, criar_usuario,
    ):
        token, doc_id, emitida = _emitir_rce(
            client, db, criar_usuario, metodo="VIDAAS",
        )
        assert emitida.status_code == 200, emitida.text
        pdf_assinado = _assinar_de_verdade(emitida.content)

        concluida = client.post(
            f"/api/receituario/documentos/{doc_id}/assinatura-externa",
            headers=_headers(token),
            files={"arquivo": ("sem-politica-icp.pdf", pdf_assinado, "application/pdf")},
        )
        assert concluida.status_code == 422, concluida.text
        assert "A1, A2, A3 ou A4 ICP-Brasil" in concluida.json()["detail"]
