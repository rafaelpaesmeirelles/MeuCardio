"""Cobertura da issue #52 — entitlement de médico CONVIDADO e de INVESTIDOR.

Fonte central de decisão: `app/services/entitlement.py::tem_acesso_ao_produto`,
consultada por `assinante_ativo` (app/core/security.py) e por
`_kyc_required`/`_onboarding_pendente` (app/api/auth.py). Este arquivo prova,
pela rota HTTP real sempre que possível, que:

- convidado/investidor têm acesso imediato ao conceder, sem depender de
  nenhuma ação adicional (checkout, visita a /billing/status, criação manual
  de Subscription);
- investidor nunca aparece como assinante pago (`Subscription.status`) só por
  ter o flag concedido, nem em `POST /billing/checkout`, que responde sem
  falar com o Stripe;
- o tour guiado (onboarding) passa a considerar convidado/investidor;
- nada disso abre brecha de segurança nova (rota administrativa continua só
  para admin, header forjado não concede nada, um usuário não vê o `/auth/me`
  de outro nem dado clínico de outro tenant).

`GET /api/library/themes` é usado como "qualquer rota real gated por
`assinante_ativo`" (está em `ROUTERS_ASSINANTES`, `app/main.py`) — não exige
nenhuma outra fixture além do token, e devolve 200 com lista vazia quando não
há documento publicado, o que basta para provar o gate.
"""
from unittest.mock import patch

from app.core.security import create_access_token
from app.models.kyc import KycVerification
from app.models.round import Patient
from app.models.subscription import (
    PERIODICIDADE_MENSAL, PLANO_BASICO, PLANO_COMPLETO, TIPO_MEUCARDIO, Subscription,
)

ROTA_GATED = "/api/library/themes"


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _converter_investidor(db, user) -> str:
    user.investidor = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return create_access_token(user.email, scope="app")


def _subscription_do_usuario(db, user_id: int) -> Subscription | None:
    return (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id, Subscription.kind == TIPO_MEUCARDIO)
        .first()
    )


def _liberar_kyc(db, user_id: int) -> None:
    """Cria uma `KycVerification` já resolvida (`liberado_sem_checagem`) para
    o usuário — usado para isolar o teste de onboarding do fluxo completo de
    submissão de documento (`POST /kyc/submeter`, que exige arquivos JPEG
    reais). `_kyc_required` (app/api/auth.py) só considera KYC resolvido
    quando `liberado_para_uso()` é True para um destes três status:
    "liberado_conselho_ok", "liberado_sem_checagem" ou "aprovado"."""
    db.add(KycVerification(
        owner_id=user_id,
        doc_profissional_frente="dummy", doc_profissional_verso="dummy", selfie="dummy",
        status="liberado_sem_checagem",
    ))
    db.commit()


# --------------------------------------------------------------------- CONVIDADO --


