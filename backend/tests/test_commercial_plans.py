from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import asyncio

import pytest
from fastapi import BackgroundTasks, HTTPException

from app.api import billing
from app.core.config import settings
from app.core.security import assinatura_email_ativa
from app.models.subscription import (
    Subscription, CURRENT_COMMERCIAL_VERSION, LEGACY_COMMERCIAL_VERSION,
)
from app.services.commercial_plans import (
    catalogue, plan_features, require_ai_entitlement, resolve_entitlements, ai_allowance_period, mail_addon_price,
)


@pytest.mark.parametrize("plan,price,ai,mail", [
    ("basico", 9990, False, False), ("basico_mail", 11990, False, True),
    ("ia", 14990, True, False), ("completo", 16990, True, True),
])
def test_new_catalogue_and_checkout_share_prices_and_features(plan, price, ai, mail):
    row = next(p for p in catalogue(subscriptions_enabled=False)["plans"] if p["id"] == plan)
    assert row["price_centavos"] == price
    assert row["features"] == {"tudo_com_tudo": True, "ai": ai, "mail": mail}
    assert row["ai_monthly_credit_centavos"] == (settings.ai_wallet_monthly_credit_centavos if ai else 0)
    assert row["checkout_available"] is False
    assert billing._item_de_preco(plan, "mensal")["price_data"]["unit_amount"] == price


def test_configured_price_changes_catalogue_and_server_checkout_together(monkeypatch):
    monkeypatch.setattr(settings, "commercial_price_ia_centavos", 15990)
    row = next(p for p in catalogue(subscriptions_enabled=False)["plans"] if p["id"] == "ia")
    assert row["price_centavos"] == billing._item_de_preco("ia", "mensal")["price_data"]["unit_amount"] == 15990


@pytest.mark.parametrize("period", ["semestral", "anual"])
def test_new_nonmonthly_offers_fail_before_provider_or_database(period, monkeypatch):
    monkeypatch.setattr(settings, "subscriptions_enabled", True)
    monkeypatch.setattr(billing, "_stripe_client", lambda: pytest.fail("No Stripe call expected"))
    with pytest.raises(HTTPException) as error:
        billing.criar_checkout(plano="ia", periodicidade=period, db=None, user=None)
    assert error.value.status_code == 409


def test_launch_disabled_before_any_payment_work(monkeypatch):
    monkeypatch.setattr(settings, "subscriptions_enabled", False)
    monkeypatch.setattr(billing, "_stripe_client", lambda: pytest.fail("No Stripe call expected"))
    with pytest.raises(HTTPException) as error:
        billing.criar_checkout(plano="ia", periodicidade="mensal", db=None, user=None)
    assert error.value.status_code == 503


def test_legacy_benefits_and_price_inference_are_preserved():
    assert plan_features("basico", LEGACY_COMMERCIAL_VERSION) == {
        "tudo_com_tudo": True, "ai": True, "mail": False,
    }
    assert plan_features("completo", LEGACY_COMMERCIAL_VERSION)["mail"]
    for amount, plan, interval, count, expected in [
        (4990, "basico", "month", 1, "mensal"),
        (5990, "completo", "month", 1, "mensal"),
        (26990, "basico", "month", 6, "semestral"),
        (57590, "completo", "year", 1, "anual"),
    ]:
        obj = {"items": {"data": [{"price": {"unit_amount": amount, "recurring": {
            "interval": interval, "interval_count": count,
        }}}]}}
        assert billing._inferir_plano_periodicidade_do_objeto(obj) == (plan, expected)
        assert billing._confirmed_commercial_version(obj) == LEGACY_COMMERCIAL_VERSION


def _new_price_event(plan="ia", amount=14990, currency="brl"):
    return {"metadata": {"commercial_version": CURRENT_COMMERCIAL_VERSION, "plano": plan},
            "items": {"data": [{"price": {"unit_amount": amount, "currency": currency,
                                          "recurring": {"interval": "month", "interval_count": 1}}}]}}


