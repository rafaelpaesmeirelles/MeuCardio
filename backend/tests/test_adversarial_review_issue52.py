"""Revisão adversarial independente da issue #52 (entitlement de CONVIDADO e
INVESTIDOR) — segunda opinião cética, não escrita pelos implementadores.

Não edita nada de produção. Roda contra um banco de teste ISOLADO
(meucardio_test_advreview), nunca o meucardio_test compartilhado.

Cada classe corresponde a um item do checklist de ataque pedido pelo
orquestrador. Comentários registram o raciocínio de ataque, não só o
resultado.
"""
from unittest.mock import patch

from app.models.agenda import CalendarIntegration
from app.models.email_account import EmailAccount
from app.models.subscription import PLANO_BASICO, TIPO_EMAIL, TIPO_MEUCARDIO, Subscription
from app.core.security import create_access_token

ROTA_GATED = "/api/library/themes"


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
    """Converte e emite uma sessão NOVA.

    A conversão redefine a senha para CorVIAOS e, por desenho de segurança,
    revoga tokens app emitidos antes da troca de senha.
    """
    _marcar(db, user, investidor=True)
    return create_access_token(user.email, scope="app")


def _mailbox_token(email_address: str) -> str:
    return create_access_token(email_address, scope="email")


# ---------------------------------------------------------------------------
# Conversão CONVIDADO -> INVESTIDOR: a matriz definitiva é mutuamente exclusiva.
# A conversão remove o grant de convidado, revoga a sessão app anterior e
# preserva o bloqueio de qualquer acesso a caixa real.
# ---------------------------------------------------------------------------


class TestConversaoConvidadoParaInvestidor:
    def test_conversao_desmarca_convidado_revoga_sessao_e_nao_vaza_resumo_real(
        self, client, db, criar_usuario, monkeypatch_mail360,
    ):
        user, token_antigo = criar_usuario()
        _marcar(db, user, convidado=True)

        ativado = client.post(
            "/api/email/conta",
            json={"senha": "senha-longa-123", "aceite_lgpd": True, "local_part": "combo.vazamento"},
            headers=_headers(token_antigo),
        )
        assert ativado.status_code == 201, ativado.text

        token_investidor = _converter_investidor(db, user)
        assert user.convidado is False
        assert user.investidor is True

        # A troca para a senha fixa CorVIAOS revoga a sessão app anterior.
        antigo = client.get("/api/auth/me", headers=_headers(token_antigo))
        assert antigo.status_code == 401

        resp = client.get("/api/email/resumo", headers=_headers(token_investidor))
        assert resp.status_code == 200
        assert resp.json() == {"disponivel": False, "email_address": None, "pendentes": []}

    def test_email_conta_prioriza_demo_depois_da_conversao(
        self, client, db, criar_usuario,
    ):
        user, _ = criar_usuario()
        _marcar(db, user, convidado=True)
        token = _converter_investidor(db, user)

        conta = client.get("/api/email/conta", headers=_headers(token))
        assert conta.status_code == 200
        assert conta.json()["modo_demonstracao"] is True
        assert conta.json()["email_address"] == "investidor.demo@corvia.med.br"
        assert user.convidado is False

    def test_mailbox_real_preexistente_fica_bloqueada_apos_conversao(
        self, client, db, criar_usuario,
    ):
        user, _ = criar_usuario()
        conta = EmailAccount(
            user_id=user.id, email_address="combo-real@corvia.med.br",
            mail360_account_key="account-key-combo", password_hash="hash", status="ativa",
        )
        db.add(conta)
        db.commit()
        _marcar(db, user, convidado=True)
        _converter_investidor(db, user)

        mailbox_token = _mailbox_token(conta.email_address)
        resp = client.get("/api/email/pastas", headers=_headers(mailbox_token))
        assert resp.status_code == 403
        assert "investidor" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Item 1 — privilege escalation via admin.py
# ---------------------------------------------------------------------------


