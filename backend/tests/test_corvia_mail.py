"""Testes automatizados do CorvIA Mail (Tarefa 28/29) — cobrem o roteiro que
a sessão de 30/07/2026 validou manualmente e descreveu em
`BRIEFING_CLAUDE_CODE_4.md` ("Nenhum teste automatizado foi commitado"),
agora commitado. Rodar com Postgres real (ver `tests/README.md`).
"""
from datetime import datetime, timedelta, timezone

from app.core.security import create_access_token
from app.models.email_account import EmailAccount
from app.models.password_reset import PasswordResetToken
from app.models.subscription import TIPO_EMAIL, Subscription


def _dar_assinatura_email_ativa(db, user, status="ativo"):
    sub = Subscription(user_id=user.id, kind=TIPO_EMAIL, status=status)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def _ativar_caixa(client, db, user, monkeypatch_mail360, senha="senha-caixa-123", local_part=None):
    _dar_assinatura_email_ativa(db, user)
    token = create_access_token(user.email, scope="app")
    if local_part is None:
        sugestao = client.get("/api/email/sugestao-endereco", headers={"Authorization": f"Bearer {token}"})
        local_part = sugestao.json()["local_part"]
    resp = client.post(
        "/api/email/conta",
        json={"senha": senha, "aceite_lgpd": True, "local_part": local_part},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# GET/POST /api/email/conta — status e ativação (current_user)
# ---------------------------------------------------------------------------

class TestStatusEAtivacao:
    def test_status_sem_caixa_nem_assinatura(self, client, criar_usuario):
        user, token = criar_usuario()
        resp = client.get("/api/email/conta", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json() == {"ativa": False, "assinatura_ativa": False}

    def test_ativar_sem_assinatura_devolve_409(self, client, criar_usuario):
        user, token = criar_usuario()
        resp = client.post(
            "/api/email/conta",
            json={"senha": "senha-longa-123", "aceite_lgpd": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 409
        assert "Assine" in resp.json()["detail"]

    def test_ativar_senha_curta_devolve_422(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_email_ativa(db, user)
        resp = client.post(
            "/api/email/conta",
            json={"senha": "curta", "aceite_lgpd": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

    def test_ativar_sem_aceite_lgpd_devolve_422(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_email_ativa(db, user)
        resp = client.post(
            "/api/email/conta",
            json={"senha": "senha-longa-123", "aceite_lgpd": False},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422
        assert "termo de transferência internacional" in resp.json()["detail"]

    def test_ativar_com_assinatura_ativa_cria_caixa(self, client, db, criar_usuario, monkeypatch_mail360):
        user, token = criar_usuario(full_name="Rafael Paes Meirelles")
        corpo = _ativar_caixa(client, db, user, monkeypatch_mail360)
        assert corpo["ativa"] is True
        assert corpo["ja_existia"] is False
        assert corpo["email_address"] == "rafael.paes@corvia.med.br"
        # o gerador de endereço foi de fato chamado com o nome do médico
        assert monkeypatch_mail360["contas_criadas"] == [
            ("rafael.paes@corvia.med.br", "Rafael Paes Meirelles"),
        ]
        conta = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
        assert conta is not None
        assert conta.password_hash is not None
        assert conta.lgpd_aceite_versao is not None

    def test_ativar_duas_vezes_atualiza_senha_sem_recriar_conta(self, client, db, criar_usuario, monkeypatch_mail360):
        user, token = criar_usuario()
        _ativar_caixa(client, db, user, monkeypatch_mail360, senha="senha-original-1")
        resp = client.post(
            "/api/email/conta",
            json={"senha": "senha-nova-outra-2", "aceite_lgpd": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        assert resp.json()["ja_existia"] is True
        # só uma conta foi criada no Mail360 nas duas chamadas
        assert len(monkeypatch_mail360["contas_criadas"]) == 1
        # e a senha nova já vale para login (ver TestLoginEmail mais abaixo
        # para a asserção completa do fluxo de login)

    def test_enderecos_duplicados_ganham_sufixo_numerico(self, client, db, criar_usuario, monkeypatch_mail360):
        u1, _ = criar_usuario(email="a@teste.local", full_name="Ana Souza")
        u2, _ = criar_usuario(email="b@teste.local", full_name="Ana Souza")
        c1 = _ativar_caixa(client, db, u1, monkeypatch_mail360)
        c2 = _ativar_caixa(client, db, u2, monkeypatch_mail360)
        assert c1["email_address"] == "ana.souza@corvia.med.br"
        assert c2["email_address"] == "ana.souza2@corvia.med.br"

    def test_status_apos_ativacao_reporta_ativa(self, client, db, criar_usuario, monkeypatch_mail360):
        user, token = criar_usuario()
        _ativar_caixa(client, db, user, monkeypatch_mail360)
        resp = client.get("/api/email/conta", headers={"Authorization": f"Bearer {token}"})
        corpo = resp.json()
        assert corpo["ativa"] is True
        assert corpo["status"] == "ativa"
        assert corpo["senha_definida"] is True

    def test_ativar_sem_local_part_devolve_422(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_email_ativa(db, user)
        resp = client.post(
            "/api/email/conta",
            json={"senha": "senha-longa-123", "aceite_lgpd": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

    def test_ativar_com_local_part_invalido_devolve_422(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_email_ativa(db, user)
        # "MAIUSCULO" não entra aqui: maiúscula é normalizada para minúscula
        # (mesmo padrão de POST /entrar), não é formato inválido — ver
        # test_ativar_normaliza_maiusculas_no_local_part.
        for invalido in ["ab", "-comeca-com-hifen", "tem espaço", "ponto.no.fim."]:
            resp = client.post(
                "/api/email/conta",
                json={"senha": "senha-longa-123", "aceite_lgpd": True, "local_part": invalido},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 422, f"'{invalido}' deveria ter sido rejeitado"

    def test_ativar_normaliza_maiusculas_no_local_part(self, client, db, criar_usuario, monkeypatch_mail360):
        user, token = criar_usuario(full_name="Ana Souza")
        corpo = _ativar_caixa(client, db, user, monkeypatch_mail360, local_part="ANA.CUSTOM")
        assert corpo["email_address"] == "ana.custom@corvia.med.br"

    def test_ativar_com_local_part_ja_em_uso_devolve_422(self, client, db, criar_usuario, monkeypatch_mail360):
        u1, _ = criar_usuario(email="a@teste.local")
        u2, token2 = criar_usuario(email="b@teste.local")
        _ativar_caixa(client, db, u1, monkeypatch_mail360, local_part="caixa-compartilhada")
        _dar_assinatura_email_ativa(db, u2)
        resp = client.post(
            "/api/email/conta",
            json={"senha": "senha-longa-123", "aceite_lgpd": True, "local_part": "caixa-compartilhada"},
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert resp.status_code == 422
        assert "em uso" in resp.json()["detail"]


class TestTelaDeCadastroDoEndereco:
    def test_sugestao_antes_de_ativar(self, client, criar_usuario):
        user, token = criar_usuario(full_name="Rafael Paes Meirelles")
        resp = client.get("/api/email/sugestao-endereco", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        corpo = resp.json()
        assert corpo["local_part"] == "rafael.paes"
        assert corpo["dominio"] == "corvia.med.br"
        assert corpo["editavel"] is True

    def test_sugestao_apos_ativar_devolve_endereco_real_nao_editavel(
        self, client, db, criar_usuario, monkeypatch_mail360,
    ):
        user, token = criar_usuario(full_name="Rafael Paes Meirelles")
        _ativar_caixa(client, db, user, monkeypatch_mail360, local_part="rafael.custom")
        resp = client.get("/api/email/sugestao-endereco", headers={"Authorization": f"Bearer {token}"})
        corpo = resp.json()
        assert corpo["local_part"] == "rafael.custom"
        assert corpo["editavel"] is False

    def test_verificar_endereco_disponivel(self, client, criar_usuario):
        user, token = criar_usuario()
        resp = client.get(
            "/api/email/verificar-endereco", params={"local": "endereco.livre"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        corpo = resp.json()
        assert corpo["disponivel"] is True
        assert corpo["motivo"] is None
        assert corpo["endereco"] == "endereco.livre@corvia.med.br"

    def test_verificar_endereco_formato_invalido(self, client, criar_usuario):
        user, token = criar_usuario()
        resp = client.get(
            "/api/email/verificar-endereco", params={"local": "ab"},
            headers={"Authorization": f"Bearer {token}"},
        )
        corpo = resp.json()
        assert corpo["disponivel"] is False
        assert corpo["motivo"] is not None

    def test_verificar_endereco_ja_em_uso(self, client, db, criar_usuario, monkeypatch_mail360):
        user, token1 = criar_usuario(email="a@teste.local")
        _, token2 = criar_usuario(email="b@teste.local")
        _ativar_caixa(client, db, user, monkeypatch_mail360, local_part="endereco.tomado")
        resp = client.get(
            "/api/email/verificar-endereco", params={"local": "endereco.tomado"},
            headers={"Authorization": f"Bearer {token2}"},
        )
        corpo = resp.json()
        assert corpo["disponivel"] is False
        assert "em uso" in corpo["motivo"]

    def test_verificar_endereco_normaliza_maiusculas(self, client, criar_usuario):
        user, token = criar_usuario()
        resp = client.get(
            "/api/email/verificar-endereco", params={"local": "Endereco.Livre"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.json()["endereco"] == "endereco.livre@corvia.med.br"


# ---------------------------------------------------------------------------
# Isolamento de escopo do token — o ponto central da Tarefa 28
# ---------------------------------------------------------------------------

class TestIsolamentoDeEscopo:
    def test_token_da_conta_principal_nao_abre_pastas(self, client, db, criar_usuario, monkeypatch_mail360):
        user, token_app = criar_usuario()
        _ativar_caixa(client, db, user, monkeypatch_mail360)
        resp = client.get("/api/email/pastas", headers={"Authorization": f"Bearer {token_app}"})
        assert resp.status_code == 401

    def test_token_da_caixa_de_email_nao_abre_auth_me(self, client, db, criar_usuario, monkeypatch_mail360):
        user, _ = criar_usuario()
        _ativar_caixa(client, db, user, monkeypatch_mail360, senha="senha-caixa-999")
        login = client.post("/api/email/entrar", json={
            "endereco": db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first().email_address,
            "senha": "senha-caixa-999",
        })
        token_email = login.json()["access_token"]
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_email}"})
        assert resp.status_code == 401

    def test_token_sem_scope_antigo_continua_valendo_como_app(self, client, criar_usuario):
        """Token emitido antes da mudança de 30/07/2026 não tem `scope` no
        payload — precisa continuar valendo como 'app' (ver `_decodificar`),
        senão todo mundo logado no momento do deploy seria deslogado."""
        import jwt

        from app.core.config import settings

        user, _ = criar_usuario()
        payload = {
            "sub": user.email,
            "exp": datetime.now(timezone.utc).timestamp() + 3600,
        }
        token_sem_scope = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_sem_scope}"})
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /api/email/entrar — login da "sessão email"
# ---------------------------------------------------------------------------

class TestLoginEmail:
    def test_login_com_senha_correta(self, client, db, criar_usuario, monkeypatch_mail360):
        user, _ = criar_usuario()
        _ativar_caixa(client, db, user, monkeypatch_mail360, senha="senha-caixa-correta")
        endereco = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first().email_address
        resp = client.post("/api/email/entrar", json={"endereco": endereco, "senha": "senha-caixa-correta"})
        assert resp.status_code == 200
        corpo = resp.json()
        assert corpo["token_type"] == "bearer"
        assert corpo["access_token"]

    def test_login_com_senha_errada_devolve_401(self, client, db, criar_usuario, monkeypatch_mail360):
        user, _ = criar_usuario()
        _ativar_caixa(client, db, user, monkeypatch_mail360, senha="senha-caixa-correta")
        endereco = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first().email_address
        resp = client.post("/api/email/entrar", json={"endereco": endereco, "senha": "senha-errada"})
        assert resp.status_code == 401

    def test_login_com_endereco_inexistente_devolve_401_nao_404(self, client):
        """401 genérico, não 404 — não confirmar pra quem pergunta se um
        endereço existe (mesma lógica anti-enumeração do resto do sistema)."""
        resp = client.post("/api/email/entrar", json={
            "endereco": "ninguem@corvia.med.br", "senha": "qualquer-coisa",
        })
        assert resp.status_code == 401

    def test_login_maiusculas_e_espacos_sao_normalizados(self, client, db, criar_usuario, monkeypatch_mail360):
        user, _ = criar_usuario()
        _ativar_caixa(client, db, user, monkeypatch_mail360, senha="senha-caixa-correta")
        endereco = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first().email_address
        resp = client.post("/api/email/entrar", json={
            "endereco": f"  {endereco.upper()}  ", "senha": "senha-caixa-correta",
        })
        assert resp.status_code == 200

    def test_login_em_caixa_suspensa_devolve_403(self, client, db, criar_usuario, monkeypatch_mail360):
        user, _ = criar_usuario()
        _ativar_caixa(client, db, user, monkeypatch_mail360, senha="senha-caixa-correta")
        conta = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
        conta.status = "suspensa"
        db.commit()
        resp = client.post("/api/email/entrar", json={
            "endereco": conta.email_address, "senha": "senha-caixa-correta",
        })
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Esqueci a senha da caixa — reaproveita PasswordResetToken.alvo == "email"
# ---------------------------------------------------------------------------

class TestEsqueciSenhaDaCaixa:
    def test_gera_token_com_alvo_email_sem_mexer_na_senha_da_conta(self, client, db, criar_usuario, monkeypatch_mail360):
        user, _ = criar_usuario()
        _ativar_caixa(client, db, user, monkeypatch_mail360)
        conta = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
        senha_conta_antes = user.password_hash

        resp = client.post("/api/email/esqueci-senha", json={"endereco": conta.email_address})
        assert resp.status_code == 202

        token = db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).first()
        assert token is not None
        assert token.alvo == "email"
        db.refresh(user)
        assert user.password_hash == senha_conta_antes  # nada mudou na conta principal ainda

    def test_endereco_inexistente_tambem_devolve_202(self, client):
        """Mesma defesa anti-enumeração do `esqueci-senha` da conta principal."""
        resp = client.post("/api/email/esqueci-senha", json={"endereco": "ninguem@corvia.med.br"})
        assert resp.status_code == 202

    def test_redefinir_com_token_alvo_email_troca_senha_da_caixa_nao_da_conta(
        self, client, db, criar_usuario, monkeypatch_mail360,
    ):
        user, _ = criar_usuario()
        _ativar_caixa(client, db, user, monkeypatch_mail360, senha="senha-original-caixa")
        conta = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
        senha_conta_antes = user.password_hash

        client.post("/api/email/esqueci-senha", json={"endereco": conta.email_address})
        token = db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).first()

        resp = client.post("/api/auth/redefinir-senha", json={
            "token": token.token, "nova_senha": "senha-nova-da-caixa-123",
        })
        assert resp.status_code == 200

        db.refresh(user)
        assert user.password_hash == senha_conta_antes  # senha da CONTA intocada

        login_com_senha_nova = client.post("/api/email/entrar", json={
            "endereco": conta.email_address, "senha": "senha-nova-da-caixa-123",
        })
        assert login_com_senha_nova.status_code == 200

        login_com_senha_antiga = client.post("/api/email/entrar", json={
            "endereco": conta.email_address, "senha": "senha-original-caixa",
        })
        assert login_com_senha_antiga.status_code == 401

    def test_token_usado_nao_pode_ser_reutilizado(self, client, db, criar_usuario, monkeypatch_mail360):
        user, _ = criar_usuario()
        _ativar_caixa(client, db, user, monkeypatch_mail360)
        conta = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
        client.post("/api/email/esqueci-senha", json={"endereco": conta.email_address})
        token = db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).first()

        primeira = client.post("/api/auth/redefinir-senha", json={
            "token": token.token, "nova_senha": "senha-nova-1234",
        })
        assert primeira.status_code == 200

        segunda = client.post("/api/auth/redefinir-senha", json={
            "token": token.token, "nova_senha": "outra-senha-5678",
        })
        assert segunda.status_code == 400


# ---------------------------------------------------------------------------
# Pastas, mensagens e anexos — exigem current_email_account
# ---------------------------------------------------------------------------

class TestPastasEMensagens:
    def _token_email(self, client, db, user, monkeypatch_mail360, senha="senha-caixa-123"):
        _ativar_caixa(client, db, user, monkeypatch_mail360, senha=senha)
        endereco = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first().email_address
        login = client.post("/api/email/entrar", json={"endereco": endereco, "senha": senha})
        return login.json()["access_token"], endereco

    def test_pastas_sem_token_devolve_401(self, client):
        assert client.get("/api/email/pastas").status_code == 401

    def test_pastas_com_token_valido(self, client, db, criar_usuario, monkeypatch_mail360):
        user, _ = criar_usuario()
        token, _ = self._token_email(client, db, user, monkeypatch_mail360)
        resp = client.get("/api/email/pastas", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()[0]["name"] == "Inbox"

    def test_mensagens_com_token_valido(self, client, db, criar_usuario, monkeypatch_mail360):
        user, _ = criar_usuario()
        token, _ = self._token_email(client, db, user, monkeypatch_mail360)
        resp = client.get("/api/email/mensagens?pasta=Inbox", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()[0]["messageId"] == "msg-1"

    def test_enviar_mensagem(self, client, db, criar_usuario, monkeypatch_mail360):
        user, _ = criar_usuario()
        token, endereco = self._token_email(client, db, user, monkeypatch_mail360)
        resp = client.post(
            "/api/email/mensagens",
            json={"para": "destinatario@example.com", "assunto": "Oi", "corpo_html": "<p>Oi</p>", "anexos": []},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        assert monkeypatch_mail360["mensagens_enviadas"][0]["para"] == "destinatario@example.com"

    def test_upload_anexo_dentro_do_limite(self, client, db, criar_usuario, monkeypatch_mail360):
        user, _ = criar_usuario()
        token, _ = self._token_email(client, db, user, monkeypatch_mail360)
        resp = client.post(
            "/api/email/mensagens/anexos",
            files={"arquivo": ("relatorio.pdf", b"conteudo pequeno", "application/pdf")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        assert resp.json()["file_id"] == "file-id-1"

    def test_upload_anexo_acima_do_limite_devolve_413(self, client, db, criar_usuario, monkeypatch_mail360):
        user, _ = criar_usuario()
        token, _ = self._token_email(client, db, user, monkeypatch_mail360)
        conteudo_grande = b"x" * (15 * 1024 * 1024 + 1)
        resp = client.post(
            "/api/email/mensagens/anexos",
            files={"arquivo": ("grande.bin", conteudo_grande, "application/octet-stream")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 413

    def test_enviar_mensagem_encaminha_ids_de_anexo(self, client, db, criar_usuario, monkeypatch_mail360):
        user, _ = criar_usuario()
        token, _ = self._token_email(client, db, user, monkeypatch_mail360)
        upload = client.post(
            "/api/email/mensagens/anexos",
            files={"arquivo": ("laudo.pdf", b"conteudo", "application/pdf")},
            headers={"Authorization": f"Bearer {token}"},
        )
        file_id = upload.json()["file_id"]
        resp = client.post(
            "/api/email/mensagens",
            json={"para": "x@example.com", "assunto": "Anexo", "corpo_html": "<p>Segue</p>", "anexos": [file_id]},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        assert monkeypatch_mail360["mensagens_enviadas"][-1]["anexos"] == [file_id]

    def test_excluir_mensagem(self, client, db, criar_usuario, monkeypatch_mail360):
        user, _ = criar_usuario()
        token, _ = self._token_email(client, db, user, monkeypatch_mail360)
        resp = client.delete("/api/email/mensagens/msg-1", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 204


# ---------------------------------------------------------------------------
# Sincronização assinatura -> caixa (o bug de roteamento por `tipo` no
# webhook, documentado no CLAUDE.md como já tendo acontecido uma vez com
# `mode` em vez de metadata) — testado direto na função, sem depender de
# assinatura HTTP do Stripe.
# ---------------------------------------------------------------------------

class TestSincronizacaoAssinaturaCaixa:
    def test_evento_de_assinatura_de_email_nao_vira_assinatura_da_plataforma(self, client, db, criar_usuario):
        """Reproduz o cenário do bug já documentado: primeiro evento de
        webhook de uma assinatura nova, sem `stripe_subscription_id` gravado
        ainda, casado só pelo `customer` + `metadata.tipo`."""
        from app.api.billing import _aplicar_evento, traduzir_status

        user, _ = criar_usuario()
        sub_email = Subscription(user_id=user.id, kind=TIPO_EMAIL, stripe_customer_id="cus_123", status="inativo")
        sub_meucardio = Subscription(
            user_id=user.id, kind="meucardio", stripe_customer_id="cus_123", status="inativo",
        )
        db.add_all([sub_email, sub_meucardio])
        db.commit()

        evento_stripe = {
            "id": "sub_stripe_1",
            "customer": "cus_123",
            "status": "active",
            "metadata": {"tipo": "email", "user_id": str(user.id)},
            "items": {"data": []},
        }

        def alterar(sub):
            sub.stripe_subscription_id = evento_stripe["id"]
            sub.status = traduzir_status(evento_stripe["status"])

        _aplicar_evento(db, evento_stripe, datetime.now(timezone.utc), alterar)

        db.refresh(sub_email)
        db.refresh(sub_meucardio)
        assert sub_email.status == "ativo"
        assert sub_email.stripe_subscription_id == "sub_stripe_1"
        # a assinatura da PLATAFORMA, mesmo cliente Stripe, não foi tocada
        assert sub_meucardio.status == "inativo"
        assert sub_meucardio.stripe_subscription_id is None

    def test_cancelamento_da_assinatura_de_email_suspende_a_caixa(self, client, db, criar_usuario, monkeypatch_mail360):
        from app.api.billing import _aplicar_evento

        user, _ = criar_usuario()
        _ativar_caixa(client, db, user, monkeypatch_mail360, senha="senha-caixa-123")
        sub = db.query(Subscription).filter(Subscription.user_id == user.id, Subscription.kind == TIPO_EMAIL).first()
        sub.stripe_subscription_id = "sub_stripe_2"
        db.commit()

        evento_cancelamento = {"id": "sub_stripe_2", "customer": sub.stripe_customer_id}
        _aplicar_evento(db, evento_cancelamento, datetime.now(timezone.utc), lambda s: setattr(s, "status", "cancelado"))

        conta = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
        assert conta.status == "suspensa"

        login_bloqueado = client.post("/api/email/entrar", json={
            "endereco": conta.email_address, "senha": "senha-caixa-123",
        })
        assert login_bloqueado.status_code == 403

    def test_evento_atrasado_nao_desfaz_estado_mais_novo(self, client, db, criar_usuario, monkeypatch_mail360):
        """`last_event_at` existe exatamente para isto: o Stripe não garante
        ordem de entrega, então um evento de cancelamento atrasado não pode
        reverter uma reativação que já chegou depois dele."""
        from app.api.billing import _aplicar_evento

        user, _ = criar_usuario()
        _ativar_caixa(client, db, user, monkeypatch_mail360, senha="senha-caixa-123")
        sub = db.query(Subscription).filter(Subscription.user_id == user.id, Subscription.kind == TIPO_EMAIL).first()
        sub.stripe_subscription_id = "sub_stripe_3"
        db.commit()

        agora = datetime.now(timezone.utc)
        evento_reativacao = {"id": "sub_stripe_3", "customer": sub.stripe_customer_id}
        _aplicar_evento(db, evento_reativacao, agora, lambda s: setattr(s, "status", "ativo"))

        evento_cancelamento_atrasado = {"id": "sub_stripe_3", "customer": sub.stripe_customer_id}
        momento_anterior = agora.replace(microsecond=0) - timedelta(minutes=5)
        _aplicar_evento(
            db, evento_cancelamento_atrasado, momento_anterior, lambda s: setattr(s, "status", "cancelado"),
        )

        db.refresh(sub)
        assert sub.status == "ativo"


# ---------------------------------------------------------------------------
# Checkout do add-on — preço em branco recusa, nunca cobra valor inventado
# ---------------------------------------------------------------------------

class TestCheckoutEmail:
    def test_preco_indefinido_devolve_409(self, client, criar_usuario, monkeypatch):
        from app.core.config import settings

        monkeypatch.setattr(settings, "corvia_mail_preco_centavos", 0)
        user, token = criar_usuario()
        resp = client.post("/api/billing/checkout-email", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 409

    def test_status_email_reporta_preco_definido(self, client, criar_usuario):
        user, token = criar_usuario()
        resp = client.get("/api/billing/status-email", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        corpo = resp.json()
        assert corpo["preco_definido"] is True
        assert corpo["preco_centavos"] == 1000
        assert corpo["status"] == "inativo"

    def test_ja_assinante_devolve_409_no_checkout(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_email_ativa(db, user, status="ativo")
        resp = client.post("/api/billing/checkout-email", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 409
        assert "já assina" in resp.json()["detail"]
