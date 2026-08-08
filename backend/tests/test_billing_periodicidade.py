"""Periodicidade de assinatura — mensal/semestral/anual (08/08/2026, pedido do
Rafael). Cobre `POST /billing/checkout?periodicidade=`,
`POST /billing/trocar-plano` e a reconciliação de periodicidade pelo webhook
a partir do `recurring` do Price confirmado pelo Stripe — nunca do que o
cliente pediu.
"""
from unittest.mock import patch

import pytest

from app.core.config import settings
from app.models.subscription import (
    PLANO_BASICO,
    PLANO_COMPLETO,
    TIPO_MEUCARDIO,
    Subscription,
)


class TestCheckoutComPeriodicidade:
    def test_periodicidade_invalida_devolve_400(self, client, criar_usuario):
        _, token = criar_usuario()
        resp = client.post(
            "/api/billing/checkout?plano=basico&periodicidade=trimestral",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400

    def test_checkout_mensal_sem_periodicidade_explicita_continua_default(
        self, client, db, criar_usuario
    ):
        """Sem `periodicidade` na query, o comportamento é o mesmo de antes
        desta funcionalidade: mensal, sem quebrar nenhum chamador antigo."""
        user, token = criar_usuario()
        with patch("app.api.billing.stripe.Customer.create") as criar_cliente, \
             patch("app.api.billing.stripe.checkout.Session.create") as criar_sessao:
            criar_cliente.return_value = {"id": "cus_x"}
            criar_sessao.return_value = {"url": "https://checkout.stripe.com/fake"}
            resp = client.post(
                "/api/billing/checkout?plano=basico", headers={"Authorization": f"Bearer {token}"}
            )
        assert resp.status_code == 200
        sub = (
            db.query(Subscription)
            .filter(Subscription.user_id == user.id, Subscription.kind == TIPO_MEUCARDIO)
            .first()
        )
        assert sub.periodicidade == "mensal"

    def test_checkout_semestral_sem_price_configurado_devolve_503(self, client, criar_usuario):
        """Nunca inventa um price_data com o valor de PRECO_CENTAVOS para
        semestral/anual — sem o Price real cadastrado no .env, a rota recusa
        em vez de cobrar um valor sem lastro no Stripe."""
        user, token = criar_usuario()
        antigo = settings.stripe_price_id_basico_semestral
        settings.stripe_price_id_basico_semestral = ""
        try:
            with patch("app.api.billing.stripe.Customer.create") as criar_cliente:
                criar_cliente.return_value = {"id": "cus_y"}
                resp = client.post(
                    "/api/billing/checkout?plano=basico&periodicidade=semestral",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 503
        finally:
            settings.stripe_price_id_basico_semestral = antigo

    def test_checkout_semestral_com_price_configurado_usa_o_price_id_do_env(
        self, client, db, criar_usuario
    ):
        user, token = criar_usuario()
        antigo = settings.stripe_price_id_completo_semestral
        settings.stripe_price_id_completo_semestral = "price_completo_semestral_fake"
        try:
            with patch("app.api.billing.stripe.Customer.create") as criar_cliente, \
                 patch("app.api.billing.stripe.checkout.Session.create") as criar_sessao:
                criar_cliente.return_value = {"id": "cus_z"}
                criar_sessao.return_value = {"url": "https://checkout.stripe.com/fake"}
                resp = client.post(
                    "/api/billing/checkout?plano=completo&periodicidade=semestral",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 200
            _, kwargs = criar_sessao.call_args
            assert kwargs["line_items"][0]["price"] == "price_completo_semestral_fake"
            assert kwargs["allow_promotion_codes"] is True
            assert kwargs["subscription_data"]["metadata"]["periodicidade"] == "semestral"
        finally:
            settings.stripe_price_id_completo_semestral = antigo

        sub = (
            db.query(Subscription)
            .filter(Subscription.user_id == user.id, Subscription.kind == TIPO_MEUCARDIO)
            .first()
        )
        assert sub.periodicidade == "semestral"
        assert sub.plano == PLANO_COMPLETO

    def test_ja_assinante_ativo_recebe_409_orientando_trocar_plano(self, client, db, criar_usuario):
        user, token = criar_usuario()
        db.add(Subscription(user_id=user.id, kind=TIPO_MEUCARDIO, status="ativo", plano=PLANO_BASICO))
        db.commit()
        resp = client.post(
            "/api/billing/checkout?plano=completo&periodicidade=anual",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 409
        assert "Trocar plano" in resp.json()["detail"]


class TestTrocarPlano:
    def test_sem_assinatura_ativa_devolve_404(self, client, criar_usuario):
        _, token = criar_usuario()
        resp = client.post(
            "/api/billing/trocar-plano?plano=completo&periodicidade=anual",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404

    def test_mesmo_plano_e_periodicidade_devolve_409(self, client, db, criar_usuario):
        user, token = criar_usuario()
        db.add(Subscription(
            user_id=user.id, kind=TIPO_MEUCARDIO, status="ativo", plano=PLANO_BASICO,
            periodicidade="mensal", stripe_subscription_id="sub_fake_1",
        ))
        db.commit()
        resp = client.post(
            "/api/billing/trocar-plano?plano=basico&periodicidade=mensal",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 409

    def test_convidado_nao_troca_plano_por_aqui(self, client, db, criar_usuario):
        user, token = criar_usuario()
        user.convidado = True
        db.add(Subscription(
            user_id=user.id, kind=TIPO_MEUCARDIO, status="ativo", plano=PLANO_COMPLETO,
            periodicidade="mensal", stripe_subscription_id="sub_fake_convidado",
        ))
        db.commit()
        resp = client.post(
            "/api/billing/trocar-plano?plano=basico&periodicidade=anual",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 409

    def test_troca_valida_chama_stripe_modify_e_nunca_aplica_localmente(
        self, client, db, criar_usuario
    ):
        """A rota só dispara a troca no Stripe — quem grava
        `sub.plano`/`sub.periodicidade` de verdade é sempre o webhook,
        nunca esta chamada otimista."""
        user, token = criar_usuario()
        antigo = settings.stripe_price_id_completo_anual
        settings.stripe_price_id_completo_anual = "price_completo_anual_fake"
        sub = Subscription(
            user_id=user.id, kind=TIPO_MEUCARDIO, status="ativo", plano=PLANO_BASICO,
            periodicidade="mensal", stripe_subscription_id="sub_fake_2",
        )
        db.add(sub)
        db.commit()
        try:
            with patch("app.api.billing.stripe.Subscription.retrieve") as retrieve, \
                 patch("app.api.billing.stripe.Subscription.modify") as modify:
                retrieve.return_value = {"items": {"data": [{"id": "si_fake_item"}]}}
                resp = client.post(
                    "/api/billing/trocar-plano?plano=completo&periodicidade=anual",
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert resp.status_code == 200
                modify.assert_called_once()
                args, kwargs = modify.call_args
                assert args[0] == "sub_fake_2"
                assert kwargs["items"][0]["id"] == "si_fake_item"
                assert kwargs["items"][0]["price"] == "price_completo_anual_fake"
                assert kwargs["proration_behavior"] == "create_prorations"
        finally:
            settings.stripe_price_id_completo_anual = antigo

        db.refresh(sub)
        # Nada aplicado localmente pela chamada otimista — só o webhook grava.
        assert sub.plano == PLANO_BASICO
        assert sub.periodicidade == "mensal"


class TestStatusExpoePeriodicidade:
    def test_status_sem_assinatura_devolve_periodicidade_none(self, client, criar_usuario):
        _, token = criar_usuario()
        resp = client.get("/api/billing/status", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["periodicidade"] is None

    def test_status_com_assinatura_expoe_periodicidade(self, client, db, criar_usuario):
        user, token = criar_usuario()
        db.add(Subscription(
            user_id=user.id, kind=TIPO_MEUCARDIO, status="ativo", plano=PLANO_COMPLETO,
            periodicidade="anual",
        ))
        db.commit()
        resp = client.get("/api/billing/status", headers={"Authorization": f"Bearer {token}"})
        assert resp.json()["periodicidade"] == "anual"


class TestPeriodicidadeDoPrice:
    """`_periodicidade_do_price`, usada pelo webhook para reconciliar sempre
    pelo que o Stripe confirma — nunca pelo que o cliente pediu."""

    @pytest.mark.parametrize(
        "recurring,esperado",
        [
            ({"interval": "month", "interval_count": 1}, "mensal"),
            ({"interval": "month"}, "mensal"),  # Price antigo, sem interval_count
            ({"interval": "month", "interval_count": 6}, "semestral"),
            ({"interval": "year", "interval_count": 1}, "anual"),
        ],
    )
    def test_mapeamento_de_recurring_para_periodicidade(self, recurring, esperado):
        from app.api.billing import _periodicidade_do_price

        assert _periodicidade_do_price({"recurring": recurring}) == esperado
