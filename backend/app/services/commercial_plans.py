"""Commercial catalogue and server-side feature entitlements.

No payment or price migration occurs here. AI entitlement is separate from the
wallet's budget reservation: courtesy and legacy access also require a budget.
"""
from __future__ import annotations
import calendar
from datetime import date, datetime, timezone

from fastapi import HTTPException
from app.core.config import settings

from app.models.subscription import (
    CURRENT_COMMERCIAL_VERSION, LEGACY_COMMERCIAL_VERSION,
    PLANO_BASICO, PLANO_BASICO_MAIL, PLANO_IA, PLANO_COMPLETO,
    TIPO_MEUCARDIO, TIPO_EMAIL, Subscription,
)

PLANS = {
    PLANO_BASICO: {"name": "CorVIA Básico", "price_centavos": 9990, "ai": False, "mail": False},
    PLANO_BASICO_MAIL: {"name": "CorVIA Básico + Mail", "price_centavos": 11990, "ai": False, "mail": True},
    PLANO_IA: {"name": "CorVIA IA", "price_centavos": 14990, "ai": True, "mail": False},
    PLANO_COMPLETO: {"name": "CorVIA Completo", "price_centavos": 16990, "ai": True, "mail": True},
}


def monthly_price(plan: str) -> int:
    if plan not in PLANS:
        raise HTTPException(status_code=400, detail="Plano inválido.")
    return int(getattr(settings, f"commercial_price_{plan}_centavos", PLANS[plan]["price_centavos"]))


def mail_addon_price() -> int:
    basic_delta = monthly_price(PLANO_BASICO_MAIL) - monthly_price(PLANO_BASICO)
    ai_delta = monthly_price(PLANO_COMPLETO) - monthly_price(PLANO_IA)
    return basic_delta if basic_delta > 0 and basic_delta == ai_delta else 0


def catalogue(*, subscriptions_enabled: bool) -> dict:
    checkout_available = bool(subscriptions_enabled and settings.stripe_secret_key)
    return {
        "currency": "brl", "commercial_version": CURRENT_COMMERCIAL_VERSION,
        "subscriptions_enabled": subscriptions_enabled,
        "checkout_available": checkout_available,
        "plans": [
            {"id": key, "name": value["name"], "price_centavos": monthly_price(key),
             "periodicidade": "mensal",
             "checkout_available": checkout_available and monthly_price(key) > 0,
             "ai_monthly_credit_centavos": int(getattr(settings, "ai_wallet_monthly_credit_centavos", 4000)) if value["ai"] else 0,
             "features": {"tudo_com_tudo": True, "ai": value["ai"], "mail": value["mail"]}}
            for key, value in PLANS.items()
        ],
    }


def plan_features(plan: str | None, commercial_version: str | None) -> dict[str, bool]:
    version = commercial_version or LEGACY_COMMERCIAL_VERSION
    if version == LEGACY_COMMERCIAL_VERSION:
        # The previous two-plan catalogue included AI in both plans.
        known = plan in {PLANO_BASICO, PLANO_COMPLETO}
        return {"tudo_com_tudo": known, "ai": known, "mail": plan == PLANO_COMPLETO}
    if version == CURRENT_COMMERCIAL_VERSION and plan in PLANS:
        return {"tudo_com_tudo": True, "ai": PLANS[plan]["ai"], "mail": PLANS[plan]["mail"]}
    return {"tudo_com_tudo": False, "ai": False, "mail": False}


def resolve_entitlements(db, user) -> dict:
    from app.services.entitlement import ACESSO_LIBERADO

    result = {"tudo_com_tudo": False, "ai": False, "mail": False,
              "source": "none", "plan": None, "commercial_version": None}
    if not getattr(user, "is_active", True):
        return result
    investor = bool(getattr(user, "investidor", False))
    if getattr(user, "role", None) == "admin" or getattr(user, "convidado", False) or investor:
        result.update(tudo_com_tudo=True, ai=True, mail=not investor,
                      source="investor" if investor else "administrative")
        return result
    sub = db.query(Subscription).filter(
        Subscription.user_id == user.id, Subscription.kind == TIPO_MEUCARDIO,
        Subscription.status.in_(ACESSO_LIBERADO),
    ).order_by(Subscription.id.desc()).first()
    if sub is not None:
        version = getattr(sub, "commercial_version", None) or LEGACY_COMMERCIAL_VERSION
        result.update(plan_features(sub.plano, version))
        result.update(source="subscription", plan=sub.plano, commercial_version=version)
        end = _as_utc(sub.current_period_end)
        start = _as_utc(getattr(sub, "current_period_start", None))
        now = datetime.now(timezone.utc)
        current_paid_period = sub.status in {"ativo", "teste"} and end is not None and end > now
        if version == CURRENT_COMMERCIAL_VERSION:
            current_paid_period = current_paid_period and start is not None and start <= now
            result["mail"] = bool(result["mail"] and current_paid_period)
        # Reading the corpus keeps the previous grace policy. Paid generation
        # and allowance renewal require a current active/trial billing cycle.
        result["ai"] = bool(result["ai"] and current_paid_period)
    # Preserve independently purchased Mail subscriptions.
    addon = db.query(Subscription.id).filter(
        Subscription.user_id == user.id, Subscription.kind == TIPO_EMAIL,
        Subscription.status.in_(ACESSO_LIBERADO),
    ).first()
    if addon is not None:
        result["mail"] = True
    return result