def test_new_contract_requires_confirmed_amount_currency_and_metadata():
    obj = _new_price_event()
    assert billing._inferir_plano_periodicidade_do_objeto(obj) == ("ia", "mensal")
    assert billing._confirmed_commercial_version(obj) == CURRENT_COMMERCIAL_VERSION
    assert billing._confirmed_commercial_version(_new_price_event(amount=1)) is None
    assert billing._confirmed_commercial_version(_new_price_event(currency="usd")) is None
    obj["metadata"] = {}
    assert billing._confirmed_commercial_version(obj) is None


def test_unknown_plan_or_version_never_grants_premium():
    assert not any(plan_features("ia", "unrecognized").values())
    assert not any(plan_features("unknown", CURRENT_COMMERCIAL_VERSION).values())


def test_entitlements_mail_gate_legacy_and_addon_on_real_subscriptions(db, criar_usuario):
    user, _ = criar_usuario()
    # Corpus access and paid AI generation have separate renewal rules.
    sub = Subscription(user_id=user.id, kind="meucardio", status="ativo", plano="basico",
                       commercial_version=CURRENT_COMMERCIAL_VERSION,
                       current_period_start=datetime.now(timezone.utc) - timedelta(days=1),
                       current_period_end=datetime.now(timezone.utc) + timedelta(days=29))
    db.add(sub); db.commit()
    assert resolve_entitlements(db, user)["tudo_com_tudo"]
    with pytest.raises(HTTPException) as error:
        require_ai_entitlement(db, user)
    assert error.value.status_code == 403
    assert not assinatura_email_ativa(db, user)
    sub.plano = "basico_mail"; db.commit()
    assert assinatura_email_ativa(db, user)
    assert not resolve_entitlements(db, user)["ai"]
    sub.plano = "ia"; db.commit()
    assert require_ai_entitlement(db, user)["ai"]
    assert not assinatura_email_ativa(db, user)
    sub.plano = "basico"; sub.commercial_version = LEGACY_COMMERCIAL_VERSION; db.commit()
    assert require_ai_entitlement(db, user)["ai"]
    sub.commercial_version = CURRENT_COMMERCIAL_VERSION
    db.add(Subscription(user_id=user.id, kind="email", status="ativo")); db.commit()
    assert assinatura_email_ativa(db, user)
    assert not resolve_entitlements(db, user)["ai"]
    sub.status = "cancelado"; db.commit()
    assert assinatura_email_ativa(db, user)  # separately purchased Mail survives
    assert not resolve_entitlements(db, user)["tudo_com_tudo"]


@pytest.mark.parametrize("role,guest,investor,mail", [
    ("admin", False, False, True), ("medico", True, False, True),
    ("medico", False, True, False),
])
def test_special_access_retains_existing_capabilities(role, guest, investor, mail, db, criar_usuario):
    # Legacy guests without a preferred plan consult consumed invitations;
    # a real database proves the direct administrative grant fallback.
    user, _ = criar_usuario(role=role)
    user.convidado, user.investidor = guest, investor
    db.commit()
    result = require_ai_entitlement(db, user)
    assert result["tudo_com_tudo"] and result["mail"] is mail
    user.is_active = False
    assert not resolve_entitlements(db, user)["ai"]


def test_checkout_requests_new_version_but_does_not_migrate_pending_contract(db, criar_usuario, monkeypatch):
    user, _ = criar_usuario()
    seen = {}
    calls = []
    def create_session(*, params, options):
        import stripe
        calls.append(params)
        seen.update(params)
        seen["idempotency_key"] = options["idempotency_key"]
        return stripe.StripeObject.construct_from({"id": "cs_test", "url": "https://checkout.stripe.com/test-only",
                "expires_at": int((datetime.now(timezone.utc) + timedelta(hours=23)).timestamp())}, "test")
    fake = SimpleNamespace(v1=SimpleNamespace(
        customers=SimpleNamespace(create=lambda **kwargs: {"id": "cus_test"}),
        checkout=SimpleNamespace(sessions=SimpleNamespace(create=create_session)),
    ))
    monkeypatch.setattr(settings, "subscriptions_enabled", True)
    monkeypatch.setattr(billing, "_stripe_client", lambda: fake)
    billing.criar_checkout(plano="ia", periodicidade="mensal", db=db, user=user)
    row = db.query(Subscription).filter_by(user_id=user.id, kind="meucardio").one()
    assert row.commercial_version == LEGACY_COMMERCIAL_VERSION
    assert row.status not in {"ativo", "teste", "inadimplente"}
    assert seen["subscription_data"]["metadata"]["commercial_version"] == CURRENT_COMMERCIAL_VERSION
    assert seen["line_items"][0]["price_data"]["unit_amount"] == 14990
    assert "payment_method_types" not in seen
    again = billing.criar_checkout(plano="ia", periodicidade="mensal", db=db, user=user)
    assert again["checkout_url"] == "https://checkout.stripe.com/test-only"
    assert len(calls) == 1
    assert billing._checkout_tracking(seen["idempotency_key"]) == seen["integration_identifier"]


