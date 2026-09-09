"""Fulfil only verified paid Stripe events, atomically with wallet grants.

The caller verifies the signature of the ORIGINAL body before invoking
handle_verified_event. A browser redirect never grants credits.
"""
from datetime import datetime, timedelta, timezone
import hashlib
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session
import stripe

from app.core.config import settings
from app.models.ai_credit_purchase import AICreditPurchase

PURPOSE = "corvia_ai_credits"


def _plain(value):
    # Stripe 15 StripeObject is no longer a dict and has no .get method.
    return value.to_dict() if isinstance(value, stripe.StripeObject) else value


def packages() -> list[int]:
    try:
        values = sorted({int(v.strip()) for v in settings.ai_credit_topup_packages_centavos.split(",") if v.strip()})
    except (ValueError, AttributeError):
        return []
    return values if values and all(100 <= n <= 100_000 for n in values) else []


def _client():
    return stripe.StripeClient(settings.stripe_secret_key, max_network_retries=0)


def _lock(db: Session, key: str) -> None:
    # One lock order: purchase, then account (wallet). Production is PostgreSQL.
    if db.get_bind().dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"), {"key": "ai-credit:" + key})


def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def create_checkout(db: Session, user, amount_centavos: int, request_key: str) -> dict:
    if not settings.subscriptions_enabled or not settings.ai_credit_topups_enabled:
        raise HTTPException(409, "As recargas serão disponibilizadas na abertura das assinaturas.")
    from app.services.commercial_plans import require_ai_entitlement
    require_ai_entitlement(db, user)
    if not settings.stripe_secret_key:
        raise HTTPException(503, "Pagamento temporariamente indisponível.")
    if amount_centavos not in packages():
        raise HTTPException(422, "Escolha um dos pacotes de créditos disponíveis.")
    _lock(db, f"checkout:{user.id}:{request_key}")
    purchase = db.scalar(select(AICreditPurchase).where(
        AICreditPurchase.user_id == user.id, AICreditPurchase.request_key == request_key,
    ))
    if purchase:
        if purchase.amount_centavos != amount_centavos:
            raise HTTPException(409, "Esta solicitação já pertence a outro pacote.")
        if purchase.status == "paid":
            raise HTTPException(409, "Esta recarga já foi confirmada. Consulte seu saldo.")
        if purchase.status in {"expired", "failed", "reversed"} or datetime.now(timezone.utc) - _utc(purchase.created_at) > timedelta(minutes=30):
            raise HTTPException(409, "Esta solicitação expirou. Inicie uma nova recarga.")
        if purchase.checkout_url:
            return {"url": purchase.checkout_url, "purchase_id": purchase.id}
    else:
        purchase = AICreditPurchase(id=str(uuid4()), user_id=user.id, request_key=request_key,
                                    amount_centavos=amount_centavos, currency="brl", status="pending")
        db.add(purchase)
    db.commit()  # Durable local identity BEFORE a network request can succeed.
    purchase_id = purchase.id
    metadata = {"purpose": PURPOSE, "purchase_id": purchase_id}
    # Stable letters ensure retries use identical params and idempotency key.
    suffix = "".join(chr(97 + int(c, 16)) for c in hashlib.sha256(purchase_id.encode()).hexdigest()[:8])
    params = {
        "mode": "payment",
        "client_reference_id": purchase_id,
        "metadata": metadata,
        "payment_intent_data": {"metadata": metadata},
        "line_items": [{"quantity": 1, "price_data": {
            "currency": "brl", "unit_amount": purchase.amount_centavos,
            "product_data": {"name": "Créditos de IA CorVIA", "description": "Recarga avulsa, sem renovação automática."},
        }}],
        "success_url": settings.public_url.rstrip("/") + "/assinatura?recarga=recebida",
        "cancel_url": settings.public_url.rstrip("/") + "/assinatura?recarga=cancelada",
        "expires_at": int((_utc(purchase.created_at) + timedelta(minutes=60)).timestamp()),
    }
    # The pinned SDK's API predates integration_identifier on some installations;
    # pass it only when that API version advertises support.
    if str(getattr(stripe, "api_version", "")) >= "2026-03-25":
        params["integration_identifier"] = "corvia_ai_credits_" + suffix
    try:
        session = _plain(_client().v1.checkout.sessions.create(params, options={"idempotency_key": "ai-credit-" + purchase_id}))
    except stripe.StripeError:
        # Ambiguous transport failures retain the identity for safe retry.
        raise HTTPException(503, "Não foi possível abrir o pagamento. Tente novamente nesta solicitação.") from None
    if not session.get("id") or not session.get("url"):
        raise HTTPException(503, "O provedor não disponibilizou o pagamento.")
    _lock(db, purchase_id)
    purchase = db.scalar(select(AICreditPurchase).where(AICreditPurchase.id == purchase_id).with_for_update().execution_options(populate_existing=True))
    if purchase.checkout_session_id not in (None, session["id"]):
        raise HTTPException(409, "Pagamento em reconciliação.")
    purchase.checkout_session_id = session["id"]
    purchase.checkout_url = session["url"]
    db.commit()
    return {"url": session["url"], "purchase_id": purchase_id}


