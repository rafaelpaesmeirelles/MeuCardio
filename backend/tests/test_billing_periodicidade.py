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
    CURRENT_COMMERCIAL_VERSION,
    PLANO_BASICO,
    PLANO_COMPLETO,
    TIPO_MEUCARDIO,
    Subscription,
)


@pytest.fixture(autouse=True)
def enabled_billing_for_contract_tests(monkeypatch):
    # Explicitly exercise the enabled flow; disabled launch has its own module.
    monkeypatch.setattr(settings, "subscriptions_enabled", True)


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
        with patch("app.api.billing._stripe_client") as factory:
            api = factory.return_value.v1
            api.customers.create.return_value = {"id": "cus_x"}
            api.checkout.sessions.create.return_value = {
                "id": "cs_monthly", "url": "https://checkout.stripe.com/fake", "expires_at": 9999999999,
            }
            resp = client.post(
                "/api/billing/checkout?plano=basico", headers={"Authorization": f"Bearer {token}"}
            )
            params = api.checkout.sessions.create.call_args.kwargs["params"]
            assert params["line_items"][0]["price_data"]["unit_amount"] == 9990
            assert params["subscription_data"]["metadata"]["periodicidade"] == "mensal"
            assert params["subscription_data"]["metadata"]["commercial_version"] == CURRENT_COMMERCIAL_VERSION
        assert resp.status_code == 200
        sub = (
            db.query(Subscription)
            .filter(Subscription.user_id == user.id, Subscription.kind == TIPO_MEUCARDIO)
            .first()
        )
        assert sub.periodicidade == "mensal"

    @pytest.mark.parametrize("period,configured", [
        ("semestral", ""), ("semestral", "price_legacy"), ("anual", "price_legacy"),
    ])
    def test_new_nonmonthly_checkout_is_not_offered_even_with_legacy_price(
        self, client, db, criar_usuario, monkeypatch, period, configured,
    ):
        user, token = criar_usuario()
        monkeypatch.setattr(settings, f"stripe_price_id_completo_{period}", configured)
        with patch("app.api.billing._stripe_client") as factory:
            resp = client.post(
                f"/api/billing/checkout?plano=completo&periodicidade={period}",
                headers={"Authorization": f"Bearer {token}"},
            )
            factory.assert_not_called()
        assert resp.status_code == 409
        assert "apenas na modalidade mensal" in resp.json()["detail"]
        assert db.query(Subscription).filter_by(user_id=user.id, kind=TIPO_MEUCARDIO).count() == 0

    def test_ja_assinante_ativo_recebe_409_orientando_trocar_plano(self, client, db, criar_usuario):
        user, token = criar_usuario()
        db.add(Subscription(user_id=user.id, kind=TIPO_MEUCARDIO, status="ativo", plano=PLANO_BASICO))
        db.commit()
        resp = client.post(
            "/api/billing/checkout?plano=completo&periodicidade=mensal",
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
            commercial_version=CURRENT_COMMERCIAL_VERSION,
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

    def test_valid_monthly_upgrade_requests_payment_and_never_applies_locally(
        self, client, db, criar_usuario,
    ):
        user, token = criar_usuario()
        sub = Subscription(
            user_id=user.id, kind=TIPO_MEUCARDIO, status="ativo", plano=PLANO_BASICO,
            periodicidade="mensal", stripe_subscription_id="sub_fake_2",
        )
        db.add(sub); db.commit()
        with patch("app.api.billing._stripe_client") as factory, \
             patch("app.api.billing._subscription_price_id", return_value="price_completo_monthly"):
            api = factory.return_value.v1
            api.subscriptions.retrieve.return_value = {"items": {"data": [
                {"id": "si_fake_item", "price": {"unit_amount": 4990}},
            ]}}
            resp = client.post(
                "/api/billing/trocar-plano?plano=completo&periodicidade=mensal",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200
            api.subscriptions.update.assert_called_once()
            args, kwargs = api.subscriptions.update.call_args
            assert args[0] == "sub_fake_2"
            assert kwargs["params"]["items"] == [{"id": "si_fake_item", "price": "price_completo_monthly"}]
            assert kwargs["params"]["proration_behavior"] == "always_invoice"
            assert kwargs["params"]["payment_behavior"] == "pending_if_incomplete"
        db.refresh(sub)
        assert sub.plano == PLANO_BASICO
        assert sub.periodicidade == "mensal"

    @pytest.mark.parametrize("period", ["semestral", "anual"])
    def test_existing_long_contract_is_preserved_until_its_end(self, client, db, criar_usuario, period):
        user, token = criar_usuario()
        sub = Subscription(user_id=user.id, kind=TIPO_MEUCARDIO, status="ativo", plano=PLANO_BASICO,
                           periodicidade=period, stripe_subscription_id="sub_existing_long")
        db.add(sub); db.commit()
        with patch("app.api.billing._stripe_client") as factory:
            resp = client.post("/api/billing/trocar-plano?plano=ia&periodicidade=mensal",
                               headers={"Authorization": f"Bearer {token}"})
            factory.assert_not_called()
        assert resp.status_code == 409
        assert "será preservado" in resp.json()["detail"]
        db.refresh(sub)
        assert sub.periodicidade == period and sub.plano == PLANO_BASICO


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