class TestConvidado:
    def test_usuario_comum_sem_assinatura_recebe_402_em_rota_protegida(self, client, criar_usuario):
        _, token = criar_usuario()
        resp = client.get(ROTA_GATED, headers=_headers(token))
        assert resp.status_code == 402

    def test_admin_marca_convidado_libera_acesso_imediatamente_sem_nenhuma_outra_acao(
        self, client, db, criar_usuario
    ):
        _, token_admin = criar_usuario(email="admin@teste.local", role="admin")
        alvo, token_alvo = criar_usuario(email="convidado@teste.local")

        # Baseline: sem grant nenhum, bloqueado.
        antes = client.get(ROTA_GATED, headers=_headers(token_alvo))
        assert antes.status_code == 402

        resp_admin = client.patch(
            f"/api/admin/users/{alvo.id}/convidado?convidado=true",
            headers=_headers(token_admin),
        )
        assert resp_admin.status_code == 200

        # Nenhuma outra chamada entre o grant e o acesso — nem checkout, nem
        # /billing/status, nem recarregar o token.
        depois = client.get(ROTA_GATED, headers=_headers(token_alvo))
        assert depois.status_code == 200

    def test_convidado_com_acesso_permitido_sem_jamais_visitar_billing_status(
        self, client, db, criar_usuario
    ):
        """O acesso não pode depender de uma checagem/cache disparada por
        `/billing/status` (ou qualquer tela de "assinatura") — só o flag no
        banco, consultado a cada requisição por `tem_acesso_ao_produto`."""
        alvo, token = criar_usuario()
        alvo.convidado = True
        db.commit()

        resp = client.get(ROTA_GATED, headers=_headers(token))
        assert resp.status_code == 200

    def test_convidado_tem_acesso_sem_jamais_chamar_checkout_e_sem_subscription_criada(
        self, client, db, criar_usuario
    ):
        alvo, token = criar_usuario()
        alvo.convidado = True
        db.commit()

        # Nenhuma chamada a /billing/checkout nesta rodada, nenhuma
        # Subscription criada manualmente — prova que o acesso não depende
        # de nenhuma das duas coisas.
        assert _subscription_do_usuario(db, alvo.id) is None

        resp = client.get(ROTA_GATED, headers=_headers(token))
        assert resp.status_code == 200
        assert _subscription_do_usuario(db, alvo.id) is None

    def test_revogar_convidado_volta_a_bloquear_acesso(self, client, db, criar_usuario):
        _, token_admin = criar_usuario(email="admin@teste.local", role="admin")
        alvo, token_alvo = criar_usuario(email="convidado@teste.local")
        alvo.convidado = True
        db.commit()
        assert client.get(ROTA_GATED, headers=_headers(token_alvo)).status_code == 200

        resp = client.patch(
            f"/api/admin/users/{alvo.id}/convidado?convidado=false",
            headers=_headers(token_admin),
        )
        assert resp.status_code == 200
        assert resp.json()["convidado"] is False

        depois = client.get(ROTA_GATED, headers=_headers(token_alvo))
        assert depois.status_code == 402

    def test_convidado_com_assinatura_real_ativa_tem_acesso(self, client, db, criar_usuario):
        alvo, token = criar_usuario()
        alvo.convidado = True
        db.add(Subscription(user_id=alvo.id, kind=TIPO_MEUCARDIO, plano=PLANO_COMPLETO, status="ativo"))
        db.commit()

        resp = client.get(ROTA_GATED, headers=_headers(token))
        assert resp.status_code == 200

    def test_revogar_convidado_mas_manter_assinatura_ativa_continua_com_acesso(
        self, client, db, criar_usuario
    ):
        """O acesso passa a vir da assinatura, não mais do grant — provado
        revogando o flag e confirmando que o acesso sobrevive."""
        alvo, token = criar_usuario()
        alvo.convidado = True
        db.add(Subscription(user_id=alvo.id, kind=TIPO_MEUCARDIO, plano=PLANO_BASICO, status="ativo"))
        db.commit()
        assert client.get(ROTA_GATED, headers=_headers(token)).status_code == 200

        alvo.convidado = False
        db.commit()

        resp = client.get(ROTA_GATED, headers=_headers(token))
        assert resp.status_code == 200

    def test_convidado_com_conta_desativada_continua_bloqueado(self, client, db, criar_usuario):
        alvo, token = criar_usuario()
        alvo.convidado = True
        alvo.is_active = False
        db.commit()

        resp = client.get(ROTA_GATED, headers=_headers(token))
        # is_active=False derruba a resolução do token ANTES de chegar em
        # assinante_ativo (usuario_por_token_app filtra is_active=True) — o
        # bloqueio acontece em current_user, daí 401, não 402. De todo modo,
        # o efeito prático é o mesmo: acesso negado, sem exceção para convidado.
        assert resp.status_code == 401


# --------------------------------------------------------------------- INVESTIDOR --


