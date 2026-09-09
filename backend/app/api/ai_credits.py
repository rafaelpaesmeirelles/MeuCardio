"""Optional prepaid credits; no automatic top-up or card charging."""
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user
from app.services.ai_credit_payments import create_checkout, packages

router = APIRouter(prefix="/api/ai-credits", tags=["ai-credits"])


class CreditCheckoutInput(BaseModel):
    amount_centavos: int = Field(gt=0, strict=True)
    request_key: UUID


@router.get("/packages")
def list_packages(user=Depends(current_user)):
    return {
        "currency": "BRL",
        "enabled": bool(settings.subscriptions_enabled and settings.ai_credit_topups_enabled and settings.stripe_secret_key),
        "packages": [{"amount_centavos": n, "credit_centavos": n} for n in packages()],
        "automatic_topup": False,
    }


@router.post("/checkout")
def checkout(body: CreditCheckoutInput, user=Depends(current_user), db: Session = Depends(get_db)):
    return create_checkout(db, user, body.amount_centavos, str(body.request_key))
