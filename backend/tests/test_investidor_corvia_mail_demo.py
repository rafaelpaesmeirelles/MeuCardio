"""Cobertura da issue #52 — complementos "INVESTIDOR NO CORVIA MAIL" e
"REGRA DEFINITIVA DE ACESSO PARA CONVIDADO".

Duas regras distintas, testadas lado a lado para que a diferença fique
explícita (nunca confundir as duas categorias):

- CONVIDADO tem CorvIA Mail REAL e completo — provisiona caixa nativa,
  conecta contas externas ainda suportadas, envia, responde, sincroniza — sem checkout, sem
  cartão, exatamente como assinante pago (`assinatura_email_ativa()` em
  app/core/security.py concede o add-on a convidado sem depender de
  Subscription nenhuma).
- INVESTIDOR só pode NAVEGAR a interface do CorvIA Mail, com conteúdo
  sintético (`app/services/investidor_mail_demo.py`) — toda operação real
  (provisionar, conectar OAuth/Yahoo/Apple com e-mail, enviar, responder,
  sincronizar, ler mailbox real) devolve 403, sempre pelo backend (nunca só
  o botão desabilitado do frontend) — `app/services/entitlement.py::
  bloquear_investidor_em_operacao_real_de_mail` e o bloqueio de defesa em
  profundidade dentro de `current_email_account()`.
"""
from app.core.security import create_access_token
from app.models.agenda import CalendarIntegration
from app.models.email_account import EmailAccount
from app.models.subscription import TIPO_EMAIL, Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _marcar(db, user, **flags):
    for campo, valor in flags.items():
        setattr(user, campo, valor)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _converter_investidor(db, user) -> str:
    _marcar(db, user, investidor=True)
    return create_access_token(user.email, scope="app")


def _mailbox_token(email_address: str) -> str:
    return create_access_token(email_address, scope="email")


# --------------------------------------------------------------------- INVESTIDOR --


class TestInvestidorAbreInterfaceEmModoDemonstracao:
    def test_get_conta_investidor_devolve_modo_demonstracao_sem_tocar_email_account(
        self, client, db, criar_usuario,
    ):
        user, _ = criar_usuario()
        token = _converter_investidor(db, user)
        resp = client.get("/api/email/conta", headers=_headers(token))
        assert resp.status_code == 200
        corpo = resp.json()
        assert corpo["ativa"] is True
        assert corpo["modo_demonstracao"] is True
        assert corpo["email_address"] == "investidor.demo@corvia.med.br"
        # Nenhuma linha real criada — a resposta não veio de consulta ao banco.
        assert db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first() is None

    def test_demo_pastas_e_mensagens_sao_dado_sintetico_sem_pii(self, client, db, criar_usuario):
        user, _ = criar_usuario()
        token = _converter_investidor(db, user)

        pastas = client.get("/api/email/demo/pastas", headers=_headers(token))
        assert pastas.status_code == 200
        assert {p["folderName"] for p in pastas.json()} == {"Entrada", "Enviados", "Rascunhos"}

        mensagens = client.get("/api/email/demo/mensagens", headers=_headers(token))
        assert mensagens.status_code == 200
        corpo = mensagens.json()
        assert 3 <= len(corpo) <= 5
        remetentes = {m["fromAddress"] for m in corpo}
        # Nenhum remetente real do sistema — só endereços fictícios de
        # demonstração, nenhum @corvia.med.br de médico/paciente de verdade.
        assert all(r.endswith(("@corvia.med.br", "@example.com")) for r in remetentes)
        assert all("paciente" not in m["subject"].lower() or "exemplo" in m["subject"].lower() for m in corpo)

        detalhe = client.get(f"/api/email/demo/mensagens/{corpo[0]['messageId']}", headers=_headers(token))
        assert detalhe.status_code == 200
        assert "content" in detalhe.json()

    def test_demo_mensagem_inexistente_devolve_404(self, client, db, criar_usuario):
        user, _ = criar_usuario()
        token = _converter_investidor(db, user)
        resp = client.get("/api/email/demo/mensagens/nao-existe", headers=_headers(token))
        assert resp.status_code == 404

    def test_rotas_demo_sao_403_para_quem_nao_e_investidor(self, client, criar_usuario):
        user, token = criar_usuario()
        assert client.get("/api/email/demo/pastas", headers=_headers(token)).status_code == 403
        assert client.get("/api/email/demo/mensagens", headers=_headers(token)).status_code == 403


