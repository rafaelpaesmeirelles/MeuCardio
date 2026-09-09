"""Money boundary: paid confirmation, replay, amount and reversal ordering."""
from datetime import datetime, timezone, timedelta
import hashlib
import hmac
import json
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.core.config import settings
from app.models.ai_credit_purchase import AICreditPurchase
from app.models.ai_wallet import AIWalletAccount, AIWalletCreditGrant
from app.models.subscription import Subscription
from app.services import ai_credit_payments as payments


def purchase_for(db, criar_usuario):
    user, token = criar_usuario()
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="ia", status="ativo",
                        commercial_version="2026-09-four-plans",
                        current_period_start=datetime.now(timezone.utc)-timedelta(days=1),
                        ai_access_started_at=datetime.now(timezone.utc)-timedelta(days=1),
                        current_period_end=datetime.now(timezone.utc)+timedelta(days=29)))
    purchase = AICreditPurchase(id=str(uuid4()), user_id=user.id, request_key=str(uuid4()),
                                amount_centavos=2990, currency="brl", status="pending")
    db.add(purchase)
    db.commit()
    return user, token, purchase


def paid_event(purchase, *, status="paid", kind="checkout.session.completed"):
    return {"object": "event", "id": "evt_" + uuid4().hex, "created": int(datetime.now(timezone.utc).timestamp()), "type": kind,
            "data": {"object": {"id": "cs_" + purchase.id, "mode": "payment", "currency": "brl",
                                  "amount_total": 2990, "payment_status": status,
                                  "payment_intent": "pi_" + purchase.id,
                                  "metadata": {"purpose": payments.PURPOSE, "purchase_id": purchase.id}}}}


def test_unpaid_redirect_cannot_credit_and_async_payment_is_idempotent(db, criar_usuario):
    user, _, purchase = purchase_for(db, criar_usuario)
    assert payments.handle_verified_event(db, paid_event(purchase, status="unpaid"))
    assert db.scalar(select(AIWalletCreditGrant)) is None
    event = paid_event(purchase, kind="checkout.session.async_payment_succeeded")
    assert payments.handle_verified_event(db, event)
    assert payments.handle_verified_event(db, event)
    assert payments.handle_verified_event(db, paid_event(purchase))
    grants = db.scalars(select(AIWalletCreditGrant)).all()
    assert len(grants) == 1
    account = db.scalar(select(AIWalletAccount).where(AIWalletAccount.user_id == user.id))
    assert account.paid_credit_micros == 29_900_000


def test_amount_mismatch_never_grants_credit(db, criar_usuario):
    _, _, purchase = purchase_for(db, criar_usuario)
    event = paid_event(purchase)
    event["data"]["object"]["amount_total"] = 1
    with pytest.raises(HTTPException) as exc:
        payments.handle_verified_event(db, event)
    assert exc.value.status_code == 400
    assert db.scalar(select(AIWalletCreditGrant)) is None


def test_out_of_order_partial_refunds_and_dispute_do_not_double_withdraw(db, criar_usuario):
    user, _, purchase = purchase_for(db, criar_usuario)
    obj = {"currency": "brl", "amount_refunded": 1000,
           "metadata": {"purpose": payments.PURPOSE, "purchase_id": purchase.id}}
    event = {"type": "charge.refunded", "data": {"object": obj}}
    payments.handle_verified_event(db, event)  # refund reaches us before checkout
    payments.handle_verified_event(db, paid_event(purchase))
    payments.handle_verified_event(db, event)  # duplicate cumulative refund
    account = db.scalar(select(AIWalletAccount).where(AIWalletAccount.user_id == user.id))
    assert account.paid_credit_micros == 19_900_000
    dispute = {"id": "dp_test", "payment_intent": "pi_" + purchase.id,
               "currency": "brl", "amount": 1990, "status": "needs_response"}
    payments.handle_verified_event(db, {"type": "charge.dispute.created", "data": {"object": dispute}})
    db.refresh(account)
    assert account.paid_credit_micros == 0
    dispute["status"] = "won"
    payments.handle_verified_event(db, {"type": "charge.dispute.closed", "data": {"object": dispute}})
    payments.handle_verified_event(db, {"type": "charge.dispute.created", "data": {"object": dispute}})
    db.refresh(account)
    assert account.paid_credit_micros == 19_900_000  # won dispute does not undo real refund
    obj["amount_refunded"] = 2990
    payments.handle_verified_event(db, event)
    db.refresh(account)
    assert account.paid_credit_micros == 0
    assert sum(g.credit_micros for g in db.scalars(select(AIWalletCreditGrant)).all()) == 0