def test_verified_subscription_event_applies_new_version_only_after_price_validation(db, criar_usuario, monkeypatch):
    user, _ = criar_usuario()
    sub = Subscription(user_id=user.id, kind="meucardio", status="pendente", plano="basico",
                       stripe_customer_id="cus_four_plans", commercial_version=LEGACY_COMMERCIAL_VERSION)
    db.add(sub); db.commit()
    obj = _new_price_event()
    obj.update(id="sub_four_plans", customer="cus_four_plans", status="active",
               current_period_start=int(datetime.now(timezone.utc).timestamp()),
               current_period_end=int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp()))
    event = {"object": "event", "id": "evt_four_plans", "type": "customer.subscription.created",
             "created": int(datetime.now(timezone.utc).timestamp()), "data": {"object": obj}}
    monkeypatch.setattr(settings, "stripe_webhook_secret", "unit-test-webhook-secret")
    monkeypatch.setattr(billing.stripe.Webhook, "construct_event", lambda *args: event)
    class Request:
        headers = {"stripe-signature": "unit-test-signature"}
        async def body(self):
            return b"{}"
    # A signed event with the wrong price cannot activate the requested plan.
    obj["items"]["data"][0]["price"]["unit_amount"] = 1
    with pytest.raises(HTTPException) as error:
        asyncio.run(billing.webhook(Request(), BackgroundTasks(), db))
    assert error.value.status_code == 400
    assert sub.commercial_version == LEGACY_COMMERCIAL_VERSION
    assert sub.status == "pendente"
    obj["items"]["data"][0]["price"]["unit_amount"] = 14990
    asyncio.run(billing.webhook(Request(), BackgroundTasks(), db))
    db.refresh(sub)
    assert (sub.plano, sub.commercial_version, sub.status) == ("ia", CURRENT_COMMERCIAL_VERSION, "ativo")
    assert sub.ai_access_started_at == sub.current_period_start


def test_paid_ai_requires_current_cycle_but_preserves_legacy_mail_grace(db, criar_usuario):
    user, _ = criar_usuario()
    now = datetime.now(timezone.utc)
    sub = Subscription(user_id=user.id, kind="meucardio", status="ativo", plano="completo",
        commercial_version=CURRENT_COMMERCIAL_VERSION, current_period_start=now-timedelta(days=3),
        current_period_end=now+timedelta(days=27))
    db.add(sub); db.commit()
    assert ai_allowance_period(db, user) == (sub.current_period_start.date(), sub.current_period_end.date())
    for status, start, end in [("inadimplente", now-timedelta(days=3), now+timedelta(days=27)),
                               ("ativo", None, now+timedelta(days=27)),
                               ("ativo", now-timedelta(days=33), now-timedelta(days=3))]:
        sub.status, sub.current_period_start, sub.current_period_end = status, start, end
        db.commit()
        rights = resolve_entitlements(db, user)
        assert rights["tudo_com_tudo"] and not rights["ai"] and not rights["mail"]
        with pytest.raises(ValueError):
            ai_allowance_period(db, user)
    sub.commercial_version = LEGACY_COMMERCIAL_VERSION
    sub.status = "inadimplente"; db.commit()
    assert resolve_entitlements(db, user)["mail"]
    assert not resolve_entitlements(db, user)["ai"]