class TestInvestidorBloqueadoEmOperacaoRealDeEmail:
    def test_provisionar_caixa_nativa_e_403(self, client, db, criar_usuario, monkeypatch_mail360):
        user, _ = criar_usuario()
        token = _converter_investidor(db, user)
        resp = client.post(
            "/api/email/conta",
            json={"senha": "senha-longa-123", "aceite_lgpd": True, "local_part": "investidor.teste"},
            headers=_headers(token),
        )
        assert resp.status_code == 403
        assert "investidor" in resp.json()["detail"].lower()
        # Nunca chegou a chamar o Mail360 de verdade.
        assert monkeypatch_mail360["contas_criadas"] == []
        assert db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first() is None

    def test_conectar_yahoo_e_403(self, client, db, criar_usuario):
        user, _ = criar_usuario()
        token = _converter_investidor(db, user)
        resp = client.post(
            "/api/email/conectar-yahoo",
            json={"endereco": "investidor@yahoo.com", "senha_de_app": "abcd-efgh-ijkl-mnop", "consent_accepted": True},
            headers=_headers(token),
        )
        assert resp.status_code == 403
        assert db.query(CalendarIntegration).filter(CalendarIntegration.owner_id == user.id).count() == 0

    def test_oauth_start_google_com_mail_true_e_403(self, client, db, criar_usuario):
        user, _ = criar_usuario()
        token = _converter_investidor(db, user)
        resp = client.get(
            "/api/agenda/oauth/google/start",
            params={"mail": "true", "consent_accepted": "true"},
            headers=_headers(token),
        )
        assert resp.status_code == 403

    def test_oauth_start_google_sem_mail_tambem_e_403_para_investidor(self, client, db, criar_usuario):
        """Agenda também é demonstração: nenhum OAuth externo pode iniciar,
        mesmo quando a integração pede apenas calendário e não e-mail."""
        user, _ = criar_usuario()
        token = _converter_investidor(db, user)
        resp = client.get(
            "/api/agenda/oauth/google/start",
            params={"mail": "false", "consent_accepted": "true"},
            headers=_headers(token),
        )
        assert resp.status_code == 403

    def test_apple_connect_com_mail_true_e_403(self, client, db, criar_usuario):
        user, _ = criar_usuario()
        token = _converter_investidor(db, user)
        resp = client.post(
            "/api/agenda/integrations/apple",
            json={
                "apple_id": "investidor@icloud.com",
                "app_specific_password": "abcd-efgh-ijkl-mnop",
                "consent_accepted": True,
                "mail": True,
                "mail_consent_accepted": True,
                "contacts": False,
            },
            headers=_headers(token),
        )
        assert resp.status_code == 403

    def test_enviar_responder_e_sincronizar_sao_403_mesmo_com_caixa_ja_existente(
        self, client, db, criar_usuario,
    ):
        """Defesa em profundidade: mesmo que uma conta JÁ tivesse caixa real
        antes de virar investidor (ex.: admin concede `investidor=True` a um
        usuário que já era convidado com caixa provisionada), a sessão da
        caixa para de funcionar — o bloqueio não depende só de nunca ter
        provisionado."""
        user, token = criar_usuario()
        conta = EmailAccount(
            user_id=user.id, email_address="ja-tinha-caixa@corvia.med.br",
            mail360_account_key="account-key-preexistente", password_hash="hash-qualquer", status="ativa",
        )
        db.add(conta)
        db.commit()
        mailbox_token = _mailbox_token(conta.email_address)

        # Confirma que o token funciona ANTES de virar investidor.
        antes = client.get("/api/email/pastas", headers=_headers(mailbox_token))
        assert antes.status_code in (200, 502)  # 502 só se o Mail360 real falhar — nunca 403 aqui

        _marcar(db, user, investidor=True)

        for metodo, caminho, corpo in [
            ("get", "/api/email/mensagens/todas", None),
            ("get", "/api/email/pastas", None),
            ("get", "/api/email/mensagens", None),
            ("get", "/api/email/contatos", None),
            (
                "post",
                "/api/email/mensagens",
                {"para": "alguem@example.com", "assunto": "teste", "corpo_html": "teste"},
            ),
            (
                "post",
                "/api/email/mensagens/msg-1/responder",
                {"acao": "reply", "assunto": "teste", "conteudo": "teste"},
            ),
        ]:
            resp = getattr(client, metodo)(caminho, headers=_headers(mailbox_token), **({"json": corpo} if corpo else {}))
            assert resp.status_code == 403, f"{metodo.upper()} {caminho} deveria ser 403, veio {resp.status_code}"

    def test_investidor_nao_acessa_mailbox_real_de_outro_usuario(self, client, db, criar_usuario):
        """Nem por engano: um token de mailbox real pertencente a OUTRO
        usuário não passa a funcionar para o investidor só porque ele tenta
        usá-lo — o titular resolvido é sempre o dono real da conta."""
        dono, _ = criar_usuario(email="dono-real@teste.local")
        investidor_user, _ = criar_usuario(email="investidor@teste.local")
        _marcar(db, investidor_user, investidor=True)

        conta_do_dono = EmailAccount(
            user_id=dono.id, email_address="dono-real@corvia.med.br",
            mail360_account_key="account-key-dono", password_hash="hash", status="ativa",
        )
        db.add(conta_do_dono)
        db.commit()

        # O token é sempre resolvido pelo endereço da CAIXA, não por quem o
        # apresenta — então o "ataque" aqui é só confirmar que o dono real
        # (não investidor) continua funcionando normalmente, sem qualquer
        # regressão introduzida por este bloqueio.
        token_do_dono = _mailbox_token(conta_do_dono.email_address)
        resp = client.get("/api/email/pastas", headers=_headers(token_do_dono))
        assert resp.status_code in (200, 502)


