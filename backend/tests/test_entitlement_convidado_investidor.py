"""Entitlement administrativo de Convidado e Investidor.

Convidado mantém acesso cortesia operacional. Investidor mantém entitlement
para navegar, porém todas as mutações reais são bloqueadas pela barreira global
de demonstração somente leitura.
"""
from unittest.mock import patch

from app.models.subscription import PLANO_BASICO, TIPO_MEUCARDIO, Subscription

ROTA_GATED = "/api/library/themes"


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscription(db, user_id: int):
    return db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.kind == TIPO_MEUCARDIO,
    ).first()


class TestConvidado:
    def test_usuario_comum_sem_assinatura_recebe_402(self, client, criar_usuario):
        _, token = criar_usuario()
        assert client.get(ROTA_GATED, headers=_headers(token)).status_code == 402

    def test_admin_marca_convidado_e_libera_sem_checkout(self, client, db, criar_usuario):
        _, token_admin = criar_usuario(email="admin@teste.local", role="admin")
        alvo, token = criar_usuario(email="convidado@teste.local")

        resp = client.patch(
            f"/api/admin/users/{alvo.id}/convidado?convidado=true",
            headers=_headers(token_admin),
        )
        assert resp.status_code == 200
        assert client.get(ROTA_GATED, headers=_headers(token)).status_code == 200
        assert _subscription(db, alvo.id) is None

    def test_revogar_convidado_sem_assinatura_volta_a_402(self, client, db, criar_usuario):
        _, token_admin = criar_usuario(email="admin@teste.local", role="admin")
        alvo, token = criar_usuario(email="convidado2@teste.local")
        alvo.convidado = True
        db.commit()
        assert client.get(ROTA_GATED, headers=_headers(token)).status_code == 200

        resp = client.patch(
            f"/api/admin/users/{alvo.id}/convidado?convidado=false",
            headers=_headers(token_admin),
        )
        assert resp.status_code == 200
        assert client.get(ROTA_GATED, headers=_headers(token)).status_code == 402

    def test_convidado_pode_executar_operacao_normal(self, client, db, criar_usuario):
        alvo, token = criar_usuario(email="convidado-write@teste.local")
        alvo.convidado = True
        db.commit()
        resp = client.put("/api/presence/me", json={"visible": True}, headers=_headers(token))
        assert resp.status_code == 200
        assert resp.json()["visible"] is True


class TestInvestidor:
    def test_investidor_tem_entitlement_para_gets(self, client, db, criar_usuario):
        alvo, token = criar_usuario(email="investidor@teste.local")
        alvo.investidor = True
        db.commit()
        assert client.get(ROTA_GATED, headers=_headers(token)).status_code == 200

    def test_investidor_nao_precisa_kYC_e_vai_direto_ao_tour(self, client, db, criar_usuario):
        alvo, token = criar_usuario(email="investidor-tour@teste.local")
        alvo.investidor = True
        db.commit()

        resp = client.get("/api/auth/me", headers=_headers(token))
        assert resp.status_code == 200
        corpo = resp.json()
        assert corpo["profile_completion_required"] is False
        assert corpo["kyc_required"] is False
        assert corpo["onboarding_pendente"] is True

    def test_investidor_conclui_tour_sem_kYC(self, client, db, criar_usuario):
        alvo, token = criar_usuario(email="investidor-fim-tour@teste.local")
        alvo.investidor = True
        db.commit()
        assert client.get("/api/auth/me", headers=_headers(token)).json()["onboarding_pendente"] is True

        fim = client.post("/api/auth/me/onboarding-concluido", headers=_headers(token))
        assert fim.status_code == 200
        assert client.get("/api/auth/me", headers=_headers(token)).json()["onboarding_pendente"] is False

    def test_investidor_write_e_403(self, client, db, criar_usuario):
        alvo, token = criar_usuario(email="investidor-readonly@teste.local")
        alvo.investidor = True
        db.commit()

        resp = client.put("/api/presence/me", json={"visible": True}, headers=_headers(token))
        assert resp.status_code == 403
        assert "somente para visualização" in resp.json()["detail"]

    def test_checkout_investidor_e_bloqueado_sem_chamar_stripe(self, client, db, criar_usuario):
        alvo, token = criar_usuario(email="investidor-billing@teste.local")
        alvo.investidor = True
        db.commit()

        with patch("app.api.billing.stripe.checkout.Session.create") as sessao, \
             patch("app.api.billing.stripe.Customer.create") as customer:
            resp = client.post("/api/billing/checkout?plano=basico", headers=_headers(token))
            sessao.assert_not_called()
            customer.assert_not_called()

        assert resp.status_code == 403
        assert _subscription(db, alvo.id) is None

    def test_revogar_investidor_remove_entitlement_se_nao_houver_assinatura(self, client, db, criar_usuario):
        alvo, token = criar_usuario(email="investidor-revogado@teste.local")
        alvo.investidor = True
        db.commit()
        assert client.get(ROTA_GATED, headers=_headers(token)).status_code == 200

        alvo.investidor = False
        db.commit()
        assert client.get(ROTA_GATED, headers=_headers(token)).status_code == 402


class TestRegressaoNormal:
    def test_checkout_normal_continua_chamando_stripe(self, client, criar_usuario):
        _, token = criar_usuario(email="normal-pago@teste.local")
        with patch("app.api.billing.stripe.Customer.create") as customer, \
             patch("app.api.billing.stripe.checkout.Session.create") as sessao:
            customer.return_value = {"id": "cus_normal"}
            sessao.return_value = {"url": "https://checkout.stripe.com/session/teste"}
            resp = client.post("/api/billing/checkout?plano=basico", headers=_headers(token))
        assert resp.status_code == 200
        assert resp.json()["checkout_url"] == "https://checkout.stripe.com/session/teste"
        sessao.assert_called_once()

    def test_assinatura_cancelada_sem_grant_continua_402(self, client, db, criar_usuario):
        alvo, token = criar_usuario(email="cancelado@teste.local")
        db.add(Subscription(user_id=alvo.id, kind=TIPO_MEUCARDIO, plano=PLANO_BASICO, status="cancelado"))
        db.commit()
        assert client.get(ROTA_GATED, headers=_headers(token)).status_code == 402


class TestSeguranca:
    def test_nao_admin_nao_pode_conceder_grants(self, client, criar_usuario):
        alvo, _ = criar_usuario(email="alvo@teste.local")
        _, token_medico = criar_usuario(email="outro@teste.local")
        assert client.patch(
            f"/api/admin/users/{alvo.id}/convidado?convidado=true",
            headers=_headers(token_medico),
        ).status_code == 403
        assert client.patch(
            f"/api/admin/users/{alvo.id}/investidor?investidor=true",
            headers=_headers(token_medico),
        ).status_code == 403

    def test_headers_forjados_nao_concedem_entitlement(self, client, criar_usuario):
        _, token = criar_usuario(email="header@teste.local")
        resp = client.get(
            ROTA_GATED,
            headers={**_headers(token), "X-Convidado": "true", "X-Investidor": "true"},
        )
        assert resp.status_code == 402
