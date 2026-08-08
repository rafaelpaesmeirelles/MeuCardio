"""Médico convidado (08/08/2026, pedido do Rafael) — `POST /billing/checkout`
libera a assinatura sem falar com o Stripe, sempre no plano Completo, e o
CorvIA Mail some junto (é incluído sem add-on separado quando o plano
principal é Completo — ver `status_email` em `app/api/billing.py`).
"""
from unittest.mock import patch

from app.models.subscription import PLANO_COMPLETO, TIPO_MEUCARDIO, Subscription


class TestCheckoutConvidado:
    def test_checkout_de_convidado_nao_chama_stripe_e_libera_plano_completo(self, client, db, criar_usuario):
        user, token = criar_usuario()
        user.convidado = True
        db.commit()

        with patch("app.api.billing.stripe.checkout.Session.create") as criar_sessao:
            resp = client.post(
                "/api/billing/checkout?plano=basico", headers={"Authorization": f"Bearer {token}"}
            )
            criar_sessao.assert_not_called()

        assert resp.status_code == 200
        corpo = resp.json()
        assert corpo["convidado"] is True
        assert corpo["checkout_url"] is None
        assert "Convidado" in corpo["mensagem"]

        sub = (
            db.query(Subscription)
            .filter(Subscription.user_id == user.id, Subscription.kind == TIPO_MEUCARDIO)
            .first()
        )
        assert sub.status == "ativo"
        # Sempre Completo, mesmo pedindo "basico" na query — "acesso completo"
        # é a promessa do convidado, não o plano que ele escolheu no clique.
        assert sub.plano == PLANO_COMPLETO
        assert sub.stripe_customer_id is None

    def test_checkout_de_convidado_nao_duplica_se_ja_ativo(self, client, db, criar_usuario):
        user, token = criar_usuario()
        user.convidado = True
        db.add(Subscription(user_id=user.id, kind=TIPO_MEUCARDIO, status="ativo", plano=PLANO_COMPLETO))
        db.commit()

        resp = client.post("/api/billing/checkout?plano=completo", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 409

    def test_checkout_normal_continua_indo_para_o_stripe_quando_nao_convidado(self, client, criar_usuario):
        user, token = criar_usuario()
        assert user.convidado is False

        with patch("app.api.billing.stripe.Customer.create") as criar_cliente, \
             patch("app.api.billing.stripe.checkout.Session.create") as criar_sessao:
            criar_cliente.return_value = {"id": "cus_normal"}
            criar_sessao.return_value = {"url": "https://checkout.stripe.com/session/fake"}
            resp = client.post("/api/billing/checkout?plano=basico", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 200
        assert resp.json()["checkout_url"] == "https://checkout.stripe.com/session/fake"
        criar_sessao.assert_called_once()


class TestToggleAdminDeConvidado:
    def test_admin_marca_e_desmarca_convidado(self, client, db, criar_usuario):
        _, token_admin = criar_usuario(email="admin@teste.local", role="admin")
        alvo, _ = criar_usuario(email="convidado@teste.local")
        assert alvo.convidado is False

        resp = client.patch(
            f"/api/admin/users/{alvo.id}/convidado?convidado=true",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert resp.status_code == 200
        assert resp.json()["convidado"] is True
        db.refresh(alvo)
        assert alvo.convidado is True

        resp = client.patch(
            f"/api/admin/users/{alvo.id}/convidado?convidado=false",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert resp.status_code == 200
        assert resp.json()["convidado"] is False

    def test_nao_admin_nao_pode_marcar_convidado(self, client, criar_usuario):
        alvo, _ = criar_usuario(email="alvo@teste.local")
        _, token_medico = criar_usuario(email="outro@teste.local")
        resp = client.patch(
            f"/api/admin/users/{alvo.id}/convidado?convidado=true",
            headers={"Authorization": f"Bearer {token_medico}"},
        )
        assert resp.status_code == 403


class TestStatusEmailParaConvidado:
    def test_status_email_ja_vem_incluido_apos_bypass(self, client, db, criar_usuario):
        """Sem precisar de nenhuma assinatura de e-mail avulsa: o plano
        Completo do convidado já basta para `status_email` responder
        'incluído no plano', liberando a tela de criar a caixa direto."""
        user, token = criar_usuario()
        user.convidado = True
        db.commit()
        client.post("/api/billing/checkout?plano=basico", headers={"Authorization": f"Bearer {token}"})

        resp = client.get("/api/billing/status-email", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        corpo = resp.json()
        assert corpo["incluido_no_plano"] is True
        assert corpo["status"] == "ativo"
