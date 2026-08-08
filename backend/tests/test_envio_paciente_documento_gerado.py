"""POST /api/document-templates/gerados/{gid}/envio-paciente — oferta de
envio ao paciente por e-mail ao concluir a assinatura digital (pedido do
Rafael, 08/08/2026). Cobre os três cenários pedidos: sem CorvIA Mail (409,
mesmo comportamento de "sem a opção"), com CorvIA Mail + canal automático
(pela Corvia, `contato@corvia.med.br`), com CorvIA Mail + canal próprio
(anexo real preparado na caixa nativa do médico via Mail360).
"""
import datetime
import io

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from reportlab.pdfgen import canvas

from app.models.assinatura import DocumentoEmitido
from app.models.clinical_docs import DocumentTemplate, GeneratedDocument
from app.models.email_account import EmailAccount
from app.models.email_log import EmailLog
from app.models.patient_document_email_send import PatientDocumentEmailSend
from app.models.subscription import Subscription
from app.services import cofre
from app.services.assinatura import emissao as assinatura_emissao
from app.services.assinatura import pdf_signer


def _gerar_pfx(*, senha: str = "senha123", cn: str = "DR TESTE DA SILVA:12345678900") -> bytes:
    # Mesmo helper de `tests/test_divulgacao_email.py` — certificado
    # autoassinado só para o teste conseguir produzir um PDF com assinatura
    # digital REAL embutida (pyhanko), já que `divulgacao_email.texto_
    # divulgacao()` nunca confia em metadado de banco, só no PDF de fato.
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


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _ativar_corvia_mail(db, user, email_address: str) -> EmailAccount:
    db.add(Subscription(user_id=user.id, kind="email", status="ativo"))
    conta = EmailAccount(
        user_id=user.id, email_address=email_address,
        mail360_account_key=f"key-{user.id}", status="ativa",
    )
    db.add(conta)
    db.commit()
    return conta


def _criar_gerado(db, user) -> GeneratedDocument:
    template = DocumentTemplate(
        owner_id=user.id, title="Atestado", doc_type="atestado", body="Texto do atestado.",
    )
    db.add(template)
    db.flush()
    gerado = GeneratedDocument(
        template_id=template.id, created_by=user.id, doc_type="atestado",
        title="Atestado", rendered_body="Texto do atestado.",
    )
    db.add(gerado)
    db.commit()
    db.refresh(gerado)
    return gerado


def _emitir(db, user, gerado_id: int, *, nivel: str) -> DocumentoEmitido:
    if nivel == "qualificada":
        # PDF com assinatura digital REAL embutida — necessário porque
        # `divulgacao_email.texto_divulgacao()` lê o arquivo de verdade
        # (pyhanko), nunca confia no `nivel` gravado no banco.
        pfx = _gerar_pfx()
        pdf = pdf_signer.assinar_pdf(
            _pdf_minimo(), pfx_bytes=pfx, senha="senha123", motivo="teste", local="teste",
        )
    else:
        pdf = b"%PDF-1.4 conteudo de teste\n%%EOF"
    nome_arquivo = cofre.guardar(pdf, user.id, raiz=assinatura_emissao._raiz())
    registro = DocumentoEmitido(
        tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=gerado_id,
        metodo="A1_ARQUIVO" if nivel == "qualificada" else "MANUAL", nivel=nivel,
        arquivo_nome=nome_arquivo, sha256="x" * 64, bytes_tam=len(pdf),
        assinado_em=datetime.datetime.now(datetime.timezone.utc), criado_por=user.id,
    )
    db.add(registro)
    db.commit()
    return registro


def _configurar_smtp_ok(monkeypatch, enviados: list):
    from app.services import emails

    class _SMTPFalso:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def starttls(self):
            pass

        def login(self, usuario, senha):
            pass

        def send_message(self, mensagem):
            enviados.append(mensagem)

    monkeypatch.setattr(emails.settings, "smtp_host", "smtp.teste.local")
    monkeypatch.setattr(emails.settings, "smtp_user", "contato@corvia.med.br")
    monkeypatch.setattr(emails.settings, "smtp_password", "segredo-de-teste")
    monkeypatch.setattr(emails.smtplib, "SMTP", lambda host, port, timeout=None: _SMTPFalso())


class TestSemCorviaMail:
    def test_canal_auto_recusa_409(self, client, db, criar_usuario):
        user, token = criar_usuario()
        gerado = _criar_gerado(db, user)
        _emitir(db, user, gerado.id, nivel="qualificada")

        resposta = client.post(
            f"/api/document-templates/gerados/{gerado.id}/envio-paciente",
            headers=_headers(token),
            json={"email_paciente": "paciente@teste.local", "canal": "auto_contato_corvia"},
        )
        assert resposta.status_code == 409, resposta.text
        assert "CorvIA Mail" in resposta.json()["detail"]

    def test_canal_proprio_recusa_409(self, client, db, criar_usuario):
        user, token = criar_usuario()
        gerado = _criar_gerado(db, user)
        _emitir(db, user, gerado.id, nivel="qualificada")

        resposta = client.post(
            f"/api/document-templates/gerados/{gerado.id}/envio-paciente",
            headers=_headers(token),
            json={"email_paciente": "paciente@teste.local", "canal": "proprio_corvia_mail"},
        )
        assert resposta.status_code == 409, resposta.text


