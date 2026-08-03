"""Sessão web da conta Corvia por cookie HttpOnly.

O endpoint OAuth2/Bearer original permanece disponível para clientes externos.
O navegador usa este router para que o JWT não fique persistido nem legível em
`localStorage`, `sessionStorage` ou JavaScript.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import create_access_token, gravar_cookie_sessao, limpar_cookie_sessao, verify_password
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _autenticar(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
    if user.status == "pendente":
        raise HTTPException(
            status_code=403,
            detail=(
                "Seu cadastro ainda está em análise. Você recebe acesso assim que um "
                "administrador confirmar seu registro no conselho de classe."
            ),
        )
    if user.status == "rejeitado":
        raise HTTPException(
            status_code=403,
            detail=(
                "Sua solicitação de acesso não foi aprovada. Fale com a administração "
                "do serviço para mais informações."
            ),
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Esta conta está desativada.")
    return user


@router.post("/sessao")
def criar_sessao_navegador(
    response: Response,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    user = _autenticar(db, form.username, form.password)
    gravar_cookie_sessao(response, create_access_token(user.email, scope="app"))
    return {"authenticated": True}


@router.post("/sair")
def sair(response: Response) -> dict[str, bool]:
    """Apaga o cookie mesmo quando o JWT já expirou ou foi revogado."""
    limpar_cookie_sessao(response)
    return {"authenticated": False}
