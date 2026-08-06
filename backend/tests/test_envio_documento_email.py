"""app/services/envio_documento_email.py — roteamento do envio de
documento pela conta padrão do médico (nativa CorvIA Mail, Yahoo, iCloud,
Google, Microsoft), Trabalho 11 (ampliação de 06/08/2026).
"""
from app.models.agenda import CalendarIntegration
from app.models.email_account import EmailAccount
from app.services import envio_documento_email


def _conta_nativa(db, user) -> EmailAccount:
    conta = EmailAccount(
        user_id=user.id, email_address=f"{user.id}@corvia.med.br",
        mail360_account_key=f"key-{user.id}", status="ativa",
    )
    db.add(conta)
    db.commit()
    return conta


def _integracao(db, user, provider: str, *, send_mail=True) -> CalendarIntegration:
    integ = CalendarIntegration(
        owner_id=user.id, provider=provider, display_name=f"{user.id}@{provider}",
        external_account_id=f"{user.id}@{provider}", sync_strategy="external_authoritative",
        status="connected", enabled=True,
        capabilities={"read_mail": True, "send_mail": send_mail},
    )
    db.add(integ)
    db.commit()
    db.refresh(integ)
    return integ


class TestRoteamentoParaContaNativa:
    def test_sem_preferencia_gravada_usa_nativa(self, db, criar_usuario, monkeypatch):
        user, _ = criar_usuario()
        _conta_nativa(db, user)
        chamadas = []
        monkeypatch.setattr(
            envio_documento_email.mail360, "enviar_mensagem",
            lambda *a, **k: chamadas.append((a, k)),
        )
        resultado = envio_documento_email.enviar(
            db, user, destinatario="p@x.com", assunto="Assunto", corpo_html="<p>x</p>",
        )
        assert resultado.enviado is True
        assert resultado.assinado_smime is False
        assert len(chamadas) == 1

    def test_smime_pedido_na_nativa_e_ignorado_sem_erro(self, db, criar_usuario, monkeypatch):
        user, _ = criar_usuario()
        _conta_nativa(db, user)
        monkeypatch.setattr(envio_documento_email.mail360, "enviar_mensagem", lambda *a, **k: None)
        resultado = envio_documento_email.enviar(
            db, user, destinatario="p@x.com", assunto="a", corpo_html="<p>x</p>", assinar_smime=True,
        )
        assert resultado.enviado is True
        assert resultado.assinado_smime is False  # nunca finge que assinou

    def test_sem_conta_nativa_ativa_falha_com_mensagem_clara(self, db, criar_usuario):
        user, _ = criar_usuario()
        resultado = envio_documento_email.enviar(
            db, user, destinatario="p@x.com", assunto="a", corpo_html="<p>x</p>",
        )
        assert resultado.enviado is False
        assert "CorvIA Mail" in resultado.erro


class TestRoteamentoParaYahooEICloud:
    def test_conta_padrao_yahoo_honra_smime(self, db, criar_usuario, monkeypatch):
        user, _ = criar_usuario()
        integ = _integracao(db, user, "yahoo_mail")
        user.email_conta_padrao_envio = str(integ.id)
        db.commit()

        capturado = {}
        def _fake_send(credentials, *, to, subject, html, db, user, assinar_smime, **kw):
            capturado.update(assinar_smime=assinar_smime, to=to)
            return {"status": "sent", "assinado_smime": assinar_smime}
        monkeypatch.setattr(envio_documento_email.yahoo_mail, "send_message", _fake_send)

        resultado = envio_documento_email.enviar(
            db, user, destinatario="p@x.com", assunto="a", corpo_html="<p>x</p>", assinar_smime=True,
        )
        assert resultado.enviado is True
        assert resultado.assinado_smime is True
        assert capturado["assinar_smime"] is True

    def test_suporta_smime_verdadeiro_so_para_yahoo_apple(self, db, criar_usuario):
        user, _ = criar_usuario()
        integ = _integracao(db, user, "apple_icloud")
        user.email_conta_padrao_envio = str(integ.id)
        db.commit()
        assert envio_documento_email.suporta_smime(db, user) is True

    def test_conta_sem_permissao_de_envio_falha(self, db, criar_usuario):
        user, _ = criar_usuario()
        integ = _integracao(db, user, "yahoo_mail", send_mail=False)
        user.email_conta_padrao_envio = str(integ.id)
        db.commit()
        resultado = envio_documento_email.enviar(
            db, user, destinatario="p@x.com", assunto="a", corpo_html="<p>x</p>",
        )
        assert resultado.enviado is False


class TestRoteamentoParaGoogleEMicrosoft:
    def test_conta_padrao_microsoft_usa_external_mail_sem_smime(self, db, criar_usuario, monkeypatch):
        user, _ = criar_usuario()
        integ = _integracao(db, user, "microsoft_365")
        user.email_conta_padrao_envio = str(integ.id)
        db.commit()

        chamadas = []
        monkeypatch.setattr(
            envio_documento_email.external_mail, "send_message",
            lambda *a, **k: chamadas.append((a, k)),
        )
        resultado = envio_documento_email.enviar(
            db, user, destinatario="p@x.com", assunto="a", corpo_html="<p>x</p>", assinar_smime=True,
        )
        assert resultado.enviado is True
        assert resultado.assinado_smime is False  # Graph API não suporta — pedido é ignorado
        assert len(chamadas) == 1

    def test_suporta_smime_falso_para_google_microsoft(self, db, criar_usuario):
        user, _ = criar_usuario()
        integ = _integracao(db, user, "google_calendar")
        user.email_conta_padrao_envio = str(integ.id)
        db.commit()
        assert envio_documento_email.suporta_smime(db, user) is False
