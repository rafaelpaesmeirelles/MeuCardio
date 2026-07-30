"""Cobre o gap encontrado ao revisar as telas do CorvIA Mail para publicar:
`POST /api/billing/portal` e `GET /api/billing/faturas` só olhavam para a
assinatura da PLATAFORMA (`_assinatura_meucardio`). Um médico que assina só
o CorvIA Mail — o add-on foi desenhado de propósito para não depender da
assinatura principal (Tarefa 28, 30/07/2026) — nunca teria como abrir o
portal nem ver as próprias faturas: o botão "Gerenciar assinatura" da Minha
Conta devolvia 404 sempre, mesmo com uma assinatura de e-mail paga e ativa.
"""
from unittest.mock import patch

from app.models.subscription import TIPO_EMAIL, TIPO_MEUCARDIO, Subscription


class TestPortalEFaturasParaAssinanteSoDeEmail:
    def test_portal_404_sem_nenhuma_assinatura(self, client, criar_usuario):
        user, token = criar_usuario()
        resp = client.post("/api/billing/portal", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_portal_funciona_so_com_assinatura_de_email(self, client, db, criar_usuario):
        user, token = criar_usuario()
        sub = Subscription(
            user_id=user.id, kind=TIPO_EMAIL, status="ativo", stripe_customer_id="cus_email_only",
        )
        db.add(sub)
        db.commit()

        with patch("app.api.billing.stripe.billing_portal.Session.create") as criar_sessao:
            criar_sessao.return_value = {"url": "https://billing.stripe.com/session/fake"}
            resp = client.post("/api/billing/portal", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 200
        assert resp.json()["portal_url"] == "https://billing.stripe.com/session/fake"
        # o customer certo (o da assinatura de e-mail, única que existe) foi usado
        assert criar_sessao.call_args.kwargs["customer"] == "cus_email_only"

    def test_portal_prefere_customer_da_assinatura_principal_quando_ha_as_duas(self, client, db, criar_usuario):
        user, token = criar_usuario()
        db.add(Subscription(
            user_id=user.id, kind=TIPO_MEUCARDIO, status="ativo", stripe_customer_id="cus_principal",
        ))
        db.add(Subscription(
            user_id=user.id, kind=TIPO_EMAIL, status="ativo", stripe_customer_id="cus_principal",
        ))
        db.commit()

        with patch("app.api.billing.stripe.billing_portal.Session.create") as criar_sessao:
            criar_sessao.return_value = {"url": "https://billing.stripe.com/session/fake"}
            resp = client.post("/api/billing/portal", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 200
        assert criar_sessao.call_args.kwargs["customer"] == "cus_principal"

    def test_faturas_vazio_sem_nenhuma_assinatura(self, client, criar_usuario):
        user, token = criar_usuario()
        resp = client.get("/api/billing/faturas", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json() == {"faturas": []}

    def test_faturas_funciona_so_com_assinatura_de_email(self, client, db, criar_usuario):
        user, token = criar_usuario()
        db.add(Subscription(
            user_id=user.id, kind=TIPO_EMAIL, status="ativo", stripe_customer_id="cus_email_only_2",
        ))
        db.commit()

        with patch("app.api.billing.stripe.Invoice.list") as listar:
            # `stripe.Invoice.list` devolve um ListObject, que é subscrito
            # por ["data"] — não é uma lista pura (mesma pegadinha que o
            # `_campo()` do módulo existe para objeto de Subscription/Invoice).
            listar.return_value = {"data": []}
            resp = client.get("/api/billing/faturas", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 200
        assert listar.call_args.kwargs["customer"] == "cus_email_only_2"
