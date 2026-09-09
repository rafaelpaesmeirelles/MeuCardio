"""Atomic prepaid AI wallet, denominated exclusively in integer BRL micros.

One real = 1,000,000 micros. Reservations commit in their own transaction
before any paid request; deleting chats/cases cannot refund financial usage.
Unknown provider outcomes retain the hold until explicitly reconciled.
"""
from datetime import date, datetime, timezone
import hashlib
import json

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.ai_wallet import AIWalletAccount, AIWalletCreditGrant, AIWalletOperation, AIWalletPeriod
from app.models.user import User

MICROS_PER_CENT = 10_000
INSTITUTIONAL_COST_CENTERS = frozenset({"retrieval", "catalog_index", "editorial"})


class AIWalletError(RuntimeError): pass
class AIWalletAccessDenied(AIWalletError): pass
class AIWalletBudgetExceeded(AIWalletError): pass
class AIWalletConflict(AIWalletError): pass


def _integer(value, name, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, int) or value < (1 if positive else 0) or value > 10**14:
        raise AIWalletError(f"Invalid {name}")
    return value


def _label(value, name, maximum):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise AIWalletError(f"Invalid {name}")
    return value


def _principal(owner_id, cost_center):
    if owner_id is not None:
        _integer(owner_id, "owner_id", positive=True)
        return f"user:{owner_id}"
    if cost_center not in INSTITUTIONAL_COST_CENTERS:
        raise AIWalletAccessDenied("Centro de custo institucional não autorizado.")
    return f"institution:{cost_center}"


def _entitlements(db, owner_id):
    from app.services.commercial_plans import resolve_entitlements
    user = db.get(User, owner_id)
    if user is None or not user.is_active:
        raise AIWalletAccessDenied("Conta indisponível.")
    return resolve_entitlements(db, user)


def _month(now=None):
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    start = date(current.year, current.month, 1)
    end = date(current.year + (current.month == 12), current.month % 12 + 1, 1)
    return start, end


def _limits(institutional=False):
    if institutional:
        ceiling = int(getattr(settings, "ai_wallet_institutional_monthly_cost_ceiling_centavos", 10_000)) * MICROS_PER_CENT
        return ceiling, ceiling, 10_000
    credit = int(getattr(settings, "ai_wallet_monthly_credit_centavos", 4_000)) * MICROS_PER_CENT
    ceiling = int(getattr(settings, "ai_wallet_monthly_cost_ceiling_centavos", 1_000)) * MICROS_PER_CENT
    markup = int(getattr(settings, "ai_wallet_markup_bps", 40_000))
    if credit < 0 or ceiling < 0 or not 10_000 <= markup <= 1_000_000:
        raise AIWalletAccessDenied("Configuração financeira de IA inválida.")
    return credit, ceiling, markup


def _credit(cost, markup):
    return (cost * markup + 9_999) // 10_000


def _locked_account(db, principal, owner_id):
    db.execute(insert(AIWalletAccount).values(principal_key=principal, user_id=owner_id,
               paid_credit_micros=0, paid_spent_micros=0, paid_reserved_micros=0,
               billing_blocked=False).on_conflict_do_nothing(index_elements=["principal_key"]))
    return db.execute(select(AIWalletAccount).where(
        AIWalletAccount.principal_key == principal).with_for_update()).scalar_one()


def _today():
    return datetime.now(timezone.utc).date()


def _allowance_period(db, account):
    if account.principal_key.startswith("institution:"):
        return _month()
    from app.services.commercial_plans import ai_allowance_period
    user = db.get(User, account.user_id)
    if user is None:
        raise AIWalletAccessDenied("Conta indisponível.")
    try:
        start, end = ai_allowance_period(db, user)
    except ValueError as exc:
        raise AIWalletAccessDenied("Ciclo financeiro de IA ainda não confirmado.") from exc
    if not isinstance(start, date) or not isinstance(end, date) or end <= start:
        raise AIWalletAccessDenied("Ciclo financeiro de IA inválido.")
    return start, end