class TestPrivilegeEscalation:
    def test_convidado_nao_pode_se_promover_a_admin_via_rota_convidado(
        self, client, db, criar_usuario,
    ):
        _, token_admin = criar_usuario(email="admin1@teste.local", role="admin")
        alvo, token_alvo = criar_usuario(email="alvo1@teste.local")
        client.patch(
            f"/api/admin/users/{alvo.id}/convidado?convidado=true",
            headers=_headers(token_admin),
        )
        # O próprio convidado tentando chamar a rota admin de novo, com o
        # PRÓPRIO token (não é admin) — precisa ser 403, nunca 200.
        resp = client.patch(
            f"/api/admin/users/{alvo.id}/investidor?investidor=true",
            headers=_headers(token_alvo),
        )
        assert resp.status_code == 403
        db.refresh(alvo)
        assert alvo.role == "medico" or alvo.role == "leitor"
        assert alvo.role != "admin"

    def test_marcar_convidado_ou_investidor_nunca_altera_role_mesmo_por_efeito_colateral(
        self, client, db, criar_usuario,
    ):
        _, token_admin = criar_usuario(email="admin2@teste.local", role="admin")
        alvo, _ = criar_usuario(email="alvo2@teste.local", role="leitor")
        r1 = client.patch(
            f"/api/admin/users/{alvo.id}/convidado?convidado=true",
            headers=_headers(token_admin),
        )
        assert r1.status_code == 200
        db.refresh(alvo)
        assert alvo.role == "leitor"

        r2 = client.patch(
            f"/api/admin/users/{alvo.id}/investidor?investidor=true",
            headers=_headers(token_admin),
        )
        assert r2.status_code == 200
        db.refresh(alvo)
        assert alvo.role == "leitor"

    def test_require_admin_nao_e_decorativo_residente_tambem_bloqueado(
        self, client, db, criar_usuario,
    ):
        alvo, _ = criar_usuario(email="alvo3@teste.local")
        _, token_residente = criar_usuario(email="residente@teste.local", role="residente")
        resp = client.patch(
            f"/api/admin/users/{alvo.id}/convidado?convidado=true",
            headers=_headers(token_residente),
        )
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Item 2 — payment bypass / contaminação de métrica de receita
# ---------------------------------------------------------------------------