class TestInvestidor:
    def test_investidor_ativo_tem_acesso(self, client, db, criar_usuario):
        alvo, _ = criar_usuario()
        token = _converter_investidor(db, alvo)

        resp = client.get(ROTA_GATED, headers=_headers(token))
        assert resp.status_code == 200

    def test_revogar_investidor_bloqueia_acesso(self, client, db, criar_usuario):
        alvo, _ = criar_usuario()
        token = _converter_investidor(db, alvo)
        assert client.get(ROTA_GATED, headers=_headers(token)).status_code == 200

        alvo.investidor = False
        db.commit()

        resp = client.get(ROTA_GATED, headers=_headers(token))
        assert resp.status_code == 402

    def test_checkout_investidor_e_bloqueado_sem_criar_subscription(
        self, client, db, criar_usuario
    ):
        alvo, _ = criar_usuario()
        token = _converter_investidor(db, alvo)

        with patch("app.api.billing.stripe.checkout.Session.create") as criar_sessao, \
             patch("app.api.billing.stripe.Customer.create") as criar_cliente:
            resp = client.post(
                "/api/billing/checkout?plano=completo", headers=_headers(token)
            )
            criar_sessao.assert_not_called()
            criar_cliente.assert_not_called()

        assert resp.status_code == 403
        assert _subscription_do_usuario(db, alvo.id) is None

    def test_marcar_investidor_nao_altera_role(self, client, db, criar_usuario):
        _, token_admin = criar_usuario(email="admin@teste.local", role="admin")
        alvo, _ = criar_usuario(email="investidor@teste.local", role="medico")
        assert alvo.role == "medico"

        resp = client.patch(
            f"/api/admin/users/{alvo.id}/investidor?investidor=true",
            headers=_headers(token_admin),
        )
        assert resp.status_code == 200
        db.refresh(alvo)
        assert alvo.role == "medico"
        assert alvo.investidor is True
        assert alvo.convidado is False
        assert alvo.profile_completion_required is False

    def test_investidor_nao_acessa_dado_de_outro_medico(self, client, db, criar_usuario):
        """Acesso ao produto não concede acesso a dados clínicos alheios."""
        dono, token_dono = criar_usuario(email="dono.paciente@teste.local")
        dono.convidado = True
        db.commit()

        criado = client.post(
            "/api/round/patients",
            headers=_headers(token_dono),
            json={
                "record_number": "INVESTIDOR-ISOLAMENTO-1",
                "initials": "II",
                "bed": "202",
                "unit": "Cardiologia",
            },
        )
        assert criado.status_code == 201, criado.text
        patient_id = criado.json()["id"]

        investidor, _ = criar_usuario(email="investidor.leitor@teste.local")
        token_investidor = _converter_investidor(db, investidor)

        listagem = client.get("/api/round/patients", headers=_headers(token_investidor))
        assert listagem.status_code == 200
        assert listagem.json() == []

        detalhe = client.get(
            f"/api/round/patients/{patient_id}", headers=_headers(token_investidor)
        )
        assert detalhe.status_code == 404
        assert "INVESTIDOR-ISOLAMENTO-1" not in detalhe.text
        assert db.query(Patient).filter(Patient.id == patient_id).count() == 1


# -------------------------------------------------------------------------- TOUR --