def _purchase(db: Session, obj: dict) -> AICreditPurchase | None:
    metadata = obj.get("metadata") or {}
    purchase_id = metadata.get("purchase_id") if metadata.get("purpose") == PURPOSE else None
    if purchase_id:
        _lock(db, purchase_id)
        return db.scalar(select(AICreditPurchase).where(AICreditPurchase.id == purchase_id).with_for_update())
    intent = obj.get("payment_intent")
    if isinstance(intent, dict):
        intent = intent.get("id")
    if not intent:
        return None
    candidate = db.scalar(select(AICreditPurchase.id).where(AICreditPurchase.payment_intent_id == intent))
    if not candidate:
        # A dispute may arrive before checkout.completed associates the PI.
        # Recover server-owned metadata instead of acknowledging and losing it.
        if not settings.stripe_secret_key:
            raise HTTPException(503, "Reconciliação de pagamento indisponível.")
        try:
            payment = _plain(_client().v1.payment_intents.retrieve(intent))
        except stripe.StripeError:
            raise HTTPException(503, "Reconciliação de pagamento temporariamente indisponível.") from None
        meta = payment.get("metadata") or {}
        if meta.get("purpose") != PURPOSE:
            return None
        candidate = meta.get("purchase_id")
        if not candidate:
            raise HTTPException(409, "Recarga aguardando identificação.")
        _lock(db, candidate)
        purchase = db.scalar(select(AICreditPurchase).where(AICreditPurchase.id == candidate).with_for_update())
        if purchase is None:
            raise HTTPException(409, "Recarga aguardando reconciliação.")
        if payment.get("amount") != purchase.amount_centavos or payment.get("currency") != purchase.currency:
            raise HTTPException(400, "Pagamento incompatível com a recarga registrada.")
        if purchase.payment_intent_id not in (None, intent):
            raise HTTPException(400, "Identidade de pagamento divergente.")
        purchase.payment_intent_id = intent
        return purchase
    _lock(db, candidate)
    return db.scalar(select(AICreditPurchase).where(AICreditPurchase.id == candidate).with_for_update())


def _reverse(db: Session, purchase: AICreditPurchase, target: int) -> None:
    if target == purchase.reversed_centavos:
        return
    if not 0 <= target <= purchase.amount_centavos:
        raise HTTPException(400, "Valor de estorno incompatível com a recarga.")
    if purchase.paid_at and purchase.user_id is not None:
        from app.services.ai_wallet import reverse_paid_credit, restore_paid_credit
        delta = target - purchase.reversed_centavos
        method = reverse_paid_credit if delta > 0 else restore_paid_credit
        # Include reason state: the same net amount can recur after a won dispute.
        reference = f"purchase:{purchase.id}:net:{target}:refund:{purchase.refunded_centavos}:dispute:{purchase.dispute_status or 'none'}"
        method(db, user_id=purchase.user_id, credit_centavos=abs(delta),
               reference=reference, original_reference="purchase:" + purchase.id)
    purchase.reversed_centavos = target
    if purchase.paid_at and target == purchase.amount_centavos:
        purchase.status = "reversed"
    elif purchase.paid_at:
        purchase.status = "paid"