class TestCanalAutomaticoContatoCorvia:
    def test_envia_pela_corvia_com_smtp_configurado(self, client, db, criar_usuario, monkeypatch):
        user, token = criar_usuario(email="medico-auto-doc@teste.local")
        _ativar_corvia_mail(db, user, "medico-auto-doc@corvia.med.br")
        gerado = _criar_gerado(db, user)
        _emitir(db, user, gerado.id, nivel="qualificada")

        enviados: list = []
        _configurar_smtp_ok(monkeypatch, enviados)

        resposta = client.post(
            f"/api/document-templates/gerados/{gerado.id}/envio-paciente",
            headers=_headers(token),
            json={"email_paciente": "paciente@teste.local", "canal": "auto_contato_corvia"},
        )
        assert resposta.status_code == 200, resposta.text
        corpo = resposta.json()
        assert corpo["enviado"] is True
        assert corpo["anexo"] is None
        assert len(enviados) == 1
        assert enviados[0]["To"] == "paciente@teste.local"

        registro = db.query(PatientDocumentEmailSend).filter(
            PatientDocumentEmailSend.referencia_id == gerado.id,
            PatientDocumentEmailSend.canal == "auto_contato_corvia",
        ).first()
        assert registro is not None
        assert registro.sucesso is True
        assert registro.assinatura_confirmada is True

        log = db.query(EmailLog).filter(EmailLog.tipo == "documento_paciente_auto").first()
        assert log is not None
        assert log.sucesso is True

    def test_sem_smtp_configurado_devolve_enviado_falso_sem_erro_500(self, client, db, criar_usuario):
        # conftest.py não define smtp_host/user/password — SMTP fica "não
        # configurado" por padrão, mesmo comportamento honesto do resto do
        # projeto (nunca finge que enviou).
        user, token = criar_usuario(email="medico-auto-doc2@teste.local")
        _ativar_corvia_mail(db, user, "medico-auto-doc2@corvia.med.br")
        gerado = _criar_gerado(db, user)
        _emitir(db, user, gerado.id, nivel="qualificada")

        resposta = client.post(
            f"/api/document-templates/gerados/{gerado.id}/envio-paciente",
            headers=_headers(token),
            json={"email_paciente": "paciente@teste.local", "canal": "auto_contato_corvia"},
        )
        assert resposta.status_code == 200, resposta.text
        corpo = resposta.json()
        assert corpo["enviado"] is False
        assert corpo["erro"]


class TestCanalProprioCorviaMail:
    def test_exige_assinatura_concluida(self, client, db, criar_usuario):
        user, token = criar_usuario(email="medico-proprio-doc@teste.local")
        _ativar_corvia_mail(db, user, "medico-proprio-doc@corvia.med.br")
        gerado = _criar_gerado(db, user)
        # Nunca chamou `_emitir` — nenhum `DocumentoEmitido` existe ainda.

        resposta = client.post(
            f"/api/document-templates/gerados/{gerado.id}/envio-paciente",
            headers=_headers(token),
            json={"email_paciente": "paciente@teste.local", "canal": "proprio_corvia_mail"},
        )
        assert resposta.status_code == 409, resposta.text
        assert "assinatura" in resposta.json()["detail"].lower()

    def test_prepara_anexo_com_assinatura_qualificada_e_confirmacao_no_corpo(
        self, client, db, criar_usuario, monkeypatch_mail360,
    ):
        user, token = criar_usuario(email="medico-proprio-doc2@teste.local")
        _ativar_corvia_mail(db, user, "medico-proprio-doc2@corvia.med.br")
        gerado = _criar_gerado(db, user)
        _emitir(db, user, gerado.id, nivel="qualificada")

        resposta = client.post(
            f"/api/document-templates/gerados/{gerado.id}/envio-paciente",
            headers=_headers(token),
            json={"email_paciente": "paciente@teste.local", "canal": "proprio_corvia_mail"},
        )
        assert resposta.status_code == 200, resposta.text
        corpo = resposta.json()
        assert corpo["enviado"] is None
        assert corpo["anexo"]["file_id"]
        assert corpo["assunto_sugerido"]
        # PDF de teste TEM assinatura digital real embutida (`_emitir` usa
        # `pdf_signer.assinar_pdf` para nivel="qualificada") — a frase de
        # confirmação vem de `divulgacao_email.texto_divulgacao()` lendo o
        # arquivo de verdade, nunca fabricada a partir do banco.
        assert "assinado digitalmente" in corpo["corpo_sugerido"]
        assert "DR TESTE DA SILVA" in corpo["corpo_sugerido"]

        anexos_subidos = monkeypatch_mail360["anexos"]
        assert len(anexos_subidos) == 1
        assert anexos_subidos[0][0] == f"key-{user.id}"

    def test_metodo_manual_tambem_libera_mas_sem_confirmacao_de_assinatura(
        self, client, db, criar_usuario, monkeypatch_mail360,
    ):
        user, token = criar_usuario(email="medico-proprio-manual@teste.local")
        _ativar_corvia_mail(db, user, "medico-proprio-manual@corvia.med.br")
        gerado = _criar_gerado(db, user)
        _emitir(db, user, gerado.id, nivel="nenhuma")

        resposta = client.post(
            f"/api/document-templates/gerados/{gerado.id}/envio-paciente",
            headers=_headers(token),
            json={"email_paciente": "paciente@teste.local", "canal": "proprio_corvia_mail"},
        )
        assert resposta.status_code == 200, resposta.text
        corpo = resposta.json()
        assert corpo["corpo_sugerido"] == ""

        registro = db.query(PatientDocumentEmailSend).filter(
            PatientDocumentEmailSend.referencia_id == gerado.id,
            PatientDocumentEmailSend.canal == "proprio_corvia_mail",
        ).first()
        assert registro.assinatura_confirmada is False