def _allowance_fraction(db, account):
    if account.principal_key.startswith("institution:"):
        return 1, 1
    from app.services.commercial_plans import ai_allowance_fraction
    user = db.get(User, account.user_id)
    if user is None:
        raise AIWalletAccessDenied("Conta indisponível.")
    try:
        numerator, denominator = ai_allowance_fraction(db, user)
    except ValueError as exc:
        raise AIWalletAccessDenied("Franquia financeira de IA ainda não confirmada.") from exc
    if (isinstance(numerator, bool) or isinstance(denominator, bool)
            or not isinstance(numerator, int) or not isinstance(denominator, int)
            or denominator <= 0 or not 0 <= numerator <= denominator):
        raise AIWalletAccessDenied("Fração da franquia de IA inválida.")
    return numerator, denominator


def _effective_limits(db, account):
    grant, ceiling, markup = _limits(account.principal_key.startswith("institution:"))
    numerator, denominator = _allowance_fraction(db, account)
    return grant * numerator // denominator, ceiling * numerator // denominator, markup


def _period(db, account, *, create):
    start, end = _allowance_period(db, account)
    # Upgrades cannot grant a second allowance while the previously financed
    # allowance is still active, even if a webhook changes billing dates.
    active = db.execute(select(AIWalletPeriod).where(
        AIWalletPeriod.account_id == account.id,
        AIWalletPeriod.period_start <= _today(),
        AIWalletPeriod.period_end > _today(),
    ).order_by(AIWalletPeriod.period_start.desc()).limit(1)).scalar_one_or_none()
    if active is not None:
        return active
    period = db.execute(select(AIWalletPeriod).where(
        AIWalletPeriod.account_id == account.id, AIWalletPeriod.period_start == start)).scalar_one_or_none()
    if period is None and create:
        grant, ceiling, markup = _effective_limits(db, account)
        period = AIWalletPeriod(account_id=account.id, period_start=start, period_end=end,
            currency="BRL", pricing_version=str(getattr(settings, "ai_wallet_pricing_version", "pilot-2026-09")),
            markup_bps=markup, grant_credit_micros=grant, cost_ceiling_micros=ceiling,
            spent_credit_micros=0, reserved_credit_micros=0, spent_cost_micros=0,
            reserved_cost_micros=0, paid_spent_credit_micros=0, paid_reserved_credit_micros=0)
        db.add(period)
        db.flush()
    return period


def _receipt(operation, *, created=False):
    return {"operation_id": operation.id, "operation_key": operation.operation_key,
            "state": operation.state, "created": created, "currency": "BRL",
            "reserved_cost_micros": operation.reserved_cost_micros,
            "reserved_credit_micros": operation.reserved_credit_micros,
            "actual_cost_micros": operation.actual_cost_micros,
            "actual_credit_micros": operation.actual_credit_micros,
            "pricing_version": operation.pricing_version}