class TestOnboardingConvidadoInvestidor:
    def test_convidado_recem_marcado_sem_kyc_resolvido_ainda_nao_ve_onboarding(
        self, client, db, criar_usuario
    ):
        alvo, token = criar_usuario()
        alvo.convidado = True
        db.commit()
        assert alvo.onboarding_visto is False

        resp = client.get("/api/auth/me", headers=_headers(token))
        assert resp.status_code == 200
        corpo = resp.json()
        assert corpo["kyc_required"] is True
        assert corpo["onboarding_pendente"] is False

    def test_convidado_com_kyc_ja_resolvido_tem_onboarding_pendente(
        self, client, db, criar_usuario
    ):
        alvo, token = criar_usuario()
        alvo.convidado = True
        db.commit()
        _liberar_kyc(db, alvo.id)
        assert alvo.onboarding_visto is False

        resp = client.get("/api/auth/me", headers=_headers(token))
        assert resp.status_code == 200
        corpo = resp.json()
        assert corpo["kyc_required"] is False
        assert corpo["onboarding_pendente"] is True

    def test_investidor_novo_e_isento_de_kyc_e_vai_direto_ao_tour(
        self, client, db, criar_usuario
    ):
        alvo, _ = criar_usuario()
        token = _converter_investidor(db, alvo)

        resp = client.get("/api/auth/me", headers=_headers(token))
        assert resp.status_code == 200
        corpo = resp.json()
        assert corpo["profile_completion_required"] is False
        assert corpo["kyc_required"] is False
        assert corpo["onboarding_pendente"] is True

    def test_kyc_legado_nao_reabre_gate_do_investidor(
        self, client, db, criar_usuario
    ):
        alvo, _ = criar_usuario()
        token = _converter_investidor(db, alvo)
        _liberar_kyc(db, alvo.id)

        resp = client.get("/api/auth/me", headers=_headers(token))
        assert resp.status_code == 200
        assert resp.json()["kyc_required"] is False
        assert resp.json()["onboarding_pendente"] is True

    def test_concluir_onboarding_marca_visto_e_zera_pendente(self, client, db, criar_usuario):
        alvo, _ = criar_usuario()
        token = _converter_investidor(db, alvo)
        assert client.get("/api/auth/me", headers=_headers(token)).json()["onboarding_pendente"] is True

        resp = client.post("/api/auth/me/onboarding-concluido", headers=_headers(token))
        assert resp.status_code == 200
        assert resp.json() == {"onboarding_pendente": False}

        db.refresh(alvo)
        assert alvo.onboarding_visto is True

    def test_onboarding_pendente_continua_false_apos_nova_consulta_me(
        self, client, db, criar_usuario
    ):
        alvo, _ = criar_usuario()
        token = _converter_investidor(db, alvo)
        client.post("/api/auth/me/onboarding-concluido", headers=_headers(token))

        resp = client.get("/api/auth/me", headers=_headers(token))
        assert resp.status_code == 200
        assert resp.json()["onboarding_pendente"] is False

    def test_concluir_onboarding_exige_autenticacao_real(self, client):
        resp = client.post("/api/auth/me/onboarding-concluido")
        assert resp.status_code == 401


# ------------------------------------------------------------------------ BILLING --


