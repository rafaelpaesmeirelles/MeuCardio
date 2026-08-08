"""POST /api/material-paciente/{slug}/envio-paciente — mesma oferta de envio
ao paciente por e-mail do documento assinado, para Material ao Paciente
(pedido do Rafael, 08/08/2026), SEM exigir assinatura digital (este material
não é documento clínico assinado).
"""
from app.models.email_account import EmailAccount
from app.models.patient_document_email_send import PatientDocumentEmailSend
from app.models.patient_material import PatientMaterial
from app.models.subscription import Subscription


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


def _material(db, slug: str) -> PatientMaterial:
    m = PatientMaterial(
        slug=slug, titulo="Fibrilação atrial — o que você precisa saber",
        tema="Arritmias", secoes=[{"titulo": "O que é", "paragrafos": ["Texto."], "itens": []}],
        published=True, review_status="revisado",
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


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
    def test_recusa_409(self, client, db, criar_usuario):
        user, token = criar_usuario(email="medico-sem-mail-mat@teste.local")
        m = _material(db, "fibrilacao-atrial-teste-sem-mail")

        resposta = client.post(
            f"/api/material-paciente/{m.slug}/envio-paciente",
            headers=_headers(token),
            json={
                "email_paciente": "paciente@teste.local", "nome_paciente": "Paciente Teste",
                "consentimento": True, "canal": "auto_contato_corvia",
            },
        )
        assert resposta.status_code == 409, resposta.text


class TestConsentimentoObrigatorio:
    def test_sem_consentimento_422(self, client, db, criar_usuario):
        user, token = criar_usuario(email="medico-consent-mat@teste.local")
        _ativar_corvia_mail(db, user, "medico-consent-mat@corvia.med.br")
        m = _material(db, "fibrilacao-atrial-teste-consentimento")

        resposta = client.post(
            f"/api/material-paciente/{m.slug}/envio-paciente",
            headers=_headers(token),
            json={
                "email_paciente": "paciente@teste.local", "nome_paciente": "Paciente Teste",
                "consentimento": False, "canal": "auto_contato_corvia",
            },
        )
        assert resposta.status_code == 422, resposta.text


class TestCanalAutomaticoContatoCorvia:
    def test_envia_pela_corvia_sem_assinatura_exigida(self, client, db, criar_usuario, monkeypatch):
        user, token = criar_usuario(email="medico-auto-mat@teste.local")
        _ativar_corvia_mail(db, user, "medico-auto-mat@corvia.med.br")
        m = _material(db, "fibrilacao-atrial-teste-auto")

        enviados: list = []
        _configurar_smtp_ok(monkeypatch, enviados)

        resposta = client.post(
            f"/api/material-paciente/{m.slug}/envio-paciente",
            headers=_headers(token),
            json={
                "email_paciente": "paciente@teste.local", "nome_paciente": "Paciente Teste",
                "recado": "Leia com calma.", "consentimento": True, "canal": "auto_contato_corvia",
            },
        )
        assert resposta.status_code == 200, resposta.text
        corpo = resposta.json()
        assert corpo["enviado"] is True
        assert corpo["anexo"] is None
        assert len(enviados) == 1

        registro = db.query(PatientDocumentEmailSend).filter(
            PatientDocumentEmailSend.referencia_id == m.id,
            PatientDocumentEmailSend.tipo_origem == "patient_material",
        ).first()
        assert registro is not None
        assert registro.assinatura_confirmada is False
        assert registro.sucesso is True


class TestCanalProprioCorviaMail:
    def test_anexa_pdf_do_material_de_verdade(self, client, db, criar_usuario, monkeypatch_mail360):
        user, token = criar_usuario(email="medico-proprio-mat@teste.local")
        _ativar_corvia_mail(db, user, "medico-proprio-mat@corvia.med.br")
        m = _material(db, "fibrilacao-atrial-teste-proprio")

        resposta = client.post(
            f"/api/material-paciente/{m.slug}/envio-paciente",
            headers=_headers(token),
            json={
                "email_paciente": "paciente@teste.local", "nome_paciente": "Paciente Teste",
                "consentimento": True, "canal": "proprio_corvia_mail",
            },
        )
        assert resposta.status_code == 200, resposta.text
        corpo = resposta.json()
        assert corpo["anexo"]["file_id"]
        assert corpo["enviado"] is None

        anexos_subidos = monkeypatch_mail360["anexos"]
        assert len(anexos_subidos) == 1
        # PDF real do material — não é link nem string vazia.
        assert anexos_subidos[0][2] > 0  # tamanho do conteúdo subido


class TestLimiteDiario:
    def test_limite_diario_bloqueia_com_429(self, client, db, criar_usuario, monkeypatch):
        from app.api import exportacao

        user, token = criar_usuario(email="medico-limite-mat@teste.local")
        _ativar_corvia_mail(db, user, "medico-limite-mat@corvia.med.br")
        m = _material(db, "fibrilacao-atrial-teste-limite")

        monkeypatch.setattr(exportacao, "LIMITE_DESTINATARIOS_DIA", 1)
        enviados: list = []
        _configurar_smtp_ok(monkeypatch, enviados)

        primeiro = client.post(
            f"/api/material-paciente/{m.slug}/envio-paciente",
            headers=_headers(token),
            json={
                "email_paciente": "paciente1@teste.local", "nome_paciente": "Paciente 1",
                "consentimento": True, "canal": "auto_contato_corvia",
            },
        )
        assert primeiro.status_code == 200, primeiro.text

        segundo = client.post(
            f"/api/material-paciente/{m.slug}/envio-paciente",
            headers=_headers(token),
            json={
                "email_paciente": "paciente2@teste.local", "nome_paciente": "Paciente 2",
                "consentimento": True, "canal": "auto_contato_corvia",
            },
        )
        assert segundo.status_code == 429, segundo.text