def test_annual_legacy_ai_allowance_is_monthly_with_original_anniversary(db, criar_usuario):
    user, _ = criar_usuario()
    now = datetime.now(timezone.utc)
    sub = Subscription(user_id=user.id, kind="meucardio", status="ativo", plano="basico",
        periodicidade="anual", commercial_version=LEGACY_COMMERCIAL_VERSION,
        current_period_start=now-timedelta(days=100), current_period_end=now+timedelta(days=265))
    db.add(sub); db.commit()
    start, end = ai_allowance_period(db, user)
    assert start <= now.date() < end
    assert 28 <= (end-start).days <= 31
    assert start.day == sub.current_period_start.day


def test_mail_price_comes_from_catalogue_and_overlap_blocks_double_charge(db, criar_usuario, monkeypatch):
    monkeypatch.setattr(settings, "corvia_mail_preco_centavos", 0)
    assert mail_addon_price() == 2000
    user, _ = criar_usuario()
    db.add(Subscription(user_id=user.id, kind="email", status="ativo", stripe_subscription_id="sub_addon"))
    db.commit()
    with pytest.raises(HTTPException) as error:
        billing._ensure_no_mail_overlap(db, user, "completo")
    assert error.value.status_code == 409
    billing._ensure_no_mail_overlap(db, user, "ia")


def test_real_stripe_objects_confirm_attached_price_over_old_subscription_metadata():
    import stripe
    obj = _new_price_event(plan="basico", amount=14990)
    obj["items"]["data"][0]["price"]["metadata"] = {
        "commercial_version": CURRENT_COMMERCIAL_VERSION, "plano": "ia"}
    obj["items"]["data"][0]["current_period_start"] = 1788912000
    obj["items"]["data"][0]["current_period_end"] = 1791504000
    real = stripe.StripeObject.construct_from(obj, "test")
    assert billing._inferir_plano_periodicidade_do_objeto(real) == ("ia", "mensal")
    assert billing._confirmed_commercial_version(real) == CURRENT_COMMERCIAL_VERSION
    assert billing._fim_do_periodo(real).timestamp() == 1791504000


@pytest.mark.parametrize("old_plan,old_amount,target,behavior", [
    ("basico", 9990, "ia", "always_invoice"), ("ia", 14990, "basico", "none"),
])
def test_plan_change_requires_payment_and_never_optimistically_grants(db, criar_usuario, monkeypatch,
        old_plan, old_amount, target, behavior):
    import stripe
    user, _ = criar_usuario()
    sub = Subscription(user_id=user.id, kind="meucardio", status="ativo", plano=old_plan,
        periodicidade="mensal", commercial_version=CURRENT_COMMERCIAL_VERSION,
        stripe_subscription_id="sub_change")
    db.add(sub); db.commit()
    seen = {}
    def update(id, *, params):
        seen.update(params)
        return stripe.StripeObject.construct_from({"pending_update": {"expires_at": 1791504000}}, "test")
    fake = SimpleNamespace(v1=SimpleNamespace(subscriptions=SimpleNamespace(
        retrieve=lambda id: stripe.StripeObject.construct_from({"items": {"data": [{"id": "si_old",
            "price": {"unit_amount": old_amount}}]}}, "test"), update=update)))
    monkeypatch.setattr(settings, "subscriptions_enabled", True)
    monkeypatch.setattr(billing, "_stripe_client", lambda: fake)
    monkeypatch.setattr(billing, "_subscription_price_id", lambda plan: "price_new")
    billing.trocar_plano(plano=target, periodicidade="mensal", db=db, user=user)
    db.refresh(sub)
    assert sub.plano == old_plan
    assert seen["payment_behavior"] == "pending_if_incomplete"
    assert seen["proration_behavior"] == behavior
    assert "metadata" not in seen


