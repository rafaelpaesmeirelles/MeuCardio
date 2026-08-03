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


def create_access_token(subject: str, scope: str = "app") -> str:
    """Emite JWT com escopo e instante preciso para revogação de sessões.

    `scope` separa o token da conta Corvia (`app`) do token da caixa de e-mail
    (`email`). `session_iat` preserva microssegundos para que uma troca de senha
    invalide imediatamente todos os tokens anteriores sem depender de blacklist.
    """
    issued_at = datetime.now(timezone.utc)
    expire = issued_at + timedelta(minutes=settings.jwt_expire_minutes)
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


def _decodificar(
    token: str,
    escopo_exigido: str,
    erro: HTTPException,
) -> tuple[str, datetime | None]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise erro

    # Token emitido antes da separação de escopos continua sendo token app.
    escopo = payload.get("scope", "app")
    if escopo != escopo_exigido:
        raise erro

    email = payload.get("sub")
    if not email:
        raise erro

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
            raise erro

    return email, issued_at


def _marco_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


# Janela de throttle da presença: gravar `last_seen_at` a cada requisição
# autenticada custaria um UPDATE por chamada de API — no ritmo de uso real do
# app (várias chamadas por segundo enquanto a tela carrega), isso é ruído no
# banco sem ganho de precisão. 60s é fino o bastante para o painel de
# "usuários online" (definido como visto nos últimos 5 minutos, ver
# `app/api/admin.py`) e grosso o bastante para não gerar um UPDATE a cada GET.
PRESENCA_THROTTLE_SEGUNDOS = 60


def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from app.models.user import User

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão inválida ou expirada. Entre novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email, issued_at = _decodificar(token, "app", credentials_error)
    user = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()
    if not user:
        raise credentials_error

    if user.sessions_valid_after is not None:
        valid_after = _marco_utc(user.sessions_valid_after)
        # JWT legado sem `session_iat` permanece aceito apenas enquanto o
        # usuário nunca rotacionou credenciais/sessões. Após o primeiro marco,
        # a ausência do claim é motivo suficiente para rejeição.
        if issued_at is None or issued_at <= valid_after:
            raise credentials_error

    agora = datetime.now(timezone.utc)
    if user.last_seen_at is None or (agora - user.last_seen_at).total_seconds() > PRESENCA_THROTTLE_SEGUNDOS:
        user.last_seen_at = agora
        db.commit()

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


def assinatura_email_ativa(db: Session, user) -> bool:
    """CorvIA Mail (Tarefa 28) é add-on cobrado à parte — não usa
    `assinante_ativo`, que é sobre a assinatura principal. Usada na ativação
    da caixa (`POST /api/email/conta`), não como dependência de rota: a
    própria rota já decide o que fazer quando falso (409, não 402 — 402 no
    `lib/api.ts` do frontend redireciona para `/assinatura`, a página errada
    aqui, que é `/corvia-mail`).

    Admin sempre tem acesso, mesmo skip do Stripe — mesmo padrão de
    `assinante_ativo` acima. Decisão do Rafael em 31/07/2026, quando o preço
    do add-on ainda não estava definido e nem o dono da plataforma conseguia
    ativar a própria caixa para testar.

    Duas formas de ter acesso, desde o plano "completo" (30/07/2026): o add-on
    avulso de sempre (kind='email'), ou o plano da plataforma que já inclui
    CorvIA Mail (kind='meucardio', plano='completo') — sem essa segunda
    checagem, quem pagasse o plano completo continuaria vendo a caixa como não
    assinada."""
    if user.role == "admin":
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


def current_email_account(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Identidade da "sessão email" — só aceita token emitido por
    `POST /api/email/entrar` (scope="email"), nunca o token da conta Corvia.
    É o equivalente, para a caixa de e-mail, do que `current_user` é para o
    resto do sistema: gate de toda rota que lê ou envia mensagem."""
    from app.models.email_account import EmailAccount

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão da caixa de e-mail inválida ou expirada. Entre novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email_address, _ = _decodificar(token, "email", credentials_error)
    conta = db.query(EmailAccount).filter(EmailAccount.email_address == email_address).first()
    if not conta or conta.status != "ativa":
        raise credentials_error
    return conta