def reserve(*, owner_id, operation_key, feature, model, max_cost_micros,
            pricing_version, cost_center=None):
    maximum = _integer(max_cost_micros, "max_cost_micros", positive=True)
    _label(operation_key, "operation_key", 180); _label(feature, "feature", 80)
    _label(model, "model", 160); _label(pricing_version, "pricing_version", 80)
    if cost_center is not None: _label(cost_center, "cost_center", 80)
    principal = _principal(owner_id, cost_center)
    fingerprint = hashlib.sha256(json.dumps([principal, feature, model, maximum, pricing_version, cost_center],
                                          ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    with SessionLocal.begin() as db:
        account = _locked_account(db, principal, owner_id)
        if owner_id is not None and not _entitlements(db, owner_id).get("ai"):
            raise AIWalletAccessDenied("Seu plano não inclui as funções de IA.")
        existing = db.execute(select(AIWalletOperation).where(
            AIWalletOperation.account_id == account.id,
            AIWalletOperation.operation_key == operation_key)).scalar_one_or_none()
        if existing:
            if existing.fingerprint != fingerprint:
                raise AIWalletConflict("Chave de operação reutilizada com parâmetros diferentes.")
            return _receipt(existing)
        if account.billing_blocked:
            raise AIWalletBudgetExceeded("Saldo de IA pendente de regularização.")
        period = _period(db, account, create=True)
        available_credit = max(0, period.grant_credit_micros - period.spent_credit_micros - period.reserved_credit_micros)
        available_cost = max(0, period.cost_ceiling_micros - period.spent_cost_micros - period.reserved_cost_micros)
        included_cost = min(maximum, available_cost, available_credit * 10_000 // period.markup_bps)
        included_credit = _credit(included_cost, period.markup_bps)
        paid_credit = _credit(maximum - included_cost, period.markup_bps)
        if paid_credit > max(0, account.paid_credit_micros - account.paid_spent_micros - account.paid_reserved_micros):
            raise AIWalletBudgetExceeded("Crédito de IA insuficiente para concluir esta operação.")
        reserved_credit = included_credit + paid_credit
        spent_and_reserved = (period.spent_credit_micros + period.reserved_credit_micros
                              + period.paid_spent_credit_micros + period.paid_reserved_credit_micros)
        if account.budget_credit_micros is not None and spent_and_reserved + reserved_credit > account.budget_credit_micros:
            raise AIWalletBudgetExceeded("Seu limite mensal de uso de IA foi atingido.")
        period.reserved_cost_micros += included_cost
        period.reserved_credit_micros += included_credit
        period.paid_reserved_credit_micros += paid_credit
        account.paid_reserved_micros += paid_credit
        operation = AIWalletOperation(account_id=account.id, period_id=period.id,
            operation_key=operation_key, feature=feature, cost_center=cost_center,
            model_name=model, pricing_version=pricing_version, fingerprint=fingerprint,
            state="reserved", reserved_cost_micros=maximum, reserved_credit_micros=reserved_credit,
            included_reserved_cost_micros=included_cost, included_reserved_credit_micros=included_credit,
            paid_reserved_credit_micros=paid_credit, tokens_input=0, tokens_output=0)
        db.add(operation); db.flush()
        return _receipt(operation, created=True)


def _find_operation(db, owner_id, cost_center, operation_key):
    principal = _principal(owner_id, cost_center)
    account = db.execute(select(AIWalletAccount).where(
        AIWalletAccount.principal_key == principal).with_for_update()).scalar_one_or_none()
    if account is None:
        raise AIWalletConflict("Reserva de IA não encontrada.")
    operation = db.execute(select(AIWalletOperation).where(
        AIWalletOperation.account_id == account.id,
        AIWalletOperation.operation_key == operation_key)).scalar_one_or_none()
    if operation is None:
        raise AIWalletConflict("Reserva de IA não encontrada.")
    return account, db.get(AIWalletPeriod, operation.period_id), operation


def _settle(*, owner_id, operation_key, actual_cost_micros, tokens_input=0,
            tokens_output=0, model=None, cost_center=None, released=False):
    actual = _integer(actual_cost_micros, "actual_cost_micros")
    _integer(tokens_input, "tokens_input"); _integer(tokens_output, "tokens_output")
    if model is not None: _label(model, "model", 160)
    with SessionLocal.begin() as db:
        account, period, operation = _find_operation(db, owner_id, cost_center, operation_key)
        if operation.state not in {"reserved", "unknown"}:
            if (operation.actual_cost_micros, operation.tokens_input, operation.tokens_output) != (actual, tokens_input, tokens_output):
                raise AIWalletConflict("A operação já foi liquidada com valores diferentes.")
            if model is not None and model != operation.model_name:
                raise AIWalletConflict("A operação já foi liquidada com outro modelo.")
            return _receipt(operation)
        if (actual < (operation.actual_cost_micros or 0)
                or tokens_input < operation.tokens_input or tokens_output < operation.tokens_output):
            raise AIWalletConflict("Liquidação não pode reduzir o consumo parcial já confirmado.")
        overrun = actual > operation.reserved_cost_micros
        # Record the full incurred provider cost, but never charge the customer
        # more than the confirmed reservation. An overrun blocks future calls.
        billable = min(actual, operation.reserved_cost_micros)
        included_cost = min(billable, operation.included_reserved_cost_micros)
        included_credit = _credit(included_cost, period.markup_bps)
        paid_credit = _credit(billable - included_cost, period.markup_bps)
        period.reserved_cost_micros -= operation.included_reserved_cost_micros
        period.reserved_credit_micros -= operation.included_reserved_credit_micros
        period.paid_reserved_credit_micros -= operation.paid_reserved_credit_micros
        account.paid_reserved_micros -= operation.paid_reserved_credit_micros
        period.spent_cost_micros += included_cost
        period.spent_credit_micros += included_credit
        period.paid_spent_credit_micros += paid_credit
        account.paid_spent_micros += paid_credit
        operation.actual_cost_micros = actual
        operation.actual_credit_micros = included_credit + paid_credit
        operation.tokens_input = tokens_input; operation.tokens_output = tokens_output
        operation.model_name = model or operation.model_name
        operation.state = "settled_overrun" if overrun else ("released" if released else "settled")
        operation.settled_at = datetime.now(timezone.utc)
        if overrun or account.paid_credit_micros < account.paid_spent_micros + account.paid_reserved_micros:
            account.billing_blocked = True
        db.flush()
        return _receipt(operation)


def settle(*, owner_id, operation_key, actual_cost_micros, tokens_input=0,
           tokens_output=0, model=None, cost_center=None):
    return _settle(owner_id=owner_id, operation_key=operation_key, actual_cost_micros=actual_cost_micros,
                   tokens_input=tokens_input, tokens_output=tokens_output, model=model, cost_center=cost_center)


def fail(*, owner_id, operation_key, billable_cost_micros=0, cost_center=None):
    """Release only a known unbilled failure; charge known incurred cost if any."""
    return _settle(owner_id=owner_id, operation_key=operation_key,
                   actual_cost_micros=billable_cost_micros, cost_center=cost_center,
                   released=billable_cost_micros == 0)


def mark_unknown(*, owner_id, operation_key, cost_center=None, known_cost_micros=0,
                 known_tokens_input=0, known_tokens_output=0, model=None):
    """Persist cumulative confirmed progress while retaining the entire hold.

    Unknown outcomes are not settled: confirmed partial cost is evidence for
    reconciliation, never an additional debit beside the reservation.
    """
    known = _integer(known_cost_micros, "known_cost_micros")
    _integer(known_tokens_input, "known_tokens_input")
    _integer(known_tokens_output, "known_tokens_output")
    if model is not None: _label(model, "model", 160)
    with SessionLocal.begin() as db:
        account, _period_row, operation = _find_operation(db, owner_id, cost_center, operation_key)
        if operation.state not in {"reserved", "unknown"}:
            if (known > (operation.actual_cost_micros or 0)
                    or known_tokens_input > operation.tokens_input
                    or known_tokens_output > operation.tokens_output):
                raise AIWalletConflict("Consumo parcial excede a liquidação já registrada.")
            return _receipt(operation)
        operation.state = "unknown"
        operation.actual_cost_micros = max(operation.actual_cost_micros or 0, known)
        operation.tokens_input = max(operation.tokens_input, known_tokens_input)
        operation.tokens_output = max(operation.tokens_output, known_tokens_output)
        if model is not None: operation.model_name = model
        if operation.actual_cost_micros > operation.reserved_cost_micros:
            account.billing_blocked = True
        db.flush()
        return _receipt(operation)


def _grant(db, user_id, credit_centavos, reference, original_reference=None, *, restore=False):
    amount = _integer(credit_centavos, "credit_centavos", positive=True) * MICROS_PER_CENT
    _label(reference, "reference", 180)
    account = _locked_account(db, _principal(user_id, None), user_id)
    if restore and not original_reference:
        raise AIWalletConflict("Restauração exige uma referência original.")
    signed = amount if restore or not original_reference else -amount
    existing = db.execute(select(AIWalletCreditGrant).where(AIWalletCreditGrant.reference == reference)).scalar_one_or_none()
    if existing:
        if (existing.account_id, existing.credit_micros, existing.original_reference) != (account.id, signed, original_reference):
            raise AIWalletConflict("Referência financeira reutilizada com valores diferentes.")
        return {"created": False, "reference": reference, "credit_centavos": signed // MICROS_PER_CENT}
    if original_reference:
        _label(original_reference, "original_reference", 180)
        original = db.execute(select(AIWalletCreditGrant).where(
            AIWalletCreditGrant.reference == original_reference,
            AIWalletCreditGrant.account_id == account.id)).scalar_one_or_none()
        if original is None or original.credit_micros <= 0:
            raise AIWalletConflict("Crédito original não encontrado.")
        reversed_amount = int(db.execute(select(func.coalesce(func.sum(AIWalletCreditGrant.credit_micros), 0)).where(
            AIWalletCreditGrant.original_reference == original_reference)).scalar_one())
        if restore and amount > -reversed_amount:
            raise AIWalletConflict("Restauração excede os estornos líquidos do crédito original.")
        if not restore and amount > original.credit_micros + reversed_amount:
            raise AIWalletConflict("Estorno excede o crédito original ainda disponível para estorno.")
    db.add(AIWalletCreditGrant(account_id=account.id, reference=reference,
                             original_reference=original_reference, credit_micros=signed, currency="BRL"))
    account.paid_credit_micros += signed
    # A new purchase can regularize debt, but never clears an unexplained cost
    # overrun; that condition requires operator reconciliation.
    has_overrun = db.execute(select(AIWalletOperation.id).where(
        AIWalletOperation.account_id == account.id,
        AIWalletOperation.actual_cost_micros > AIWalletOperation.reserved_cost_micros).limit(1)).first()
    account.billing_blocked = bool(has_overrun) or account.paid_credit_micros < account.paid_spent_micros + account.paid_reserved_micros
    db.flush()
    return {"created": True, "reference": reference, "credit_centavos": signed // MICROS_PER_CENT}


def grant_paid_credit(db, user_id, credit_centavos, reference):
    """Called only after a verified payment; participates in caller transaction."""
    return _grant(db, user_id, credit_centavos, reference)


def reverse_paid_credit(db, user_id, credit_centavos, reference, original_reference):
    """Verified refund/chargeback; spent funds can create blocked debt."""
    return _grant(db, user_id, credit_centavos, reference, original_reference)


def restore_paid_credit(db, user_id, credit_centavos, reference, original_reference):
    """Verified dispute reversal; cannot restore more than net reversed credit."""
    return _grant(db, user_id, credit_centavos, reference, original_reference, restore=True)


def wallet_summary(owner_id):
    with SessionLocal() as db:
        entitlement = _entitlements(db, owner_id)
        account = db.execute(select(AIWalletAccount).where(AIWalletAccount.principal_key == _principal(owner_id, None))).scalar_one_or_none()
        period = _period(db, account, create=False) if account and entitlement.get("ai") else None
        grant, _ceiling, _markup = _limits()
        start, end = _month()
        if period:
            grant = period.grant_credit_micros
            start, end = period.period_start, period.period_end
        elif entitlement.get("ai"):
            prospective_account = account or AIWalletAccount(
                principal_key=_principal(owner_id, None), user_id=owner_id)
            start, end = _allowance_period(db, prospective_account)
            grant, _ceiling, _markup = _effective_limits(db, prospective_account)
        included_spent = period.spent_credit_micros if period else 0
        included_reserved = period.reserved_credit_micros if period else 0
        paid_available = max(0, account.paid_credit_micros - account.paid_spent_micros - account.paid_reserved_micros) if account else 0
        spent = included_spent + (period.paid_spent_credit_micros if period else 0)
        reserved = included_reserved + (period.paid_reserved_credit_micros if period else 0)
        budget = account.budget_credit_micros if account else None
        available = max(0, grant - included_spent - included_reserved) + paid_available
        if budget is not None: available = min(available, max(0, budget - spent - reserved))
        enabled = bool(entitlement.get("ai")) and not bool(account and account.billing_blocked)
        cents_up = lambda micros: (micros + MICROS_PER_CENT - 1) // MICROS_PER_CENT
        return {"currency": "BRL", "period_start": start.isoformat(), "period_end": end.isoformat(),
                "plan": entitlement.get("plan"), "enabled": enabled,
                "monthly_credit_centavos": grant // MICROS_PER_CENT if entitlement.get("ai") else 0,
                "spent_credit_centavos": cents_up(spent), "reserved_credit_centavos": cents_up(reserved),
                "available_credit_centavos": available // MICROS_PER_CENT if enabled else 0,
                "paid_available_credit_centavos": paid_available // MICROS_PER_CENT,
                "budget_credit_centavos": budget // MICROS_PER_CENT if budget is not None else None,
                "billing_blocked": bool(account and account.billing_blocked),
                "pricing_version": period.pricing_version if period else str(getattr(settings, "ai_wallet_pricing_version", "pilot-2026-09")),
                "recharge_supported": True,
                "payments_enabled": bool(getattr(settings, "subscriptions_enabled", False) and getattr(settings, "ai_credit_topups_enabled", False) and getattr(settings, "stripe_secret_key", ""))}


def set_monthly_budget(owner_id, budget_credit_centavos):
    if budget_credit_centavos is not None: _integer(budget_credit_centavos, "budget_credit_centavos")
    with SessionLocal.begin() as db:
        _entitlements(db, owner_id)
        account = _locked_account(db, _principal(owner_id, None), owner_id)
        account.budget_credit_micros = budget_credit_centavos * MICROS_PER_CENT if budget_credit_centavos is not None else None
    return wallet_summary(owner_id)


def quote_cost(*, owner_id, max_cost_micros, cost_center=None):
    """Read-only upper quote; reserve remains the atomic authorization gate."""
    maximum = _integer(max_cost_micros, "max_cost_micros")
    principal = _principal(owner_id, cost_center)
    with SessionLocal() as db:
        if owner_id is not None and not _entitlements(db, owner_id).get("ai"):
            raise AIWalletAccessDenied("Seu plano não inclui as funções de IA.")
        account = db.execute(select(AIWalletAccount).where(
            AIWalletAccount.principal_key == principal)).scalar_one_or_none()
        period = _period(db, account, create=False) if account else None
        if period is not None:
            markup = period.markup_bps
        else:
            _grant_amount, _ceiling, markup = _effective_limits(db, account or AIWalletAccount(
                principal_key=principal, user_id=owner_id))
        # Included and prepaid portions round independently. One extra micro
        # safely covers that split even if another reservation changes balances.
        credit = _credit(maximum, markup) + (1 if maximum and markup % 10_000 else 0)
        return {"maximum_credit_centavos": (credit + MICROS_PER_CENT - 1) // MICROS_PER_CENT,
                "currency": "BRL", "pricing_version": period.pricing_version if period else
                str(getattr(settings, "ai_wallet_pricing_version", "pilot-2026-09"))}