def handle_verified_event(db: Session, event: dict) -> bool:
    """Return True for our payment; commit financial changes together."""
    event = _plain(event)
    kind = event.get("type", "")
    if kind not in {"checkout.session.completed", "checkout.session.async_payment_succeeded",
                    "checkout.session.async_payment_failed", "checkout.session.expired",
                    "charge.refunded", "charge.dispute.created", "charge.dispute.closed"}:
        return False
    obj = event["data"]["object"]
    purchase = _purchase(db, obj)
    if purchase is None:
        # Explicitly ours but missing the durable order: request redelivery.
        if (obj.get("metadata") or {}).get("purpose") == PURPOSE:
            raise HTTPException(409, "Recarga aguardando reconciliação.")
        return False
    if kind.startswith("checkout.session."):
        if obj.get("mode") != "payment" or obj.get("currency") != purchase.currency or obj.get("amount_total") != purchase.amount_centavos:
            raise HTTPException(400, "Pagamento incompatível com a recarga registrada.")
        if purchase.checkout_session_id not in (None, obj.get("id")):
            raise HTTPException(400, "Identidade de pagamento divergente.")
        if not obj.get("id"):
            raise HTTPException(400, "Pagamento sem identificação.")
        purchase.checkout_session_id = obj["id"]
        intent = obj.get("payment_intent")
        if isinstance(intent, dict):
            intent = intent.get("id")
        if intent:
            if purchase.payment_intent_id not in (None, intent):
                raise HTTPException(400, "Identidade de pagamento divergente.")
            purchase.payment_intent_id = intent
        if kind in {"checkout.session.completed", "checkout.session.async_payment_succeeded"} and obj.get("payment_status") == "paid":
            if purchase.paid_at is None:
                if purchase.user_id is None:
                    raise HTTPException(409, "Titular da recarga indisponível para reconciliação.")
                from app.services.ai_wallet import grant_paid_credit
                grant_paid_credit(db, user_id=purchase.user_id, credit_centavos=purchase.amount_centavos,
                                  reference="purchase:" + purchase.id)
                purchase.paid_at = datetime.now(timezone.utc)
                purchase.status = "paid"
                reversed_before_payment = purchase.reversed_centavos
                purchase.reversed_centavos = 0
                _reverse(db, purchase, reversed_before_payment)
        elif purchase.paid_at is None and kind in {"checkout.session.expired", "checkout.session.async_payment_failed"}:
            purchase.status = "expired" if kind.endswith("expired") else "failed"
    else:
        if obj.get("currency") != purchase.currency:
            raise HTTPException(400, "Moeda de estorno incompatível.")
        if kind == "charge.refunded":
            amount = obj.get("amount_refunded", 0)
            if type(amount) is not int or not 0 <= amount <= purchase.amount_centavos:
                raise HTTPException(400, "Valor de estorno incompatível.")
            purchase.refunded_centavos = max(purchase.refunded_centavos, amount)
        else:
            amount = obj.get("amount")
            dispute_id = obj.get("id")
            if type(amount) is not int or not 0 <= amount <= purchase.amount_centavos or not dispute_id:
                raise HTTPException(400, "Disputa incompatível com a recarga.")
            if purchase.dispute_id not in (None, dispute_id):
                raise HTTPException(409, "Disputa adicional requer reconciliação.")
            purchase.dispute_id = dispute_id
            terminal = purchase.dispute_status in {"won", "lost", "warning_closed"}
            if kind == "charge.dispute.closed":
                outcome = obj.get("status")
                if outcome not in {"won", "lost", "warning_closed"}:
                    raise HTTPException(409, "Disputa aguardando resultado final.")
                if terminal and outcome != purchase.dispute_status:
                    raise HTTPException(409, "Resultados de disputa divergentes.")
                purchase.dispute_status = outcome
                purchase.disputed_centavos = 0 if outcome in {"won", "warning_closed"} else amount
            elif not terminal:
                purchase.dispute_status = "open"
                purchase.disputed_centavos = amount
        _reverse(db, purchase, min(purchase.amount_centavos, purchase.refunded_centavos + purchase.disputed_centavos))
    db.commit()
    return True
