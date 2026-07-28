from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user, hash_password
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.services.notificar import tentar_enviar_email

router = APIRouter(prefix="/api/auth", tags=["auth"])


class SolicitacaoReset(BaseModel):
    email: str


@router.post("/esqueci-senha", status_code=202)
def esqueci_senha(dados: SolicitacaoReset, db: Session = Depends(get_db)):
    """Sempre responde 202, exista ou não o e-mail — não confirma pra quem
    pergunta se um e-mail está cadastrado (evita enumeração de usuários)."""
    email = dados.email.strip().lower()
    user = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()
    if user:
        token = PasswordResetToken(user_id=user.id)
        db.add(token)
        db.commit()
        link = f"/redefinir-senha?token={token.token}"
        enviado = tentar_enviar_email(
            destinatario=user.email,
            assunto="Corvia — redefinição de senha",
            corpo=f"Use este link para redefinir sua senha (válido por 2 horas): {{DOMINIO}}{link}",
        )
        if not enviado:
            # sem SMTP configurado: registra pra um admin conseguir ver e repassar manualmente
            pass
    return {"nota": "Se o e-mail existir e estiver ativo, um link de redefinição foi gerado."}


class RedefinirSenha(BaseModel):
    token: str
    nova_senha: str


@router.post("/redefinir-senha")
def redefinir_senha(dados: RedefinirSenha, db: Session = Depends(get_db)):
    if len(dados.nova_senha) < 8:
        raise HTTPException(status_code=422, detail="A senha precisa ter ao menos 8 caracteres.")
    registro = db.query(PasswordResetToken).filter(PasswordResetToken.token == dados.token).first()
    if not registro or not registro.valido:
        raise HTTPException(status_code=400, detail="Link inválido ou expirado. Solicite um novo.")
    user = db.get(User, registro.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="Link inválido.")
    user.password_hash = hash_password(dados.nova_senha)
    registro.used = True
    db.commit()
    return {"nota": "Senha redefinida. Você já pode entrar com a nova senha."}


@router.get("/reset-pendentes")
def listar_resets_pendentes(db: Session = Depends(get_db), admin: User = Depends(current_user)):
    """Painel de apoio pro admin: enquanto não há SMTP configurado, os links
    de reset ficam visíveis aqui pra repasse manual (WhatsApp, telefone etc.)."""
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
            "email": u.email, "full_name": u.full_name,
            "link": f"/redefinir-senha?token={t.token}",
            "expira_em": t.expires_at, "solicitado_em": t.created_at,
        }
        for t, u in pendentes
    ]
