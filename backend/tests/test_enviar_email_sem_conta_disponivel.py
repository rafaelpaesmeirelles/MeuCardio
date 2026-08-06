"""Envio de receituário/documento por e-mail quando o médico NÃO tem
CorvIA Mail ativo nem outra conta conectada como padrão — cenário real:
assinante do plano básico (sem CorvIA Mail incluso) que ainda gera e
assina documentos. Trabalho 11, ampliação de 06/08/2026.

Antes desta correção, a rota devolvia 502 e DESCARTAVA o link já criado —
regressão introduzida na própria ampliação de hoje (o comportamento
original, anterior a esta sessão, sempre devolveu o link em caso de falha
de envio, para o médico compartilhar por outro canal). Estes testes fixam
o contrato correto: `enviado: false` + `link` presente, nunca 502.
"""
import datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from sqlalchemy import text

from app.models.assinatura import DocumentoEmitido
from app.models.clinical_docs import DocumentTemplate, GeneratedDocument, Prescription
from app.models.receituario import (
    PrescriptionDocument, PrescriptionRecipient, PrescriptionType,
)
from app.models.subscription import Subscription
from app.services import cofre
from app.services.assinatura import emissao as assinatura_emissao

_TABELAS = (
    "documentos_emitidos", "prescription_documents", "prescription_recipients",
    "prescriptions", "generated_documents", "document_templates", "prescription_types",
    "digital_certificates",
)


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _gerar_pfx() -> bytes:
    chave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nome = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "DR TESTE:12345678900")])
    certificado = (
        x509.CertificateBuilder()
        .subject_name(nome).issuer_name(nome).public_key(chave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
        .sign(chave, hashes.SHA256())
    )
    return pkcs12.serialize_key_and_certificates(
        name=b"t", key=chave, cert=certificado, cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(b"senha123"),
    )


def _emitido_qualificada(db, user, *, tipo: str, referencia_id: int) -> DocumentoEmitido:
    """Simula um documento já emitido com certificado A1 (nível
    'qualificada') sem passar pelo fluxo HTTP de assinatura — o que se
    testa aqui é a rota de envio, não a emissão em si (já coberta em
    test_pdf_signer.py/test_assinatura_provedor_a1.py)."""
    pdf_falso = b"%PDF-1.4 conteudo de teste\n%%EOF"
    nome_arquivo = cofre.guardar(pdf_falso, user.id, raiz=assinatura_emissao._raiz())
    registro = DocumentoEmitido(
        tipo=tipo, referencia_id=referencia_id, metodo="A1_ARQUIVO", nivel="qualificada",
        arquivo_nome=nome_arquivo, sha256="x" * 64, bytes_tam=len(pdf_falso),
        assinado_em=datetime.datetime.now(datetime.timezone.utc), criado_por=user.id,
    )
    db.add(registro)
    db.commit()
    return registro


def _fixture_limpa(db):
    db.execute(text(f"TRUNCATE {', '.join(_TABELAS)} RESTART IDENTITY CASCADE"))
    db.add(PrescriptionType(codigo="COMUM", nome="Receituário comum", ativo=True))
    db.commit()


def test_receituario_sem_conta_de_envio_devolve_link_em_vez_de_502(client, db, criar_usuario):
    _fixture_limpa(db)
    user, token = criar_usuario()
    _subscribe(db, user.id)

    presc = Prescription(created_by=user.id, items=[{"descricao": "Losartana"}])
    db.add(presc)
    db.flush()
    db.add(PrescriptionRecipient(
        prescription_id=presc.id,
        nome_cifrado=cofre.cifrar_campo("Paciente Teste", presc.id),
    ))
    doc = PrescriptionDocument(prescription_id=presc.id, tipo_codigo="COMUM", status="emitido")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    _emitido_qualificada(db, user, tipo=assinatura_emissao.TIPO_RECEITA, referencia_id=doc.id)

    # Sem EmailAccount, sem CalendarIntegration — nenhuma conta de envio disponível.
    resposta = client.post(
        f"/api/receituario/documentos/{doc.id}/enviar-email",
        headers=_headers(token), json={"email": "paciente@teste.local"},
    )
    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["enviado"] is False
    assert corpo["link"] is not None
    assert corpo["link"].startswith("https://corvia.med.br/api/documentos-publicos/")
    assert corpo["erro"]


def test_documento_gerado_sem_conta_de_envio_devolve_link_em_vez_de_502(client, db, criar_usuario):
    _fixture_limpa(db)
    user, token = criar_usuario()
    _subscribe(db, user.id)

    template = DocumentTemplate(owner_id=user.id, title="Atestado", doc_type="atestado", body="Texto do atestado.")
    db.add(template)
    db.flush()
    gerado = GeneratedDocument(
        template_id=template.id, created_by=user.id, doc_type="atestado",
        title="Atestado", rendered_body="Texto do atestado.",
    )
    db.add(gerado)
    db.commit()
    db.refresh(gerado)

    _emitido_qualificada(db, user, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=gerado.id)

    resposta = client.post(
        f"/api/document-templates/gerados/{gerado.id}/enviar-email",
        headers=_headers(token), json={"email": "paciente@teste.local"},
    )
    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["enviado"] is False
    assert corpo["link"] is not None
    assert corpo["erro"]
