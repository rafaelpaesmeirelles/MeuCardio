from datetime import datetime, timedelta, timezone
import re

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.runtime import ambiente_atual

BCRYPT_ROUNDS = 12
_BCRYPT_HASH_RE = re.compile(
    r"^\$2[aby]\$(?:0[4-9]|[12][0-9]|3[01])\$[./A-Za-z0-9]{53}$",
    re.ASCII,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
AUTH_COOKIE_NAME = "corvia_session"


def hash_password(raw: str) -> str:
    hashed = bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_ROUNDS))
    return hashed.decode("ascii")


def verify_password(raw: str, hashed: str) -> bool:
    if not isinstance(raw, str) or not isinstance(hashed, str):
        return False
    if _BCRYPT_HASH_RE.fullmatch(hashed) is None:
        return False
    try:
        return bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("ascii"))
    except (TypeError, ValueError, UnicodeEncodeError):
        return False


def create_access_token(subject: str, scope: str = "app", expires_minutes: int | None = None) -> str:
    issued_at = datetime.now(timezone.utc)
    expire = issued_at + timedelta(minutes=expires_minutes if expires_minutes is not None else settings.jwt_expire_minutes)
    return jwt.encode(
        {
            "sub": subject,
            "scope": scope,
            "iat": issued_at,
            "session_iat": issued_at.isoformat(),
            "exp": expire,
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def gravar_cookie_sessao(response: Response, token: str) -> None:
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token,
        max_age=settings.jwt_expire_minutes * 60,
        httponly=True,
        secure=ambiente_atual() == "production",
        samesite="lax",
        path="/",
    )


def limpar_cookie_sessao(response: Response) -> None:
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        httponly=True,
        secure=ambiente_atual() == "production",
        samesite="lax",
        path="/",
    )


def _identidade_do_token(token: str, escopo_exigido: str) -> tuple[str, datetime | None]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except (jwt.PyJWTError, TypeError):
        raise ValueError("token inválido") from None

    escopo = payload.get("scope", "app")
    if escopo != escopo_exigido:
        raise ValueError("escopo inválido")

    email = payload.get("sub")
    if not isinstance(email, str) or not email:
        raise ValueError("sujeito ausente")

    issued_at = None
    raw_issued_at = payload.get("session_iat")
    if raw_issued_at is not None:
        try:
            issued_at = datetime.fromisoformat(raw_issued_at)
            if issued_at.tzinfo is None:
                issued_at = issued_at.replace(tzinfo=timezone.utc)
            else:
                issued_at = issued_at.astimezone(timezone.utc)
        except (TypeError, ValueError):
            raise ValueError("instante de sessão inválido") from None

    return email, issued_at


def _decodificar(token: str, escopo_exigido: str, erro: HTTPException) -> tuple[str, datetime | None]:
    try:
        return _identidade_do_token(token, escopo_exigido)
    except ValueError:
        raise erro


def _marco_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _sessao_valida_para_usuario(user, issued_at: datetime | None) -> bool:
    if user.sessions_valid_after is None:
        return True
    valid_after = _marco_utc(user.sessions_valid_after)
    return issued_at is not None and issued_at > valid_after


def usuario_por_token_app(db: Session, token: str | None):
    from app.models.user import User

    if not token:
        return None
    try:
        email, issued_at = _identidade_do_token(token, "app")
    except ValueError:
        return None
    user = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()
    if not user or not _sessao_valida_para_usuario(user, issued_at):
        return None
    return user


PRESENCA_THROTTLE_SEGUNDOS = 60


def current_user(
    request: Request,
    token_bearer: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão inválida ou expirada. Entre novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = token_bearer or request.cookies.get(AUTH_COOKIE_NAME)
    user = usuario_por_token_app(db, token)
    if not user:
        raise credentials_error

    # Conta Investidor é demonstração somente leitura. Até a telemetria de
    # presença deve permanecer passiva: um GET de navegação não pode virar
    # UPDATE de last_seen_at no banco. Usuários normais/convidados preservam
    # o throttle de presença de sempre.
    if not getattr(user, "investidor", False):
        agora = datetime.now(timezone.utc)
        if user.last_seen_at is None or (agora - user.last_seen_at).total_seconds() > PRESENCA_THROTTLE_SEGUNDOS:
            user.last_seen_at = agora
            db.commit()

    return user


def require_admin(user=Depends(current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Ação restrita a administradores.")
    return user


ACESSO_LIBERADO = {"ativo", "teste", "inadimplente"}


def assinante_ativo(user=Depends(current_user), db: Session = Depends(get_db)):
    from app.services.entitlement import tem_acesso_ao_produto

    if not tem_acesso_ao_produto(db, user):
        raise HTTPException(
            status_code=402,
            detail="Assinatura necessária para acessar este conteúdo.",
        )
    return user


def assinatura_email_ativa(db: Session, user) -> bool:
    if user.role == "admin":
        return True
    if getattr(user, "convidado", False):
        return True

    from app.models.subscription import PLANO_COMPLETO, TIPO_EMAIL, TIPO_MEUCARDIO, Subscription

    sub_email = (
        db.query(Subscription)
        .filter(Subscription.user_id == user.id, Subscription.kind == TIPO_EMAIL)
        .order_by(Subscription.id)
        .first()
    )
    if sub_email is not None and sub_email.status in ACESSO_LIBERADO:
        return True

    sub_principal = (
        db.query(Subscription)
        .filter(Subscription.user_id == user.id, Subscription.kind == TIPO_MEUCARDIO)
        .order_by(Subscription.id)
        .first()
    )
    return (
        sub_principal is not None
        and sub_principal.status in ACESSO_LIBERADO
        and sub_principal.plano == PLANO_COMPLETO
    )


def current_email_account(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    from app.models.email_account import EmailAccount
    from app.models.user import User

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão da caixa de e-mail inválida ou expirada. Entre novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_error
    email_address, issued_at = _decodificar(token, "email", credentials_error)
    conta = db.query(EmailAccount).filter(EmailAccount.email_address == email_address).first()
    if not conta or conta.status != "ativa":
        raise credentials_error
    if not _sessao_valida_para_usuario(conta, issued_at):
        raise credentials_error
    titular = db.get(User, conta.user_id)
    if titular is None or not titular.is_active:
        raise credentials_error
    if getattr(titular, "investidor", False):
        raise HTTPException(
            status_code=403,
            detail="Recurso indisponível no modo investidor.",
        )
    return conta
