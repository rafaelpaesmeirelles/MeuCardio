from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user, hash_password
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.services import emails

router = APIRouter(prefix="/api/auth", tags=["auth"])


class SolicitacaoReset(BaseModel):
    email: str


@router.post("/esqueci-senha", status_code=202)
def esqueci_senha(dados: SolicitacaoReset, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Sempre responde 202, exista ou não o e-mail — não confirma pra quem
    pergunta se um e-mail está cadastrado (evita enumeração de usuários).

    O e-mail em si (item 3 do spec de e-mails transacionais) sai em
    background: a resposta não espera o SMTP, e `emails.enviar_recuperar_senha`
    cria o próprio `PasswordResetToken` (validade de 1h) numa sessão de banco
    própria — não a `db` desta rota, que pode já estar liberada quando o
    background task rodar."""
    email = dados.email.strip().lower()
    user = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()
    if user:
        background_tasks.add_task(emails.enviar_recuperar_senha, user.id)
    return {"nota": "Se o e-mail existir e estiver ativo, um link de redefinição foi gerado."}


@router.post("/reenviar-ativacao", status_code=202)
def reenviar_ativacao(dados: SolicitacaoReset, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Item 2 do spec de e-mails transacionais — mesmo padrão anti-enumeração
    de `esqueci_senha`: responde 202 sempre. Só reenvia para conta que ainda
    não foi ativada (`is_active is False`); conta já ativa não tem link de
    ativação para reenviar."""
    email = dados.email.strip().lower()
    user = db.query(User).filter(User.email == email, User.is_active.is_(False)).first()
    if user:
        background_tasks.add_task(emails.enviar_reenvio_ativacao, user.id)
    return {"nota": "Se houver uma conta pendente de ativação com este e-mail, um novo link foi enviado."}


class RedefinirSenha(BaseModel):
    token: str
    nova_senha: str


@router.post("/redefinir-senha")
def redefinir_senha(dados: RedefinirSenha, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """`registro.alvo` decide QUAL senha muda: 'conta' é o comportamento
    original (senha da conta Corvia); 'email' é a senha própria da caixa
    de e-mail (Tarefa 28) — reaproveita o mesmo token e o mesmo formulário
    de redefinição em vez de duplicar a peça inteira. 'ativacao' (02/08/2026)
    é o link de boas-vindas: além de definir a senha, ativa a conta
    (`is_active = True`) — é o único momento em que uma conta criada via
    assinatura passa a poder logar."""
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
            # 'conta': troca genuína de senha de quem já podia logar —
            # dispara a confirmação de segurança (item 4 do spec). Uma
            # ativação de conta nova não manda essa confirmação: não é
            # "sua senha foi alterada", é a primeira senha sendo criada, e
            # o próprio e-mail de boas-vindas já cobre esse momento.
            background_tasks.add_task(emails.enviar_senha_alterada, user.id)

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
            "email": u.email, "full_name": u.full_name, "alvo": t.alvo,
            "link": f"/redefinir-senha?token={t.token}" + ("&alvo=email" if t.alvo == "email" else ""),
            "expira_em": t.expires_at, "solicitado_em": t.created_at,
        }
        for t, u in pendentes
    ]
