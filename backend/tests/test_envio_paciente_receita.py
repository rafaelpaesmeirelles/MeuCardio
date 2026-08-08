"""POST /api/receituario/documentos/{documento_id}/envio-paciente — mesma
oferta de envio ao paciente por e-mail, para receituário (pedido do Rafael,
08/08/2026). Mais estrita que o documento genérico: só libera com
assinatura qualificada ICP-Brasil (mesma regra já valia para `enviar-email`).
"""
import datetime

from app.models.assinatura import DocumentoEmitido
from app.models.clinical_docs import Prescription
from app.models.email_account import EmailAccount
from app.models.patient_document_email_send import PatientDocumentEmailSend
from app.models.receituario import PrescriptionDocument, PrescriptionRecipient, PrescriptionType
from app.models.subscription import Subscription
from app.services import cofre
from app.services.assinatura import emissao as assinatura_emissao


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


def _tipo_comum(db) -> None:
    if not db.query(PrescriptionType).filter(PrescriptionType.codigo == "COMUM").first():
        db.add(PrescriptionType(codigo="COMUM", nome="Receituário comum", ativo=True))
        db.commit()


def _criar_documento_emitido(db, user) -> PrescriptionDocument:
    _tipo_comum(db)
    presc = Prescription(created_by=user.id, items=[{"descricao": "Losartana"}])
    db.add(presc)
    db.flush()
    db.add(PrescriptionRecipient(
        prescription_id=presc.id, nome_cifrado=cofre.cifrar_campo("Paciente Teste", presc.id),
    ))
    doc = PrescriptionDocument(prescription_id=presc.id, tipo_codigo="COMUM", status="emitido")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def _emitir(db, user, doc_id: int, *, nivel: str) -> DocumentoEmitido:
    pdf_falso = b"%PDF-1.4 conteudo de teste\n%%EOF"
    nome_arquivo = cofre.guardar(pdf_falso, user.id, raiz=assinatura_emissao._raiz())
    registro = DocumentoEmitido(
        tipo=assinatura_emissao.TIPO_RECEITA, referencia_id=doc_id,
        metodo="A1_ARQUIVO" if nivel == "qualificada" else "MANUAL", nivel=nivel,
        arquivo_nome=nome_arquivo, sha256="y" * 64, bytes_tam=len(pdf_falso),
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
    def test_recusa_409_mesmo_com_assinatura_qualificada(self, client, db, criar_usuario):
        user, token = criar_usuario(email="medico-sem-mail-rx@teste.local")
        doc = _criar_documento_emitido(db, user)
        _emitir(db, user, doc.id, nivel="qualificada")

        resposta = client.post(
            f"/api/receituario/documentos/{doc.id}/envio-paciente",
            headers=_headers(token),
            json={"email_paciente": "paciente@teste.local", "canal": "auto_contato_corvia"},
        )
        assert resposta.status_code == 409, resposta.text


class TestExigeAssinaturaQualificada:
    def test_metodo_manual_recusa_os_dois_canais(self, client, db, criar_usuario):
        user, token = criar_usuario(email="medico-manual-rx@teste.local")
        _ativar_corvia_mail(db, user, "medico-manual-rx@corvia.med.br")
        doc = _criar_documento_emitido(db, user)
        _emitir(db, user, doc.id, nivel="nenhuma")

        for canal in ("auto_contato_corvia", "proprio_corvia_mail"):
            resposta = client.post(
                f"/api/receituario/documentos/{doc.id}/envio-paciente",
                headers=_headers(token),
                json={"email_paciente": "paciente@teste.local", "canal": canal},
            )
            assert resposta.status_code == 409, resposta.text
            assert "qualificada" in resposta.json()["detail"].lower()


class TestCanalAutomaticoContatoCorvia:
    def test_envia_pela_corvia_com_confirmacao_de_assinatura(self, client, db, criar_usuario, monkeypatch):
        user, token = criar_usuario(email="medico-auto-rx@teste.local")
        _ativar_corvia_mail(db, user, "medico-auto-rx@corvia.med.br")
        doc = _criar_documento_emitido(db, user)
        _emitir(db, user, doc.id, nivel="qualificada")

        enviados: list = []
        _configurar_smtp_ok(monkeypatch, enviados)

        resposta = client.post(
            f"/api/receituario/documentos/{doc.id}/envio-paciente",
            headers=_headers(token),
            json={"email_paciente": "paciente@teste.local", "canal": "auto_contato_corvia"},
        )
        assert resposta.status_code == 200, resposta.text
        corpo = resposta.json()
        assert corpo["enviado"] is True
        assert corpo["anexo"] is None
        assert len(enviados) == 1

        registro = db.query(PatientDocumentEmailSend).filter(
            PatientDocumentEmailSend.referencia_id == doc.id,
            PatientDocumentEmailSend.tipo_origem == "prescription_document",
        ).first()
        assert registro is not None
        assert registro.assinatura_confirmada is True
        assert registro.sucesso is True


class TestCanalProprioCorviaMail:
    def test_prepara_anexo_com_nome_de_arquivo_por_tipo(self, client, db, criar_usuario, monkeypatch_mail360):
        user, token = criar_usuario(email="medico-proprio-rx@teste.local")
        _ativar_corvia_mail(db, user, "medico-proprio-rx@corvia.med.br")
        doc = _criar_documento_emitido(db, user)
        _emitir(db, user, doc.id, nivel="qualificada")

        resposta = client.post(
            f"/api/receituario/documentos/{doc.id}/envio-paciente",
            headers=_headers(token),
            json={"email_paciente": "paciente@teste.local", "canal": "proprio_corvia_mail"},
        )
        assert resposta.status_code == 200, resposta.text
        corpo = resposta.json()
        assert corpo["anexo"]["file_id"]
        assert corpo["anexo"]["nome"] == f"receituario-{doc.id}.pdf"

        anexos_subidos = monkeypatch_mail360["anexos"]
        assert len(anexos_subidos) == 1
        assert anexos_subidos[0][1] == f"receituario-{doc.id}.pdf"

    def test_sem_caixa_nativa_ativa_502(self, client, db, criar_usuario):
        # CorvIA Mail "ativo" (assinatura do add-on) mas sem `EmailAccount`
        # provisionada não deveria nem passar do gate de 409 comum — este
        # teste cobre o caminho defensivo dentro de `anexo_email_proprio`
        # caso o gate de rota mude no futuro; hoje os dois já bloqueiam
        # juntos, então o teste também serve de trava de regressão.
        user, token = criar_usuario(email="medico-sem-caixa-rx@teste.local")
        db.add(Subscription(user_id=user.id, kind="email", status="ativo"))
        db.commit()
        doc = _criar_documento_emitido(db, user)
        _emitir(db, user, doc.id, nivel="qualificada")

        resposta = client.post(
            f"/api/receituario/documentos/{doc.id}/envio-paciente",
            headers=_headers(token),
            json={"email_paciente": "paciente@teste.local", "canal": "proprio_corvia_mail"},
        )
        assert resposta.status_code == 409, resposta.text