def test_invoice_failure_targets_actual_addon_without_mutating_main(db, criar_usuario):
    user, _ = criar_usuario()
    main = Subscription(user_id=user.id, kind="meucardio", status="ativo", stripe_customer_id="cus_shared",
                        stripe_subscription_id="sub_main")
    addon = Subscription(user_id=user.id, kind="email", status="ativo", stripe_customer_id="cus_shared",
                         stripe_subscription_id="sub_mail")
    db.add_all([main, addon]); db.commit()
    when = datetime.now(timezone.utc)
    invoice = {"object": "invoice", "id": "in_mail_failed", "customer": "cus_shared",
               "parent": {"subscription_details": {"subscription": "sub_mail"}}}
    result = billing._aplicar_evento(db, invoice, when, lambda sub: setattr(sub, "status", "inadimplente"))
    assert result.id == addon.id and addon.status == "inadimplente"
    db.refresh(main)
    assert main.status == "ativo"
    unknown = {**invoice, "parent": {"subscription_details": {"subscription": "sub_unknown"}}}
    assert billing._aplicar_evento(db, unknown, when, lambda sub: setattr(sub, "status", "cancelado")) is None
    assert main.status == "ativo"
    older = when - timedelta(seconds=1)
    assert billing._aplicar_evento(db, invoice, older, lambda sub: setattr(sub, "status", "ativo")) is None
    assert addon.status == "inadimplente"


def test_cancelled_history_cannot_hide_active_subscription_and_create_duplicate(db, criar_usuario, monkeypatch):
    user, _ = criar_usuario()
    old = Subscription(user_id=user.id, kind="meucardio", status="cancelado", stripe_subscription_id="sub_old")
    current = Subscription(user_id=user.id, kind="meucardio", status="ativo", stripe_subscription_id="sub_current")
    db.add_all([old, current]); db.commit()
    monkeypatch.setattr(settings, "subscriptions_enabled", True)
    monkeypatch.setattr(billing, "_stripe_client", lambda: pytest.fail("Active contract must block another checkout"))
    with pytest.raises(HTTPException) as error:
        billing.criar_checkout(plano="ia", periodicidade="mensal", db=db, user=user)
    assert error.value.status_code == 409
    assert billing._assinatura_meucardio(db, user.id).id == current.id


def test_verified_upgrade_prorates_ai_start_and_preserves_it_for_ai_to_ai(db, criar_usuario, monkeypatch):
    user, _ = criar_usuario()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    start, end = now-timedelta(days=29), now+timedelta(days=1)
    sub = Subscription(user_id=user.id, kind="meucardio", status="ativo", plano="basico",
        commercial_version=CURRENT_COMMERCIAL_VERSION, stripe_customer_id="cus_prorated",
        stripe_subscription_id="sub_prorated", current_period_start=start, current_period_end=end)
    db.add(sub); db.commit()
    obj = _new_price_event()
    obj.update(id="sub_prorated", customer="cus_prorated", status="active",
               current_period_start=int(start.timestamp()), current_period_end=int(end.timestamp()))
    event = {"object": "event", "id": "evt_prorated", "type": "customer.subscription.updated",
             "created": int(now.timestamp()), "data": {"object": obj}}
    monkeypatch.setattr(settings, "stripe_webhook_secret", "unit-test-secret")
    monkeypatch.setattr(billing.stripe.Webhook, "construct_event", lambda *args: event)
    class Request:
        headers = {"stripe-signature": "test"}
        async def body(self): return b"{}"
    asyncio.run(billing.webhook(Request(), BackgroundTasks(), db))
    db.refresh(sub)
    assert sub.ai_access_started_at == now
    from app.services.commercial_plans import ai_allowance_fraction
    assert ai_allowance_fraction(db, user) == (86400, 30*86400)
    obj["metadata"]["plano"] = "completo"
    obj["items"]["data"][0]["price"]["unit_amount"] = 16990
    event["created"] += 1
    asyncio.run(billing.webhook(Request(), BackgroundTasks(), db))
    db.refresh(sub)
    assert sub.plano == "completo" and sub.ai_access_started_at == now
    # Same-second replay must never resurrect the canceled Stripe contract.
    billing._aplicar_evento(db, {**obj, "status": "canceled"}, now+timedelta(seconds=2),
                           lambda row: setattr(row, "status", "cancelado"))
    event["created"] += 1
    asyncio.run(billing.webhook(Request(), BackgroundTasks(), db))
    db.refresh(sub)
    assert sub.status == "cancelado"
