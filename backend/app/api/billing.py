from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user
from app.models.subscription import Subscription
from app.models.user import User

# O prefixo precisa incluir /api: o Caddy usa `handle /api/*` (que, ao contrário
# de `handle_path`, não remove o prefixo antes de repassar ao backend).
router = APIRouter(prefix="/api/billing", tags=["billing"])

stripe.api_key = settings.stripe_secret_key

# Tradução dos status do Stripe para o vocabulário em português usado no banco
# e na interface. Sem isso o valor cru em inglês vaza para a tela do assinante.
STATUS_STRIPE_PT = {
    "active": "ativo",
    "trialing": "teste",
    "past_due": "inadimplente",   # cobrança falhou, mas ainda em período de tolerância
    "unpaid": "suspenso",         # tolerância esgotada
    "canceled": "cancelado",
    "incomplete": "pendente",
    "incomplete_expired": "inativo",
    "paused": "pausado",
}


def traduzir_status(status_stripe: str) -> str:
    """Status desconhecido (Stripe pode introduzir novos) vira 'pendente' em vez
    de vazar o termo em inglês — pendente não libera acesso, que é o lado seguro."""
    return STATUS_STRIPE_PT.get(status_stripe, "pendente")


def _fim_do_periodo(obj) -> datetime | None:
    """Desde a versão de API 2025-03-31.basil o current_period_end saiu do objeto
    Subscription e passou a viver em cada item da assinatura."""
    itens = (obj.get("items") or {}).get("data") or []
    if not itens:
        return None
    fim = itens[0].get("current_period_end")
    if not fim:
        return None
    return datetime.fromtimestamp(fim, tz=timezone.utc)


def _obter_ou_criar_assinatura(db: Session, user: User) -> Subscription:
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if sub:
        return sub
    sub = Subscription(user_id=user.id)
    db.add(sub)
    try:
        db.commit()
    except IntegrityError:
        # Duas chamadas simultâneas de /checkout: a que perdeu a corrida relê a
        # linha criada pela outra em vez de estourar 500 no unique de user_id.
        db.rollback()
        sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
        if sub is None:
            raise
        return sub
    db.refresh(sub)
    return sub


def _aplicar_evento(db: Session, obj, quando: datetime, alteracoes) -> None:
    """Grava as alterações se o evento for mais novo que o último já aplicado.

    O Stripe reentrega eventos e não garante ordem de chegada, então um evento
    atrasado pode desfazer um estado mais recente (ex.: um cancelamento antigo
    chegando depois de uma reativação)."""
    sub = db.query(Subscription).filter(Subscription.stripe_customer_id == obj["customer"]).first()
    if sub is None:
        return
    if sub.last_event_at is not None and quando < sub.last_event_at:
        return
    alteracoes(sub)
    sub.last_event_at = quando
    db.commit()


@router.post("/checkout")
def criar_checkout(db: Session = Depends(get_db), user: User = Depends(current_user)):
    sub = _obter_ou_criar_assinatura(db, user)

    if not sub.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email, name=user.full_name)
        sub.stripe_customer_id = customer["id"]
        db.commit()

    session = stripe.checkout.Session.create(
        customer=sub.stripe_customer_id,
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
        success_url=f"{settings.public_url}/assinatura?status=sucesso",
        cancel_url=f"{settings.public_url}/assinatura?status=cancelado",
    )
    return {"checkout_url": session["url"]}


@router.get("/status")
def status_assinatura(db: Session = Depends(get_db), user: User = Depends(current_user)):
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub:
        return {"status": "inativo", "current_period_end": None}
    return {"status": sub.status, "current_period_end": sub.current_period_end}


@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Assinatura de webhook inválida.")

    tipo = event["type"]
    obj = event["data"]["object"]
    quando = datetime.fromtimestamp(event["created"], tz=timezone.utc)

    if tipo in ("customer.subscription.created", "customer.subscription.updated"):
        def alterar(sub):
            sub.stripe_subscription_id = obj["id"]
            sub.status = traduzir_status(obj["status"])
            fim = _fim_do_periodo(obj)
            if fim is not None:
                sub.current_period_end = fim

        _aplicar_evento(db, obj, quando, alterar)

    elif tipo == "customer.subscription.deleted":
        _aplicar_evento(db, obj, quando, lambda sub: setattr(sub, "status", "cancelado"))

    elif tipo == "invoice.payment_failed":
        _aplicar_evento(db, obj, quando, lambda sub: setattr(sub, "status", "inadimplente"))

    return {"received": True}