def _as_utc(value):
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def _anniversary(anchor: datetime, year: int, month: int) -> datetime:
    return anchor.replace(year=year, month=month, day=min(anchor.day, calendar.monthrange(year, month)[1]))


def ai_allowance_period(db, user) -> tuple[date, date]:
    """Confirmed monthly cycle; annual legacy contracts receive monthly windows."""
    if not resolve_entitlements(db, user)["ai"]:
        raise ValueError("No current paid or administrative AI entitlement")
    now = datetime.now(timezone.utc)
    if getattr(user, "role", None) == "admin" or getattr(user, "convidado", False) or getattr(user, "investidor", False):
        start = date(now.year, now.month, 1)
        return start, date(now.year + (now.month == 12), now.month % 12 + 1, 1)
    sub = db.query(Subscription).filter(
        Subscription.user_id == user.id, Subscription.kind == TIPO_MEUCARDIO,
        Subscription.status.in_({"ativo", "teste"}),
    ).order_by(Subscription.id.desc()).first()
    if sub is None:
        raise ValueError("No confirmed subscription")
    version = sub.commercial_version or LEGACY_COMMERCIAL_VERSION
    anchor = _as_utc(sub.current_period_start)
    end = _as_utc(sub.current_period_end)
    if version == CURRENT_COMMERCIAL_VERSION:
        if anchor is None or end is None or not anchor <= now < end:
            raise ValueError("No confirmed current billing period")
        return anchor.date(), end.date()
    anchor = anchor or _as_utc(sub.created_at)
    if anchor is None or end is None or end <= now:
        raise ValueError("No legacy cycle anchor")
    start = _anniversary(anchor, now.year, now.month)
    if start > now:
        start = _anniversary(anchor, now.year - (now.month == 1), (now.month - 2) % 12 + 1)
    next_start = _anniversary(anchor, start.year + (start.month == 12), start.month % 12 + 1)
    return start.date(), min(next_start, end).date()


def require_ai_entitlement(db, user) -> dict:
    result = resolve_entitlements(db, user)
    if not result["ai"]:
        raise HTTPException(status_code=403, detail={
            "code": "ai_plan_required",
            "message": "Seu plano não inclui IA. Escolha CorVIA IA ou CorVIA Completo.",
        })
    return result


def ai_allowance_fraction(db, user) -> tuple[int, int]:
    """Prorate the first AI allowance to the paid upgrade's remaining cycle."""
    if not resolve_entitlements(db, user)["ai"]:
        raise ValueError("No current AI entitlement")
    if getattr(user, "role", None) == "admin" or getattr(user, "convidado", False) or getattr(user, "investidor", False):
        return 1, 1
    sub = db.query(Subscription).filter(
        Subscription.user_id == user.id, Subscription.kind == TIPO_MEUCARDIO,
        Subscription.status.in_({"ativo", "teste"}),
    ).order_by(Subscription.id.desc()).first()
    if sub is None:
        raise ValueError("No confirmed subscription")
    if (sub.commercial_version or LEGACY_COMMERCIAL_VERSION) == LEGACY_COMMERCIAL_VERSION:
        return 1, 1
    start, end = _as_utc(sub.current_period_start), _as_utc(sub.current_period_end)
    access = _as_utc(sub.ai_access_started_at)
    if start is None or end is None or end <= start or access is None:
        raise ValueError("No confirmed AI access start")
    if access <= start:
        return 1, 1
    total = int((end - start).total_seconds())
    remaining = max(0, int((end - access).total_seconds()))
    return min(remaining, total), max(total, 1)