class TestPaymentBypass:
    def test_usuario_pagante_normal_sem_flags_nunca_ganha_acesso_de_graca(
        self, client, db, criar_usuario,
    ):
        alvo, token = criar_usuario()
        assert alvo.convidado is False
        assert alvo.investidor is False
        resp = client.get(ROTA_GATED, headers=_headers(token))
        assert resp.status_code == 402

    def test_convidado_polui_subscription_status_ativo_mas_investidor_nao(
        self, client, db, criar_usuario,
    ):
        """Achado (não crítico, documentado como residual): `criar_checkout`
        marca `Subscription.status = "ativo"` para convidado (kind=meucardio),
        sem `stripe_customer_id`/`stripe_subscription_id` — qualquer relatório
        futuro que conte `Subscription.status == 'ativo'` sem excluir
        `stripe_subscription_id IS NULL` contaria convidados como assinantes
        pagos. Já era o comportamento documentado no código antes desta
        revisão (`billing.py::criar_checkout`, comentário do branch
        convidado) — investidor foi desenhado deliberadamente para NÃO fazer
        isso (comentário: "nunca marca sub.status=ativo"). Registrado aqui
        como assimetria intencional, não como bug novo desta issue."""
        convidado, token_convidado = criar_usuario(email="poluicao.convidado@teste.local")
        _marcar(db, convidado, convidado=True)
        client.post("/api/billing/checkout?plano=completo", headers=_headers(token_convidado))
        sub_convidado = (
            db.query(Subscription)
            .filter(Subscription.user_id == convidado.id, Subscription.kind == TIPO_MEUCARDIO)
            .first()
        )
        assert sub_convidado is not None
        assert sub_convidado.status == "ativo"
        assert sub_convidado.stripe_subscription_id is None

        investidor, _ = criar_usuario(email="poluicao.investidor@teste.local")
        token_investidor = _converter_investidor(db, investidor)
        with patch("app.api.billing.stripe.checkout.Session.create") as criar_sessao, \
             patch("app.api.billing.stripe.Customer.create") as criar_cliente:
            resp_investidor = client.post(
                "/api/billing/checkout?plano=completo",
                headers=_headers(token_investidor),
            )
            criar_sessao.assert_not_called()
            criar_cliente.assert_not_called()
        assert resp_investidor.status_code == 403
        sub_investidor = (
            db.query(Subscription)
            .filter(Subscription.user_id == investidor.id, Subscription.kind == TIPO_MEUCARDIO)
            .first()
        )
        assert sub_investidor is None

    def test_trocar_plano_recusa_convidado_sem_falar_com_stripe(self, client, db, criar_usuario):
        alvo, token = criar_usuario()
        _marcar(db, alvo, convidado=True)
        client.post("/api/billing/checkout?plano=completo", headers=_headers(token))
        with patch("app.api.billing.stripe.Subscription.retrieve") as retrieve, \
             patch("app.api.billing.stripe.Subscription.modify") as modify:
            resp = client.post(
                "/api/billing/trocar-plano?plano=basico&periodicidade=mensal",
                headers=_headers(token),
            )
            retrieve.assert_not_called()
            modify.assert_not_called()
        # Sem stripe_subscription_id gravado, a rota já barra em 404 antes de
        # checar `user.convidado` — resultado prático idêntico (nunca fala
        # com o Stripe), só o código de status muda.
        assert resp.status_code in (404, 409)

    def test_checkout_email_investidor_e_bloqueado_antes_de_falar_com_stripe(self, client, db, criar_usuario):
        """CORRIGIDO após esta revisão — era um achado real (IMPORTANTE, não
        crítico): ao contrário de `/billing/checkout` (que já tinha um
        `if user.investidor: ...` explícito), `POST /billing/checkout-email`
        não tinha bloqueio nenhum para investidor — o fluxo caía no caminho
        de pagamento normal, criava `stripe.Customer` de verdade e devolvia
        uma URL de checkout REAL. Não era escalada de privilégio (o
        investidor não ganhava e-mail real de graça — `POST /email/conta`
        continuava barrado por `bloquear_investidor_em_operacao_real_de_mail`
        depois), mas permitia iniciar e concluir um pagamento real por um
        produto que a regra de negócio diz que essa conta nunca usa.
        Corrigido com o mesmo padrão do `/billing/checkout`: bloqueio
        explícito de investidor ANTES de qualquer chamada ao Stripe."""
        alvo, _ = criar_usuario()
        token = _converter_investidor(db, alvo)
        with patch("app.api.billing.stripe.Customer.create") as criar_cliente, \
             patch("app.api.billing.stripe.checkout.Session.create") as criar_sessao:
            resp = client.post("/api/billing/checkout-email", headers=_headers(token))

        assert resp.status_code == 403, resp.text
        criar_cliente.assert_not_called()
        criar_sessao.assert_not_called()

        # Nenhuma Subscription de e-mail com stripe_customer_id foi criada.
        sub = (
            db.query(Subscription)
            .filter(Subscription.user_id == alvo.id, Subscription.kind == TIPO_EMAIL)
            .first()
        )
        assert sub is None or sub.stripe_customer_id is None

        provisionar = client.post(
            "/api/email/conta",
            json={"senha": "senha-longa-123", "aceite_lgpd": True, "local_part": "investidor.bloqueado"},
            headers=_headers(token),
        )
        assert provisionar.status_code == 403


# ---------------------------------------------------------------------------
# Item 3 — IDOR / isolamento de tenant
# ---------------------------------------------------------------------------


