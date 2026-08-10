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
# Formato modular bcrypt completo: versão histórica aceita, custo válido,
# salt de 22 caracteres e checksum de 31. A validação evita enviar entradas
# truncadas ao binding Rust do bcrypt 4.0.1, que pode gerar PanicException.
_BCRYPT_HASH_RE = re.compile(
    r"^\$2[aby]\$(?:0[4-9]|[12][0-9]|3[01])\$[./A-Za-z0-9]{53}$",
    re.ASCII,
)

# O Bearer permanece disponível para clientes externos, testes e integrações.
# No navegador, a sessão principal usa cookie HttpOnly e não fica acessível a
# JavaScript. `auto_error=False` permite escolher conscientemente entre os dois.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
AUTH_COOKIE_NAME = "corvia_session"


def hash_password(raw: str) -> str:
    """Gera hash bcrypt compatível com os hashes já armazenados pelo Passlib."""
    hashed = bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_ROUNDS))
    return hashed.decode("ascii")


def verify_password(raw: str, hashed: str) -> bool:
    """Valida hashes bcrypt existentes sem regravar credenciais no banco."""
    if not isinstance(raw, str) or not isinstance(hashed, str):
        return False
    if _BCRYPT_HASH_RE.fullmatch(hashed) is None:
        return False
    try:
        return bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("ascii"))
    except (TypeError, ValueError, UnicodeEncodeError):
        return False


def create_access_token(subject: str, scope: str = "app", expires_minutes: int | None = None) -> str:
    """Emite JWT com escopo e instante preciso para revogação de sessões.

    `scope` separa o token da conta Corvia (`app`) do token da caixa de e-mail
    (`email`). `session_iat` preserva microssegundos para que uma troca de senha
    invalide imediatamente todos os tokens anteriores sem depender de blacklist.

    `expires_minutes` sobrescreve `settings.jwt_expire_minutes` quando informado
    — usado pelo "Permanecer conectado" do CorvIA Mail (09/08/2026, pedido do
    Rafael: a sessão da caixa de e-mail expirava em 12h como qualquer sessão
    comum, e ele precisava digitar a senha da caixa de novo toda vez que
    voltava depois de um tempo — as duas caixas de referência que ele mandou,
    Yahoo e Gmail, sempre oferecem essa opção)."""
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
    """Entrega a sessão do navegador sem expor o JWT ao JavaScript.

    `samesite="lax"`, não "strict" (09/08/2026, bug real do Rafael: reconectar
    Google/Microsoft derrubava para a tela de login). Causa raiz: o retorno do
    OAuth é uma navegação de nível superior que chega a `/api/agenda/oauth/
    google/callback` vinda de `accounts.google.com` — cross-site do ponto de
    vista do navegador — e o backend então redireciona (303) de volta para
    `/agenda`. Com `Strict`, o cookie de sessão não acompanha essa cadeia de
    navegação iniciada por outro site, mesmo o destino final sendo o próprio
    corvia.med.br; o `GET /auth/me` que a página `/agenda` dispara ao montar
    chega sem cookie, toma 401, e o interceptor genérico manda para `/entrar`
    — não é sessão expirada de verdade, é o cookie que nunca chegou naquela
    requisição específica. `Lax` continua enviando o cookie em navegação de
    nível superior por GET (exatamente este caso) e continua retendo-o em
    requisições cross-site que não são navegação de topo (POST/PUT/DELETE via
    fetch, iframe, etc.) — a proteção contra CSRF que importa na prática não
    muda; é o mesmo default que Django, Rails e a maioria dos frameworks usam
    para cookie de sessão justamente por causa deste tipo de fluxo (OAuth,
    link de e-mail, retorno de gateway de pagamento)."""
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

    # Token emitido antes da separação de escopos continua sendo token app.
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


def _decodificar(
    token: str,
    escopo_exigido: str,
    erro: HTTPException,
) -> tuple[str, datetime | None]:
    try:
        return _identidade_do_token(token, escopo_exigido)
    except ValueError:
        raise erro


def _marco_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _sessao_valida_para_usuario(user, issued_at: datetime | None) -> bool:
    """Genérica de propósito: usada tanto para `User` (sessão principal)
    quanto para `EmailAccount` (sessão da caixa CorvIA Mail, issue #52 gate
    final) — as duas entidades expõem `sessions_valid_after` com o mesmo
    contrato (marcado por um listener de `password_hash` em cada modelo)."""
    if user.sessions_valid_after is None:
        return True
    valid_after = _marco_utc(user.sessions_valid_after)
    # JWT legado sem `session_iat` permanece aceito apenas enquanto o usuário
    # nunca rotacionou credenciais/sessões. Após o primeiro marco, a ausência
    # do claim é motivo suficiente para rejeição.
    return issued_at is not None and issued_at > valid_after


def usuario_por_token_app(db: Session, token: str | None):
    """Resolve um usuário por JWT app para HTTP ou WebSocket.

    Retorna ``None`` em qualquer falha e aplica o mesmo marco de revogação usado
    por `current_user`, evitando que o WebSocket mantenha uma regra paralela.
    """
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


# Janela de throttle da presença: gravar `last_seen_at` a cada requisição
# autenticada custaria um UPDATE por chamada de API — no ritmo de uso real do
# app (várias chamadas por segundo enquanto a tela carrega), isso é ruído no
# banco sem ganho de precisão. 60s é fino o bastante para o painel de
# "usuários online" (definido como visto nos últimos 5 minutos, ver
# `app/api/admin.py`) e grosso o bastante para não gerar um UPDATE a cada GET.
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


def current_email_account(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Identidade da sessão separada da caixa de e-mail.

    Continua Bearer de propósito nesta etapa: a caixa tem credencial, escopo e
    ciclo próprios. O cookie app nunca é usado como sessão da caixa.
    """
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
    # Achado de auditoria (issue #52, gate final): faltava aqui o mesmo marco
    # de revogação que `current_user`/`usuario_por_token_app` já aplicam à
    # sessão principal — sem ele, trocar a senha da caixa não invalidava
    # tokens já emitidos (inclusive "permanecer conectado", até 30 dias).
    if not _sessao_valida_para_usuario(conta, issued_at):
        raise credentials_error
    # Achado relacionado, mesmo gate: a conta principal desativada (ex.:
    # banimento por admin) não derrubava a sessão da caixa — a coerência
    # pedida com a sessão principal exige as duas caírem juntas.
    titular = db.get(User, conta.user_id)
    if titular is None or not titular.is_active:
        raise credentials_error
    return conta