class TestBillingRegressao:
    def test_assinante_pago_normal_continua_funcionando_como_antes(self, client, criar_usuario):
        _, token = criar_usuario()

        with patch("app.api.billing.stripe.Customer.create") as criar_cliente, \
             patch("app.api.billing.stripe.checkout.Session.create") as criar_sessao:
            criar_cliente.return_value = {"id": "cus_regressao"}
            criar_sessao.return_value = {"url": "https://checkout.stripe.com/session/regressao"}
            resp = client.post(
                f"/api/billing/checkout?plano={PLANO_BASICO}&periodicidade={PERIODICIDADE_MENSAL}",
                headers=_headers(token),
            )

        assert resp.status_code == 200
        assert resp.json()["checkout_url"] == "https://checkout.stripe.com/session/regressao"
        criar_sessao.assert_called_once()

    def test_assinatura_cancelada_sem_convidado_nem_investidor_e_402(
        self, client, db, criar_usuario
    ):
        alvo, token = criar_usuario()
        db.add(Subscription(user_id=alvo.id, kind=TIPO_MEUCARDIO, plano=PLANO_BASICO, status="cancelado"))
        db.commit()
        assert alvo.convidado is False
        assert alvo.investidor is False

        resp = client.get(ROTA_GATED, headers=_headers(token))
        assert resp.status_code == 402

    def test_conceder_convidado_e_investidor_nao_cria_subscription_ativa_automaticamente(
        self, client, db, criar_usuario
    ):
        _, token_admin = criar_usuario(email="admin@teste.local", role="admin")
        convidado, _ = criar_usuario(email="so.convidado@teste.local")
        investidor, _ = criar_usuario(email="so.investidor@teste.local")

        r1 = client.patch(
            f"/api/admin/users/{convidado.id}/convidado?convidado=true",
            headers=_headers(token_admin),
        )
        assert r1.status_code == 200
        r2 = client.patch(
            f"/api/admin/users/{investidor.id}/investidor?investidor=true",
            headers=_headers(token_admin),
        )
        assert r2.status_code == 200

        # O admin nunca chamou /billing/checkout por nenhum dos dois — o
        # simples grant não cria (e muito menos ativa) nenhuma Subscription.
        assert _subscription_do_usuario(db, convidado.id) is None
        assert _subscription_do_usuario(db, investidor.id) is None
        ativos = (
            db.query(Subscription)
            .filter(
                Subscription.user_id.in_([convidado.id, investidor.id]),
                Subscription.status == "ativo",
            )
            .count()
        )
        assert ativos == 0

    def test_checkout_normal_usuario_pagante_continua_chamando_stripe(self, client, criar_usuario):
        _, token = criar_usuario()

        with patch("app.api.billing.stripe.Customer.create") as criar_cliente, \
             patch("app.api.billing.stripe.checkout.Session.create") as criar_sessao:
            criar_cliente.return_value = {"id": "cus_normal_2"}
            criar_sessao.return_value = {"url": "https://checkout.stripe.com/session/normal"}
            resp = client.post(
                f"/api/billing/checkout?plano={PLANO_COMPLETO}", headers=_headers(token)
            )

        assert resp.status_code == 200
        criar_cliente.assert_called_once()
        criar_sessao.assert_called_once()


# ----------------------------------------------------------------------- SEGURANÇA --


class TestSeguranca:
    def test_nao_admin_nao_pode_marcar_convidado_nem_investidor(self, client, criar_usuario):
        alvo, _ = criar_usuario(email="alvo@teste.local")
        _, token_medico = criar_usuario(email="outro@teste.local")

        r1 = client.patch(
            f"/api/admin/users/{alvo.id}/convidado?convidado=true",
            headers=_headers(token_medico),
        )
        assert r1.status_code == 403

        r2 = client.patch(
            f"/api/admin/users/{alvo.id}/investidor?investidor=true",
            headers=_headers(token_medico),
        )
        assert r2.status_code == 403

    def test_header_inventado_nao_concede_acesso(self, client, criar_usuario):
        """`assinante_ativo` só consulta `tem_acesso_ao_produto(db, user)` —
        nenhum header do cliente é lido para decidir acesso."""
        _, token = criar_usuario()
        resp = client.get(
            ROTA_GATED,
            headers={**_headers(token), "X-Convidado": "true", "X-Investidor": "true"},
        )
        assert resp.status_code == 402

    def test_convidado_e_investidor_cada_um_so_ve_o_proprio_me(self, client, db, criar_usuario):
        convidado, token_convidado = criar_usuario(email="so.convidado.me@teste.local")
        convidado.convidado = True
        db.commit()
        investidor, _ = criar_usuario(email="so.investidor.me@teste.local")
        token_investidor = _converter_investidor(db, investidor)

        resp_convidado = client.get("/api/auth/me", headers=_headers(token_convidado))
        assert resp_convidado.status_code == 200
        corpo_convidado = resp_convidado.json()
        assert corpo_convidado["email"] == "so.convidado.me@teste.local"
        assert corpo_convidado["convidado"] is True
        assert corpo_convidado["investidor"] is False

        resp_investidor = client.get("/api/auth/me", headers=_headers(token_investidor))
        assert resp_investidor.status_code == 200
        corpo_investidor = resp_investidor.json()
        assert corpo_investidor["email"] == "so.investidor.me@teste.local"
        assert corpo_investidor["investidor"] is True
        assert corpo_investidor["convidado"] is False
