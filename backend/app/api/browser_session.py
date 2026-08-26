"""Sessão web da conta Corvia por cookie HttpOnly.

O endpoint OAuth2/Bearer original permanece disponível para clientes externos.
O navegador usa este router para que o JWT não fique persistido nem legível em
`localStorage`, `sessionStorage` ou JavaScript.
"""
from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.runtime import ambiente_atual
from app.core.security import (
    AUTH_COOKIE_NAME,
    create_access_token,
    limpar_cookie_sessao,
    session_id_from_token,
    verify_password,
)
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])
SESSAO_PERSISTENTE_MINUTOS = 30 * 24 * 60


def _autenticar(
    db: Session, email: str, password: str, request: Request,
    background_tasks: BackgroundTasks,
) -> User:
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    def falha(reason: str) -> None:
        if not user:
            return
        from app.services.access_security import record_failed_login
        access = record_failed_login(
            db, user_id=user.id, surface="corvia_os", request=request, reason=reason,
        )
        if access.risk_level == "alto":
            from app.services import emails
            # HTTPException nao preserva BackgroundTasks da rota; alerta de
            # tentativa recusada precisa ser enviado antes da resposta 401/403.
            emails.enviar_alerta_seguranca(access.id)

    if not user or not verify_password(password, user.password_hash):
        falha("invalid_credentials")
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
    if user.status == "pendente":
        falha("account_pending")
        raise HTTPException(
            status_code=403,
            detail=(
                "Seu cadastro ainda está em análise. Você recebe acesso assim que um "
                "administrador confirmar seu registro no conselho de classe."
            ),
        )
    if user.status == "rejeitado":
        falha("account_rejected")
        raise HTTPException(
            status_code=403,
            detail=(
                "Sua solicitação de acesso não foi aprovada. Fale com a administração "
                "do serviço para mais informações."
            ),
        )
    if not user.is_active:
        falha("account_inactive")
        raise HTTPException(status_code=403, detail="Esta conta está desativada.")
    return user


def _cookie_base(response: Response, token: str, *, max_age: int | None) -> None:
    kwargs = {
        "key": AUTH_COOKIE_NAME,
        "value": token,
        "httponly": True,
        "secure": ambiente_atual() == "production",
        "samesite": "lax",
        "path": "/",
    }
    if max_age is not None:
        kwargs["max_age"] = max_age
    response.set_cookie(**kwargs)


@router.post("/sessao")
def criar_sessao_navegador(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    form: OAuth2PasswordRequestForm = Depends(),
    permanecer_conectado: bool = Form(False),
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    user = _autenticar(db, form.username, form.password, request, background_tasks)
    from app.services.access_security import start_session
    session_id, _access = start_session(
        db, subject=user, user_id=user.id, surface="corvia_os", request=request,
    )
    from app.api.chat import gerenciador
    background_tasks.add_task(gerenciador.encerrar_usuario, user.id)
    if _access.risk_level == "alto":
        from app.services import emails
        background_tasks.add_task(emails.enviar_alerta_seguranca, _access.id)
    if permanecer_conectado:
        token = create_access_token(
            user.email,
            scope="app",
            expires_minutes=SESSAO_PERSISTENTE_MINUTOS,
            session_id=session_id,
        )
        _cookie_base(response, token, max_age=SESSAO_PERSISTENTE_MINUTOS * 60)
    else:
        # Cookie de sessão: sem Expires/Max-Age. O JWT continua tendo seu prazo
        # normal de segurança, mas fechar o navegador encerra a persistência.
        _cookie_base(
            response,
            create_access_token(user.email, scope="app", session_id=session_id),
            max_age=None,
        )
    return {"authenticated": True, "persistent": permanecer_conectado}


@router.post("/sair")
def sair(request: Request, response: Response, db: Session = Depends(get_db)) -> dict[str, bool]:
    token = request.cookies.get(AUTH_COOKIE_NAME)
    session_id = session_id_from_token(token, "app")
    if session_id:
        user = db.query(User).filter(User.active_session_id == session_id).first()
        if user:
            from app.services.access_security import end_session
            end_session(
                db, user_id=user.id, surface="corvia_os",
                session_id=session_id, reason="logout",
            )
            user.active_session_id = None
            db.commit()
    limpar_cookie_sessao(response)
    return {"authenticated": False}