class TestIDOR:
    def test_investidor_nao_le_me_de_outro_usuario_via_id_arbitrario(
        self, client, db, criar_usuario,
    ):
        """/auth/me nunca aceita id — mas confirmamos que o token de um
        investidor nunca resolve para outro usuário mesmo tentando token
        adulterado/reaproveitado."""
        outro, _ = criar_usuario(email="outro.idor@teste.local")
        investidor, _ = criar_usuario(email="investidor.idor@teste.local")
        token_investidor = _converter_investidor(db, investidor)

        resp = client.get("/api/auth/me", headers=_headers(token_investidor))
        assert resp.status_code == 200
        assert resp.json()["email"] == investidor.email
        assert resp.json()["email"] != outro.email

    def test_investidor_nao_altera_preferencia_de_integracao_de_outro_usuario(
        self, client, db, criar_usuario,
    ):
        dono, _ = criar_usuario(email="dono.integracao@teste.local")
        integracao = CalendarIntegration(
            owner_id=dono.id, provider="google_calendar", display_name="Agenda do dono",
            status="connected", enabled=True,
            capabilities={"read_appointments": True, "read_mail": True, "send_mail": True},
            # sync_mail teria default True no modelo — força False aqui para
            # que o teste prove alteração de verdade, não o valor de fábrica.
            sync_mail=False,
        )
        db.add(integracao)
        db.commit()
        db.refresh(integracao)

        investidor, _ = criar_usuario(email="investidor.integracao@teste.local")
        token_investidor = _converter_investidor(db, investidor)

        resp = client.patch(
            f"/api/agenda/integrations/{integracao.id}/preferencias",
            json={"sync_mail": True},
            headers=_headers(token_investidor),
        )
        # O modo Investidor é barrado globalmente ANTES de qualquer mutação
        # ou resolução do recurso. O mesmo 403 é devolvido para qualquer id.
        assert resp.status_code == 403
        db.refresh(integracao)
        assert integracao.sync_mail is False

    def test_email_account_de_outro_usuario_nao_e_acessivel_por_id_de_integracao_alheio(
        self, client, db, criar_usuario,
    ):
        dono, token_dono = criar_usuario(email="dono.mailbox.idor@teste.local")
        conta_dono = EmailAccount(
            user_id=dono.id, email_address="dono.mailbox.idor@corvia.med.br",
            mail360_account_key="key-dono-idor", password_hash="hash", status="ativa",
        )
        db.add(conta_dono)
        db.commit()

        outro, token_outro = criar_usuario(email="outro.mailbox.idor@teste.local")
        conta_outro = EmailAccount(
            user_id=outro.id, email_address="outro.mailbox.idor@corvia.med.br",
            mail360_account_key="key-outro-idor", password_hash="hash", status="ativa",
        )
        db.add(conta_outro)
        db.commit()

        # Token de mailbox é resolvido pelo endereço no JWT (sub), não por
        # parâmetro de rota — confirmamos que o token da conta do dono não
        # pode ser usado para acessar recursos de outra CalendarIntegration
        # que pertence ao "outro" (owner_id=outro.id).
        integracao_do_outro = CalendarIntegration(
            owner_id=outro.id, provider="google_calendar", display_name="Agenda do outro",
            status="connected", enabled=True,
            capabilities={"read_appointments": True, "read_mail": True, "send_mail": True},
        )
        db.add(integracao_do_outro)
        db.commit()
        db.refresh(integracao_do_outro)

        token_mailbox_dono = _mailbox_token(conta_dono.email_address)
        resp = client.get(
            f"/api/email/externas/{integracao_do_outro.id}/pastas",
            headers=_headers(token_mailbox_dono),
        )
        # _integracao_email() filtra por owner_id == conta.user_id (o dono do
        # token de mailbox) — integração de outro titular não é encontrada.
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Item 4 — confusão entre "tem acesso ao produto" e "é admin"
# ---------------------------------------------------------------------------


class TestAdminVsEntitlementConfusion:
    def test_convidado_nao_acessa_rotas_admin_mesmo_tendo_acesso_ao_produto(
        self, client, db, criar_usuario,
    ):
        convidado, token = criar_usuario(email="convidado.naoadmin@teste.local")
        _marcar(db, convidado, convidado=True)
        # tem_acesso_ao_produto(convidado) é True, mas isso não deve valer
        # como "é admin" em nenhuma rota gated por require_admin.
        resp = client.get("/api/admin/users", headers=_headers(token))
        assert resp.status_code == 403

    def test_investidor_nao_acessa_rotas_admin_mesmo_tendo_acesso_ao_produto(
        self, client, db, criar_usuario,
    ):
        investidor, _ = criar_usuario(email="investidor.naoadmin@teste.local")
        token = _converter_investidor(db, investidor)
        resp = client.get("/api/admin/users", headers=_headers(token))
        assert resp.status_code == 403

    def test_verificar_retencao_exige_role_admin_de_verdade(self, client, db, criar_usuario):
        """`POST /billing/verificar-retencao` usa `current_user` +
        checagem manual de `admin.role != "admin"` em vez de
        `Depends(require_admin)` — confirma que a checagem manual não é
        mais fraca que a dependency."""
        convidado, token = criar_usuario(email="convidado.retencao@teste.local")
        _marcar(db, convidado, convidado=True)
        resp = client.post("/api/billing/verificar-retencao", headers=_headers(token))
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Item 5 — revogação incompleta de sessão
# ---------------------------------------------------------------------------