def test_dispute_before_checkout_without_metadata_is_reconciled(db, criar_usuario, monkeypatch):
    user, _, purchase = purchase_for(db, criar_usuario)
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_not_real")
    def retrieve(intent):
        assert intent == "pi_" + purchase.id
        return {"id": intent, "amount": 2990, "currency": "brl",
                "metadata": {"purpose": payments.PURPOSE, "purchase_id": purchase.id}}
    monkeypatch.setattr(payments, "_client", lambda: SimpleNamespace(v1=SimpleNamespace(
        payment_intents=SimpleNamespace(retrieve=retrieve))))
    dispute = {"id": "dp_early", "payment_intent": "pi_" + purchase.id,
               "currency": "brl", "amount": 1000, "status": "needs_response"}
    assert payments.handle_verified_event(db, {"type": "charge.dispute.created", "data": {"object": dispute}})
    payments.handle_verified_event(db, paid_event(purchase))
    account = db.scalar(select(AIWalletAccount).where(AIWalletAccount.user_id == user.id))
    assert account.paid_credit_micros == 19_900_000


def test_checkout_retries_reuse_purchase_and_provider_session(db, criar_usuario, monkeypatch):
    user, _, _ = purchase_for(db, criar_usuario)
    monkeypatch.setattr(settings, "subscriptions_enabled", True)
    monkeypatch.setattr(settings, "ai_credit_topups_enabled", True)
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_not_real")
    calls = []

    def create(params, options):
        calls.append((params, options))
        assert "payment_method_types" not in params
        assert params["line_items"][0]["price_data"]["unit_amount"] == 2990
        return {"id": "cs_test_one", "url": "https://checkout.stripe.com/test-one"}

    monkeypatch.setattr(payments, "_client", lambda: SimpleNamespace(v1=SimpleNamespace(
        checkout=SimpleNamespace(sessions=SimpleNamespace(create=create)))))
    key = str(uuid4())
    first = payments.create_checkout(db, user, 2990, key)
    assert payments.create_checkout(db, user, 2990, key) == first
    assert len(calls) == 1
    with pytest.raises(HTTPException) as exc:
        payments.create_checkout(db, user, 5990, key)
    assert exc.value.status_code == 409


def test_prelaunch_blocks_purchase_without_contacting_provider(client, db, criar_usuario, monkeypatch):
    _, token, _ = purchase_for(db, criar_usuario)
    monkeypatch.setattr(settings, "subscriptions_enabled", False)
    monkeypatch.setattr(payments, "_client", lambda: pytest.fail("No payment before launch"))
    response = client.post("/api/ai-credits/checkout", json={"amount_centavos": 2990, "request_key": str(uuid4())},
                           headers={"Authorization": "Bearer " + token})
    assert response.status_code == 409


def test_real_signed_webhook_required_and_replay_safe(client, db, criar_usuario, monkeypatch):
    user, _, purchase = purchase_for(db, criar_usuario)
    secret = "whsec_only_for_this_unit_test"
    monkeypatch.setattr(settings, "stripe_webhook_secret", secret)
    event = paid_event(purchase)
    payload = json.dumps(event).encode()
    timestamp = str(event["created"])
    signature = hmac.new(secret.encode(), timestamp.encode() + b"." + payload, hashlib.sha256).hexdigest()
    bad = client.post("/api/billing/webhook", content=payload, headers={"stripe-signature": "t=" + timestamp + ",v1=invalid"})
    assert bad.status_code == 400
    assert db.scalar(select(AIWalletCreditGrant)) is None
    for _ in range(2):
        response = client.post("/api/billing/webhook", content=payload,
                               headers={"stripe-signature": "t=" + timestamp + ",v1=" + signature})
        assert response.status_code == 200, response.text
    db.expire_all()
    assert len(db.scalars(select(AIWalletCreditGrant)).all()) == 1
