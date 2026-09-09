"""Authenticated AI balance and voluntary monthly spending ceiling."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict

from app.core.security import current_user
from app.services.ai_wallet import AIWalletError, set_monthly_budget, wallet_summary

router = APIRouter(prefix="/api/ai/wallet", tags=["carteira-ia"])


class WalletBudgetIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    budget_credit_centavos: int | None = Field(..., ge=0, le=100_000_000, strict=True)


@router.get("")
def get_wallet(user=Depends(current_user)):
    try:
        return wallet_summary(user.id)
    except AIWalletError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.put("/budget")
def update_budget(body: WalletBudgetIn, user=Depends(current_user)):
    try:
        return set_monthly_budget(user.id, body.budget_credit_centavos)
    except AIWalletError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