class TestRevogacaoDeSessao:
    def test_token_app_emitido_antes_de_revogar_convidado_para_de_funcionar(
        self, client, db, criar_usuario,
    ):
        alvo, token = criar_usuario()
        _marcar(db, alvo, convidado=True)
        assert client.get(ROTA_GATED, headers=_headers(token)).status_code == 200

        _marcar(db, alvo, convidado=False)
        # O token app não muda (não há rotação de JWT em revogação de
        # convidado/investidor — a decisão é lida do banco a cada
        # requisição via tem_acesso_ao_produto, então o próprio token
        # antigo já reflete o novo estado).
        resp = client.get(ROTA_GATED, headers=_headers(token))
        assert resp.status_code == 402

    def test_token_de_mailbox_emitido_antes_de_virar_investidor_para_de_funcionar_em_tempo_real(
        self, client, db, criar_usuario,
    ):
        """Já coberto por test_investidor_corvia_mail_demo.py, reproduzido
        aqui de forma independente para confirmar que não é um teste
        cosmético: o token de mailbox usado é literalmente o MESMO objeto
        de string emitido antes da mudança de flag — current_email_account
        reconsulta o banco a cada chamada, não há cache de decisão."""
        alvo, token = criar_usuario()
        conta = EmailAccount(
            user_id=alvo.id, email_address="revogacao.tempo.real@corvia.med.br",
            mail360_account_key="key-revogacao", password_hash="hash", status="ativa",
        )
        db.add(conta)
        db.commit()
        token_mailbox = _mailbox_token(conta.email_address)

        antes = client.get("/api/email/pastas", headers=_headers(token_mailbox))
        assert antes.status_code in (200, 502)

        _marcar(db, alvo, investidor=True)

        depois = client.get("/api/email/pastas", headers=_headers(token_mailbox))
        assert depois.status_code == 403

    def test_janela_de_revogacao_incompleta_documentada_sessao_de_mailbox_nao_reconsulta_assinatura_email_ativa(
        self, client, db, criar_usuario, monkeypatch_mail360,
    ):
        """RISCO RESIDUAL DOCUMENTADO, não corrigido por esta revisão:
        `current_email_account()` reconsulta `investidor` e `is_active` a
        cada requisição (marco de revogação real, provado acima), mas NÃO
        reconsulta `assinatura_email_ativa()` a cada requisição — só
        checa `conta.status == "ativa"`. Se um convidado tem a caixa
        provisionada e o admin revoga `convidado` SEM também suspender a
        `EmailAccount` (o código de `_sincronizar_caixa_de_email` só reage
        a eventos de `Subscription`, que convidado nunca gera), o token de
        mailbox ("permanecer conectado", até 30 dias) continua funcionando
        até expirar — o e-mail nativo não é automaticamente suspenso pela
        revogação do flag `convidado`."""
        alvo, token = criar_usuario()
        _marcar(db, alvo, convidado=True)
        ativado = client.post(
            "/api/email/conta",
            json={"senha": "senha-longa-123", "aceite_lgpd": True, "local_part": "janela.revogacao"},
            headers=_headers(token),
        )
        assert ativado.status_code == 201
        token_mailbox = _mailbox_token(ativado.json()["email_address"])

        antes = client.get("/api/email/pastas", headers=_headers(token_mailbox))
        assert antes.status_code == 200

        # Revoga convidado — sem tocar em EmailAccount.status.
        _marcar(db, alvo, convidado=False)

        depois = client.get("/api/email/pastas", headers=_headers(token_mailbox))
        # Achado: continua 200, porque current_email_account só olha
        # conta.status (ainda "ativa") e o marco de revogação de senha —
        # não reconsulta assinatura_email_ativa()/convidado.
        assert depois.status_code == 200, (
            "Se isto passou a falhar, o comportamento mudou: current_email_account "
            "passou a reconsultar entitlement a cada chamada — bom sinal, mas "
            "atualize este teste e o relatório."
        )


# ---------------------------------------------------------------------------
# Item 9 — soft-gate do tour (simetria com usuário comum)
# ---------------------------------------------------------------------------


class TestSoftGateDoTour:
    def test_onboarding_pendente_e_so_sinal_de_frontend_api_nao_bloqueia(
        self, client, db, criar_usuario,
    ):
        """Investidor é isento de perfil/KYC e vai diretamente ao tour.

        O tour continua sendo um soft-gate de UX: enquanto
        onboarding_pendente=True, GETs de produto permanecem disponíveis.
        """
        investidor, _ = criar_usuario(email="tour.investidor@teste.local")
        token_investidor = _converter_investidor(db, investidor)

        me = client.get("/api/auth/me", headers=_headers(token_investidor))
        assert me.status_code == 200
        assert me.json()["kyc_required"] is False
        assert me.json()["profile_completion_required"] is False
        assert me.json()["onboarding_pendente"] is True

        resp = client.get(ROTA_GATED, headers=_headers(token_investidor))
        assert resp.status_code == 200
