"""Renovação deslizante da sessão própria do CorvIA Mail.

Mantém a separação de credenciais: somente um token `scope=email` ainda válido
pode ser renovado. A sessão principal da Corvia não abre nem renova a caixa.
"""
from fastapi import APIRouter, Depends

from app.core.security import create_access_token, current_email_account
from app.models.email_account import EmailAccount

router = APIRouter(prefix="/api/email", tags=["caixa de e-mail"])
SESSAO_EMAIL_PERSISTENTE_MINUTOS = 30 * 24 * 60


@router.post("/renovar-sessao")
def renovar_sessao_email(
    conta: EmailAccount = Depends(current_email_account),
) -> dict[str, str]:
    token = create_access_token(
        conta.email_address,
        scope="email",
        expires_minutes=SESSAO_EMAIL_PERSISTENTE_MINUTOS,
    )
    return {"access_token": token, "token_type": "bearer"}
