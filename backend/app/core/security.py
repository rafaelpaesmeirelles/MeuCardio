from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(raw: str) -> str:
    return pwd_context.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(
        {"sub": subject, "exp": expire}, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )


def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from app.models.user import User

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão inválida ou expirada. Entre novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        email = payload.get("sub")
    except JWTError:
        raise credentials_error
    user = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()
    if not user:
        raise credentials_error
    return user


def require_admin(user=Depends(current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Ação restrita a administradores.")
    return user


# Status (já traduzidos, ver app/api/billing.py) que dão direito de uso.
# 'inadimplente' entra de propósito: é o past_due do Stripe, período de
# tolerância em que a cobrança falhou mas o assinante ainda não perdeu acesso.
ACESSO_LIBERADO = {"ativo", "teste", "inadimplente"}


def assinante_ativo(user=Depends(current_user), db: Session = Depends(get_db)):
    """Exige assinatura vigente. Aplicada por router em app/main.py — os únicos
    de acesso livre são health, auth, password_reset, billing e admin."""
    from app.models.subscription import Subscription

    if user.role == "admin":
        return user

    # Filtrar por `kind` é o que impede uma assinatura de curso parceiro de
    # valer como assinatura da plataforma. Sem isso, quem assinasse só um curso
    # (que é venda de terceiro, com repasse) entraria em toda a biblioteca de
    # graça — e quem tivesse a assinatura da plataforma cancelada mas um curso
    # ativo continuaria com acesso, sem que nada acusasse erro.
    sub = (
        db.query(Subscription)
        .filter(Subscription.user_id == user.id, Subscription.kind == "meucardio")
        .order_by(Subscription.id)
        .first()
    )
    if sub is None or sub.status not in ACESSO_LIBERADO:
        raise HTTPException(
            status_code=402,
            detail="Assinatura necessária para acessar este conteúdo.",
        )
    return user