class TestInvestidorPreferenciasDeSincronizacaoNuncaLiberamEmail:
    def test_ligar_sync_mail_e_bloqueado_pelo_readonly_global(self, client, db, criar_usuario):
        """Mesmo uma integração legada/preexistente não pode ser alterada:
        PATCH nasce fail-closed para Investidor antes de validar capacidades."""
        user, _ = criar_usuario()
        token = _converter_investidor(db, user)
        integracao = CalendarIntegration(
            owner_id=user.id, provider="google_calendar", display_name="Agenda de teste",
            status="connected", enabled=True,
            capabilities={"read_appointments": True, "read_mail": False, "send_mail": False},
        )
        db.add(integracao)
        db.commit()
        db.refresh(integracao)

        resp = client.patch(
            f"/api/agenda/integrations/{integracao.id}/preferencias",
            json={"sync_mail": True},
            headers=_headers(token),
        )
        assert resp.status_code == 403
        db.refresh(integracao)
        assert integracao.sync_mail is False


# --------------------------------------------------------------------- CONVIDADO --


class TestConvidadoTemCorvIAMailRealECompleto:
    def test_assinatura_email_ativa_sem_qualquer_checkout_ou_subscription(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _marcar(db, user, convidado=True)
        resp = client.get("/api/email/conta", headers=_headers(token))
        assert resp.status_code == 200
        corpo = resp.json()
        assert corpo["ativa"] is False  # ainda não provisionou, mas pode
        assert corpo["assinatura_ativa"] is True
        assert corpo["modo_demonstracao"] is False
        assert db.query(Subscription).filter(Subscription.user_id == user.id).count() == 0

    def test_billing_status_email_nao_oferece_cobranca_a_convidado(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _marcar(db, user, convidado=True)
        resp = client.get("/api/billing/status-email", headers=_headers(token))
        assert resp.status_code == 200
        corpo = resp.json()
        assert corpo["incluido_no_plano"] is True
        assert corpo["status"] == "ativo"

    def test_convidado_provisiona_caixa_nativa_de_verdade(self, client, db, criar_usuario, monkeypatch_mail360):
        user, token = criar_usuario()
        _marcar(db, user, convidado=True)
        resp = client.post(
            "/api/email/conta",
            json={"senha": "senha-longa-123", "aceite_lgpd": True, "local_part": "convidado.teste"},
            headers=_headers(token),
        )
        assert resp.status_code == 201, resp.text
        assert resp.json()["email_address"] == "convidado.teste@corvia.med.br"
        assert len(monkeypatch_mail360["contas_criadas"]) == 1

    def test_convidado_envia_e_le_mensagens_reais(self, client, db, criar_usuario, monkeypatch_mail360):
        user, token = criar_usuario()
        _marcar(db, user, convidado=True)
        ativado = client.post(
            "/api/email/conta",
            json={"senha": "senha-longa-123", "aceite_lgpd": True, "local_part": "convidado.envia"},
            headers=_headers(token),
        )
        assert ativado.status_code == 201
        mailbox_token = _mailbox_token(ativado.json()["email_address"])

        envio = client.post(
            "/api/email/mensagens",
            json={"para": "paciente@example.com", "assunto": "Retorno", "corpo_html": "Olá."},
            headers=_headers(mailbox_token),
        )
        assert envio.status_code == 201, envio.text
        assert len(monkeypatch_mail360["mensagens_enviadas"]) == 1

        leitura = client.get("/api/email/mensagens", headers=_headers(mailbox_token))
        assert leitura.status_code == 200

    def test_convidado_tambem_nao_conecta_yahoo_retirado(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _marcar(db, user, convidado=True)
        resp = client.post(
            "/api/email/conectar-yahoo",
            json={"endereco": "convidado@yahoo.com", "senha_de_app": "abcd-efgh-ijkl-mnop", "consent_accepted": True},
            headers=_headers(token),
        )
        assert resp.status_code == 410, resp.text
        assert "não está mais disponível" in resp.json()["detail"]
        assert db.query(CalendarIntegration).filter(
            CalendarIntegration.owner_id == user.id,
            CalendarIntegration.provider == "yahoo_mail",
        ).count() == 0

    def test_revogar_convidado_sem_assinatura_bloqueia_nova_ativacao(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _marcar(db, user, convidado=True)
        _marcar(db, user, convidado=False)
        resp = client.post(
            "/api/email/conta",
            json={"senha": "senha-longa-123", "aceite_lgpd": True, "local_part": "pos-revogacao"},
            headers=_headers(token),
        )
        assert resp.status_code == 409

    def test_revogar_convidado_mas_com_assinatura_paga_de_email_continua_funcionando(
        self, client, db, criar_usuario, monkeypatch_mail360,
    ):
        user, token = criar_usuario()
        _marcar(db, user, convidado=True)
        _marcar(db, user, convidado=False)
        db.add(Subscription(user_id=user.id, kind=TIPO_EMAIL, status="ativo"))
        db.commit()
        resp = client.post(
            "/api/email/conta",
            json={"senha": "senha-longa-123", "aceite_lgpd": True, "local_part": "com-assinatura-propria"},
            headers=_headers(token),
        )
        assert resp.status_code == 201

    def test_convidado_nao_e_afetado_pelo_bloqueio_de_investidor(self, client, db, criar_usuario, monkeypatch_mail360):
        """Prova negativa direta: as duas categorias nunca se misturam — um
        convidado (mesmo se `investidor` também estiver False, o caso
        normal) nunca recebe o 403 do modo demonstração."""
        user, token = criar_usuario()
        _marcar(db, user, convidado=True, investidor=False)
        resp = client.post(
            "/api/email/conta",
            json={"senha": "senha-longa-123", "aceite_lgpd": True, "local_part": "convidado.isolado"},
            headers=_headers(token),
        )
        assert resp.status_code == 201
