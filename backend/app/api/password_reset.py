from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, field_validator, model_validator
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user, hash_password, require_admin, verify_password
from app.models.account_recovery import AccountRecoveryEmail
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.services import account_recovery, emails

router = APIRouter(prefix="/api/auth", tags=["auth"])


class SolicitacaoReset(BaseModel):
    # Pode ser o e-mail de login OU o segundo e-mail de recuperação. O nome do
    # campo fica "email" por compatibilidade com o frontend e clientes antigos.
    email: str


@router.post("/esqueci-senha", status_code=202)
def esqueci_senha(dados: SolicitacaoReset, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Sempre responde 202, exista ou não o endereço — evita enumeração.

    A busca aceita o login e o segundo canal externo. Quando a conta tem um
    e-mail de recuperação cadastrado, o link é SEMPRE entregue nele; isso
    evita o ciclo em que a pessoa perde o Clinical OS e, junto, perde também
    a caixa ``@corvia.med.br`` usada como login.
    """
    user = account_recovery.encontrar_usuario_por_identificador(db, dados.email)
    if user:
        background_tasks.add_task(account_recovery.enviar_recuperacao_senha, user.id)
    return {
        "nota": "Se o endereço estiver vinculado a uma conta ativa, enviaremos um link de redefinição ao canal seguro cadastrado."
    }


@router.post("/reenviar-ativacao", status_code=202)
def reenviar_ativacao(dados: SolicitacaoReset, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Item 2 do spec de e-mails transacionais — padrão anti-enumeração."""
    email = dados.email.strip().lower()
    user = db.query(User).filter(User.email == email, User.is_active.is_(False)).first()
    if user:
        background_tasks.add_task(emails.enviar_reenvio_ativacao, user.id)
    return {"nota": "Se houver uma conta pendente de ativação com este e-mail, um novo link foi enviado."}


class EmailRecuperacaoPayload(BaseModel):
    recovery_email: str

    @field_validator("recovery_email")
    @classmethod
    def _email(cls, value: str) -> str:
        try:
            return account_recovery.validar_email_basico(value)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc


class EmailRecuperacaoDoTitular(EmailRecuperacaoPayload):
    senha_atual: str


@router.get("/email-recuperacao")
def obter_email_recuperacao(
    db: Session = Depends(get_db), user: User = Depends(current_user),
):
    return {"recovery_email": account_recovery.obter_email_recuperacao(db, user.id)}


@router.put("/email-recuperacao")
def atualizar_email_recuperacao(
    dados: EmailRecuperacaoDoTitular,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    """Troca sensível: exige a senha atual e confirma no novo canal."""
    if not verify_password(dados.senha_atual, user.password_hash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta.")
    try:
        registro = account_recovery.definir_email_recuperacao(db, user, dados.recovery_email)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    background_tasks.add_task(account_recovery.enviar_confirmacao_canal_recuperacao, user.id)
    return {"recovery_email": registro.email}


@router.put("/admin/users/{user_id}/email-recuperacao")
def admin_atualizar_email_recuperacao(
    user_id: int,
    dados: EmailRecuperacaoPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Permite recuperar uma conta já bloqueada sem pedir que o titular entre."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    try:
        registro = account_recovery.definir_email_recuperacao(db, user, dados.recovery_email)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    background_tasks.add_task(account_recovery.enviar_confirmacao_canal_recuperacao, user.id)
    return {"user_id": user.id, "recovery_email": registro.email}


# -------------------------------------------------------------------------
# Cadastro novo com segundo canal obrigatório. Mantemos a rota histórica
# intacta por compatibilidade interna, mas toda interface CorVIA passa a usar
# esta versão. Ela reutiliza a regra canônica de cadastro em auth.py e apenas
# adiciona, na mesma requisição, o canal externo independente.
# -------------------------------------------------------------------------

from app.api.auth import SolicitacaoAcesso, solicitar_acesso  # noqa: E402


class SolicitacaoAcessoComRecuperacao(SolicitacaoAcesso):
    recovery_email: str

    @field_validator("recovery_email")
    @classmethod
    def _recovery(cls, value: str) -> str:
        try:
            return account_recovery.validar_email_basico(value)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

    @model_validator(mode="after")
    def _diferente_do_login(self):
        if self.recovery_email == self.email.strip().lower():
            raise ValueError("O e-mail de recuperação precisa ser diferente do e-mail de login.")
        return self


@router.post("/solicitar-acesso-com-recuperacao", status_code=201)
def solicitar_acesso_com_recuperacao(
    dados: SolicitacaoAcessoComRecuperacao,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    recovery_email = account_recovery.normalizar_email(dados.recovery_email)
    if account_recovery.email_ja_em_uso(db, recovery_email):
        raise HTTPException(status_code=409, detail="Este e-mail de recuperação já está vinculado a uma conta CorVIA.")

    base = SolicitacaoAcesso(**dados.model_dump(exclude={"recovery_email"}))
    resultado = solicitar_acesso(base, background_tasks, db)
    user = db.query(User).filter(User.email == base.email).first()
    if user is None:
        raise HTTPException(status_code=500, detail="Cadastro criado sem vínculo de recuperação. Operação abortada.")
    try:
        account_recovery.definir_email_recuperacao(db, user, recovery_email)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    background_tasks.add_task(account_recovery.enviar_confirmacao_canal_recuperacao, user.id)
    return resultado


# Rota segura para a criação pelo Admin. O endpoint legado /api/admin/users
# continua existindo para compatibilidade, mas a UI de criação deve usar esta
# variante porque ela exige o segundo canal e dispara o e-mail de primeiro
# acesso sem transmitir senha em texto.
from app.api.admin import NovoUsuario, criar_usuario  # noqa: E402


class NovoUsuarioComRecuperacao(NovoUsuario):
    recovery_email: str

    @field_validator("recovery_email")
    @classmethod
    def _admin_recovery(cls, value: str) -> str:
        try:
            return account_recovery.validar_email_basico(value)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

    @model_validator(mode="after")
    def _admin_diferente_do_login(self):
        if self.recovery_email == self.email.strip().lower():
            raise ValueError("O e-mail de recuperação precisa ser diferente do e-mail de login.")
        return self


@router.post("/admin/criar-usuario-com-recuperacao", status_code=201)
def admin_criar_usuario_com_recuperacao(
    dados: NovoUsuarioComRecuperacao,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    recovery_email = account_recovery.normalizar_email(dados.recovery_email)
    if account_recovery.email_ja_em_uso(db, recovery_email):
        raise HTTPException(status_code=409, detail="Este e-mail de recuperação já está vinculado a uma conta CorVIA.")

    base = NovoUsuario(**dados.model_dump(exclude={"recovery_email"}))
    resultado = criar_usuario(base, db, admin)
    user = db.get(User, resultado["id"])
    if user is None:
        raise HTTPException(status_code=500, detail="Usuário criado sem vínculo de recuperação. Operação abortada.")
    try:
        account_recovery.definir_email_recuperacao(db, user, recovery_email)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    background_tasks.add_task(account_recovery.enviar_primeiro_acesso, user.id)
    return {**resultado, "recovery_email": recovery_email}


class RedefinirSenha(BaseModel):
    token: str
    nova_senha: str


@router.post("/redefinir-senha")
def redefinir_senha(dados: RedefinirSenha, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """`registro.alvo` decide QUAL senha muda: conta, e-mail ou ativação."""
    if len(dados.nova_senha) < 8:
        raise HTTPException(status_code=422, detail="A senha precisa ter ao menos 8 caracteres.")
    registro = db.query(PasswordResetToken).filter(PasswordResetToken.token == dados.token).first()
    if not registro or not registro.valido:
        raise HTTPException(status_code=400, detail="Link inválido ou expirado. Solicite um novo.")

    if registro.alvo == "email":
        from app.models.email_account import EmailAccount

        conta = db.query(EmailAccount).filter(EmailAccount.user_id == registro.user_id).first()
        if not conta:
            raise HTTPException(status_code=400, detail="Link inválido.")
        conta.password_hash = hash_password(dados.nova_senha)
    else:
        user = db.get(User, registro.user_id)
        if not user:
            raise HTTPException(status_code=400, detail="Link inválido.")
        user.password_hash = hash_password(dados.nova_senha)
        if registro.alvo == "ativacao":
            user.is_active = True
        else:
            background_tasks.add_task(emails.enviar_senha_alterada, user.id)

    registro.used = True
    db.commit()
    return {"nota": "Senha redefinida. Você já pode entrar com a nova senha."}


@router.get("/reset-pendentes")
def listar_resets_pendentes(db: Session = Depends(get_db), admin: User = Depends(current_user)):
    """Painel de apoio pro admin; nunca expõe senha ou hash."""
    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Só administradores.")
    agora = datetime.now(timezone.utc)
    pendentes = (
        db.query(PasswordResetToken, User)
        .join(User, User.id == PasswordResetToken.user_id)
        .filter(PasswordResetToken.used.is_(False), PasswordResetToken.expires_at > agora)
        .order_by(PasswordResetToken.created_at.desc())
        .all()
    )
    return [
        {
            "email": u.email, "full_name": u.full_name, "alvo": t.alvo,
            "link": f"/redefinir-senha?token={t.token}" + ("&alvo=email" if t.alvo == "email" else ""),
            "expira_em": t.expires_at, "solicitado_em": t.created_at,
        }
        for t, u in pendentes
    ]
