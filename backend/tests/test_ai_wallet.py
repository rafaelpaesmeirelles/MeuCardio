"""Financial invariants against an isolated Postgres database, no provider calls."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import delete, select, text

from app.models.ai_wallet import AIWalletAccount, AIWalletOperation, AIWalletPeriod
from app.models.rag import AIConversation
from app.models.user import User
from app.services import ai_wallet as wallet

_REAL_ENTITLEMENTS = wallet._entitlements
_REAL_ALLOWANCE_PERIOD = wallet._allowance_period
_REAL_ALLOWANCE_FRACTION = wallet._allowance_fraction


@pytest.fixture(autouse=True)
def _banco_limpo(db, monkeypatch):
    db.execute(text("TRUNCATE ai_wallet_credit_grants, ai_wallet_operations, ai_wallet_periods, ai_wallet_accounts RESTART IDENTITY CASCADE"))
    db.execute(text("TRUNCATE users RESTART IDENTITY CASCADE"))
    db.commit()
    monkeypatch.setattr(wallet, "_entitlements", lambda _db, _owner: {"ai": True, "plan": "ia"})
    monkeypatch.setattr(wallet, "_allowance_period", lambda _db, _account: wallet._month())
    monkeypatch.setattr(wallet, "_allowance_fraction", lambda _db, _account: (1, 1))
    monkeypatch.setattr(wallet, "_limits", lambda institutional=False:
                        (100_000_000, 100_000_000, 10_000) if institutional else (40_000_000, 10_000_000, 40_000))
    yield
    db.rollback()


@pytest.fixture
def owner(db):
    user = User(email="wallet-test@example.test", full_name="Wallet test", role="medico",
                password_hash="not-a-real-password", is_active=True)
    db.add(user); db.commit(); db.refresh(user)
    return user.id


def reserve(owner, key, cost, **extra):
    return wallet.reserve(owner_id=owner, operation_key=key, feature="clinical_chat",
                          model="test-model-v1", max_cost_micros=cost,
                          pricing_version="test-prices-v1", **extra)


def test_reservation_commits_before_call_idempotent_settlement_and_chat_delete_do_not_refund(db, owner):
    first = reserve(owner, "journey-1", 6_000_000)
    assert first["created"] and first["reserved_credit_micros"] == 24_000_000
    assert reserve(owner, "journey-1", 6_000_000)["created"] is False
    with pytest.raises(wallet.AIWalletConflict):
        reserve(owner, "journey-1", 5_000_000)
    with pytest.raises(wallet.AIWalletBudgetExceeded):
        reserve(owner, "journey-2", 5_000_000)
    # A separate DB session observes the persisted hold before provider I/O.
    persisted = db.execute(select(AIWalletOperation).where(AIWalletOperation.operation_key == "journey-1")).scalar_one()
    assert persisted.state == "reserved"
    wallet.settle(owner_id=owner, operation_key="journey-1", actual_cost_micros=2_000_000,
                  tokens_input=100, tokens_output=40, model="test-model-v1")
    wallet.settle(owner_id=owner, operation_key="journey-1", actual_cost_micros=2_000_000,
                  tokens_input=100, tokens_output=40, model="test-model-v1")
    before = wallet.wallet_summary(owner)
    assert before["spent_credit_centavos"] == 800
    assert before["available_credit_centavos"] == 3200
    db.add(AIConversation(user_id=owner, titulo="Disposable conversation")); db.commit()
    db.execute(delete(AIConversation).where(AIConversation.user_id == owner)); db.commit()
    assert wallet.wallet_summary(owner) == before


def test_concurrent_reservations_cannot_overspend_the_same_allowance(owner):
    def attempt(key):
        try:
            return reserve(owner, key, 6_000_000)["state"]
        except wallet.AIWalletBudgetExceeded:
            return "denied"
    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(attempt, ["parallel-1", "parallel-2"]))
    assert sorted(outcomes) == ["denied", "reserved"]
    assert wallet.wallet_summary(owner)["reserved_credit_centavos"] == 2400


def test_unknown_failure_keeps_hold_known_unbilled_failure_releases_and_budget_zero_blocks(owner):
    reserve(owner, "uncertain", 10_000_000)
    assert wallet.mark_unknown(owner_id=owner, operation_key="uncertain")["state"] == "unknown"
    with pytest.raises(wallet.AIWalletBudgetExceeded): reserve(owner, "more", 1)
    wallet.fail(owner_id=owner, operation_key="uncertain")
    wallet.fail(owner_id=owner, operation_key="uncertain")
    assert wallet.wallet_summary(owner)["available_credit_centavos"] == 4000
    reserve(owner, "already-approved", 1_000_000)
    wallet.set_monthly_budget(owner, 0)
    with pytest.raises(wallet.AIWalletBudgetExceeded): reserve(owner, "after-pause", 1)
    # User pause affects future calls, never erases an already incurred cost.
    wallet.settle(owner_id=owner, operation_key="already-approved", actual_cost_micros=500_000)
    assert wallet.wallet_summary(owner)["spent_credit_centavos"] == 200


def test_prepaid_credit_is_idempotent_non_expiring_and_chargeback_blocks_debt(db, owner, monkeypatch):
    reserve(owner, "consume-allowance", 10_000_000)
    wallet.settle(owner_id=owner, operation_key="consume-allowance", actual_cost_micros=10_000_000)
    assert wallet.grant_paid_credit(db, owner, 2000, "purchase:1")["created"]
    db.commit()
    assert wallet.grant_paid_credit(db, owner, 2000, "purchase:1")["created"] is False
    db.commit()
    reserve(owner, "prepaid", 5_000_000)
    wallet.settle(owner_id=owner, operation_key="prepaid", actual_cost_micros=4_000_000)
    assert wallet.wallet_summary(owner)["paid_available_credit_centavos"] == 400
    monkeypatch.setattr(wallet, "_month", lambda now=None: (date(2031, 2, 1), date(2031, 3, 1)))
    monkeypatch.setattr(wallet, "_today", lambda: date(2031, 2, 1))
    assert wallet.wallet_summary(owner)["paid_available_credit_centavos"] == 400
    assert wallet.reverse_paid_credit(db, owner, 2000, "refund:1", "purchase:1")["created"]
    db.commit()
    assert wallet.reverse_paid_credit(db, owner, 2000, "refund:1", "purchase:1")["created"] is False
    db.commit()
    assert wallet.wallet_summary(owner)["billing_blocked"] is True
    with pytest.raises(wallet.AIWalletBudgetExceeded): reserve(owner, "debt-block", 1)
    with pytest.raises(wallet.AIWalletConflict):
        wallet.reverse_paid_credit(db, owner, 1, "refund:excess", "purchase:1")
    db.rollback()
    assert wallet.restore_paid_credit(db, owner, 2000, "dispute-won:1", "purchase:1")["created"]
    db.commit()
    assert wallet.restore_paid_credit(db, owner, 2000, "dispute-won:1", "purchase:1")["created"] is False
    db.commit()
    assert wallet.wallet_summary(owner)["billing_blocked"] is False
    assert wallet.wallet_summary(owner)["paid_available_credit_centavos"] == 400
    with pytest.raises(wallet.AIWalletConflict):
        wallet.restore_paid_credit(db, owner, 1, "restore:excess", "purchase:1")
    db.rollback()


def test_overrun_records_full_provider_cost_caps_customer_charge_and_blocks_more(owner):
    reserve(owner, "overrun", 1_000_000)
    receipt = wallet.settle(owner_id=owner, operation_key="overrun", actual_cost_micros=2_000_000)
    assert receipt["state"] == "settled_overrun"
    assert receipt["actual_cost_micros"] == 2_000_000
    assert receipt["actual_credit_micros"] == receipt["reserved_credit_micros"] == 4_000_000
    with pytest.raises(wallet.AIWalletBudgetExceeded): reserve(owner, "blocked", 1)


def test_institutional_allowlist_has_separate_finite_budget_and_basic_plan_denies(owner, monkeypatch):
    receipt = reserve(None, "index-batch", 100_000_000, cost_center="catalog_index")
    assert receipt["reserved_credit_micros"] == 100_000_000
    with pytest.raises(wallet.AIWalletBudgetExceeded): reserve(None, "index-over", 1, cost_center="catalog_index")
    with pytest.raises(wallet.AIWalletAccessDenied): reserve(None, "bad-center", 1, cost_center="arbitrary")
    monkeypatch.setattr(wallet, "_entitlements", lambda _db, _owner: {"ai": False, "plan": "basico"})
    with pytest.raises(wallet.AIWalletAccessDenied): reserve(owner, "basic", 1)


def test_billing_allowance_survives_calendar_rollover_and_upgrade_without_double_grant(owner, monkeypatch):
    window = [date(2032, 1, 30), date(2032, 2, 29)]
    today = [date(2032, 1, 30)]
    monkeypatch.setattr(wallet, "_allowance_period", lambda _db, _account: tuple(window))
    monkeypatch.setattr(wallet, "_today", lambda: today[0])
    reserve(owner, "end-of-month", 10_000_000)
    wallet.settle(owner_id=owner, operation_key="end-of-month", actual_cost_micros=10_000_000)
    today[0] = date(2032, 2, 1)
    # Even a mid-cycle upgrade event cannot replace an already active grant.
    window[:] = [date(2032, 2, 1), date(2032, 3, 1)]
    monkeypatch.setattr(wallet, "_entitlements", lambda _db, _owner: {"ai": True, "plan": "completo"})
    with pytest.raises(wallet.AIWalletBudgetExceeded): reserve(owner, "calendar-reset-denied", 1)
    summary = wallet.wallet_summary(owner)
    assert summary["monthly_credit_centavos"] == 4000
    assert summary["available_credit_centavos"] == 0
    assert summary["period_start"] == "2032-01-30"
    assert summary["period_end"] == "2032-02-29"
    today[0] = date(2032, 2, 29)
    window[:] = [date(2032, 2, 29), date(2032, 3, 30)]
    assert reserve(owner, "confirmed-next-cycle", 10_000_000)["created"]


def test_unknown_persists_monotonic_partial_without_releasing_or_double_debiting(db, owner):
    reserve(owner, "partial", 5_000_000)
    receipt = wallet.mark_unknown(owner_id=owner, operation_key="partial", known_cost_micros=2_000_000,
                                 known_tokens_input=100, known_tokens_output=40, model="test-model-v1")
    assert receipt["state"] == "unknown" and receipt["actual_cost_micros"] == 2_000_000
    assert receipt["actual_credit_micros"] is None
    wallet.mark_unknown(owner_id=owner, operation_key="partial", known_cost_micros=1_000_000,
                        known_tokens_input=50, known_tokens_output=20)
    operation = db.execute(select(AIWalletOperation).where(AIWalletOperation.operation_key == "partial")).scalar_one()
    assert (operation.actual_cost_micros, operation.tokens_input, operation.tokens_output) == (2_000_000, 100, 40)
    summary = wallet.wallet_summary(owner)
    assert summary["reserved_credit_centavos"] == 2000 and summary["spent_credit_centavos"] == 0
    with pytest.raises(wallet.AIWalletConflict):
        wallet.settle(owner_id=owner, operation_key="partial", actual_cost_micros=1_000_000,
                      tokens_input=150, tokens_output=60)
    with pytest.raises(wallet.AIWalletConflict):
        wallet.settle(owner_id=owner, operation_key="partial", actual_cost_micros=3_000_000,
                      tokens_input=99, tokens_output=60)
    with pytest.raises(wallet.AIWalletConflict): wallet.fail(owner_id=owner, operation_key="partial")
    assert wallet.wallet_summary(owner)["reserved_credit_centavos"] == 2000
    for _ in range(2):
        wallet.settle(owner_id=owner, operation_key="partial", actual_cost_micros=3_000_000,
                      tokens_input=150, tokens_output=60)
    summary = wallet.wallet_summary(owner)
    assert summary["spent_credit_centavos"] == 1200 and summary["reserved_credit_centavos"] == 0
    assert summary["available_credit_centavos"] == 2800


def test_unknown_overrun_blocks_without_releasing_hold_and_grant_cannot_clear_it(db, owner):
    reserve(owner, "unknown-overrun", 1_000_000)
    receipt = wallet.mark_unknown(owner_id=owner, operation_key="unknown-overrun", known_cost_micros=2_000_000,
                                 known_tokens_input=100)
    assert receipt["state"] == "unknown" and receipt["actual_cost_micros"] == 2_000_000
    summary = wallet.wallet_summary(owner)
    assert summary["billing_blocked"] and summary["reserved_credit_centavos"] == 400
    assert summary["spent_credit_centavos"] == 0
    wallet.grant_paid_credit(db, owner, 2000, "purchase:overrun"); db.commit()
    assert wallet.wallet_summary(owner)["billing_blocked"]
    with pytest.raises(wallet.AIWalletBudgetExceeded): reserve(owner, "still-blocked", 1)
    receipt = wallet.settle(owner_id=owner, operation_key="unknown-overrun", actual_cost_micros=2_000_000,
                            tokens_input=100)
    assert receipt["state"] == "settled_overrun"
    assert receipt["actual_credit_micros"] == 4_000_000


def test_confirmed_subscription_cycle_integrates_with_real_wallet_helper(db, owner, monkeypatch):
    from app.models.subscription import Subscription, CURRENT_COMMERCIAL_VERSION
    monkeypatch.setattr(wallet, "_entitlements", _REAL_ENTITLEMENTS)
    monkeypatch.setattr(wallet, "_allowance_period", _REAL_ALLOWANCE_PERIOD)
    monkeypatch.setattr(wallet, "_allowance_fraction", _REAL_ALLOWANCE_FRACTION)
    now = datetime.now(timezone.utc)
    start, end = now - timedelta(days=2), now + timedelta(days=28)
    subscription = Subscription(user_id=owner, kind="meucardio", plano="ia", status="ativo",
        commercial_version=CURRENT_COMMERCIAL_VERSION, periodicidade="mensal",
        stripe_subscription_id="sub_wallet_confirmed_test", current_period_start=start, current_period_end=end,
        ai_access_started_at=start)
    db.add(subscription); db.commit()
    # Reads and estimates before the first operation must not create a grant.
    assert wallet.quote_cost(owner_id=owner, max_cost_micros=0)["maximum_credit_centavos"] == 0
    assert wallet.quote_cost(owner_id=owner, max_cost_micros=1_000_000)["maximum_credit_centavos"] == 400
    assert db.execute(select(AIWalletAccount.id)).first() is None
    reserve(owner, "confirmed-cycle", 1_000_000)
    summary = wallet.wallet_summary(owner)
    assert summary["period_start"] == start.date().isoformat()
    assert summary["period_end"] == end.date().isoformat()
    assert summary["monthly_credit_centavos"] == 4000
    periods = db.execute(select(AIWalletPeriod)).scalars().all()
    assert len(periods) == 1 and periods[0].grant_credit_micros == 40_000_000
    # Quote honors an existing period's tariff snapshot, not changed defaults.
    monkeypatch.setattr(wallet, "_limits", lambda institutional=False: (40_000_000, 10_000_000, 50_000))
    assert wallet.quote_cost(owner_id=owner, max_cost_micros=1_000_000)["maximum_credit_centavos"] == 400


def test_real_upgrade_one_day_allowance_is_prorated_and_confirmed_renewal_is_full(db, owner, monkeypatch):
    from app.models.subscription import Subscription, CURRENT_COMMERCIAL_VERSION
    from app.services import commercial_plans
    monkeypatch.setattr(wallet, "_entitlements", _REAL_ENTITLEMENTS)
    monkeypatch.setattr(wallet, "_allowance_period", _REAL_ALLOWANCE_PERIOD)
    monkeypatch.setattr(wallet, "_allowance_fraction", _REAL_ALLOWANCE_FRACTION)
    # Real persisted subscription + real allowance helpers; only the clock moves
    # for the confirmed renewal half of this test.
    access = datetime.now(timezone.utc) - timedelta(hours=1)
    start, end = access - timedelta(days=29), access + timedelta(days=1)
    subscription = Subscription(user_id=owner, kind="meucardio", plano="ia", status="ativo",
        commercial_version=CURRENT_COMMERCIAL_VERSION, periodicidade="mensal",
        stripe_subscription_id="sub_wallet_upgrade_test", current_period_start=start,
        current_period_end=end, ai_access_started_at=access)
    db.add(subscription); db.commit()
    prospective = wallet.wallet_summary(owner)
    assert prospective["monthly_credit_centavos"] <= 4000 // 30
    assert db.execute(select(AIWalletAccount.id)).first() is None
    reserve(owner, "prorated-upgrade", 10_000_000 // 30)
    period = db.execute(select(AIWalletPeriod)).scalar_one()
    assert 0 < period.grant_credit_micros <= 40_000_000 // 30
    assert 0 < period.cost_ceiling_micros <= 10_000_000 // 30
    with pytest.raises(wallet.AIWalletBudgetExceeded): reserve(owner, "no-whole-grant", 1)
    wallet.settle(owner_id=owner, operation_key="prorated-upgrade", actual_cost_micros=10_000_000 // 30)
    next_now = end + timedelta(hours=1)
    class NextCycleClock(datetime):
        @classmethod
        def now(cls, tz=None):
            return next_now if tz is not None else next_now.replace(tzinfo=None)
    monkeypatch.setattr(commercial_plans, "datetime", NextCycleClock)
    monkeypatch.setattr(wallet, "_today", lambda: next_now.date())
    subscription.current_period_start = end
    subscription.current_period_end = end + timedelta(days=30)
    db.commit()
    assert wallet.wallet_summary(owner)["monthly_credit_centavos"] == 4000
    reserve(owner, "confirmed-renewal-full", 10_000_000)
    db.expire_all()
    periods = db.execute(select(AIWalletPeriod).order_by(AIWalletPeriod.period_start)).scalars().all()
    assert len(periods) == 2 and periods[1].grant_credit_micros == 40_000_000
    assert periods[1].cost_ceiling_micros == 10_000_000
    assert periods[0].spent_cost_micros == 10_000_000 // 30
