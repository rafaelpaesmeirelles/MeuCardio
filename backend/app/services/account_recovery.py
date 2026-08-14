"""Recuperação de acesso por um segundo endereço independente do CorVIA Mail.

O login do médico pode ser uma caixa ``@corvia.med.br``. Essa caixa depende do
próprio Clinical OS e, portanto, não pode ser o único canal para recuperar uma
conta bloqueada. Este módulo mantém o segundo canal separado e nunca envia
senha em texto: somente links de uso único.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.account_recovery import AccountRecoveryEmail
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.services import emails

PRAZO_RECUPERACAO_HORAS = 1
PRAZO_PRIMEIRO_ACESSO_HORAS = 48


def normalizar_email(value: str) -> str:
    return (value or "").strip().lower()


def validar_email_basico(value: str) -> str:
    value = normalizar_email(value)
    if not value or "@" not in value or value.startswith("@") or value.endswith("@"):
        raise ValueError("E-mail de recuperação inválido.")
    return value


def email_ja_em_uso(db, email: str, *, ignorar_user_id: int | None = None) -> bool:
    """Evita ambiguidade entre login e segundo canal.

    Um endereço não pode ser login de uma conta e recuperação de outra, nem
    recuperação de duas contas. Isso permite procurar por qualquer dos dois
    sem revelar ou redefinir a conta errada.
    """
    email = normalizar_email(email)
    q_user = db.query(User).filter(User.email == email)
    if ignorar_user_id is not None:
        q_user = q_user.filter(User.id != ignorar_user_id)
    if q_user.first() is not None:
        return True

    q_recovery = db.query(AccountRecoveryEmail).filter(AccountRecoveryEmail.email == email)
    if ignorar_user_id is not None:
        q_recovery = q_recovery.filter(AccountRecoveryEmail.user_id != ignorar_user_id)
    return q_recovery.first() is not None


def definir_email_recuperacao(db, user: User, recovery_email: str) -> AccountRecoveryEmail:
    recovery_email = validar_email_basico(recovery_email)
    if recovery_email == normalizar_email(user.email):
        raise ValueError("O e-mail de recuperação precisa ser diferente do e-mail de login.")
    if email_ja_em_uso(db, recovery_email, ignorar_user_id=user.id):
        raise ValueError("Este e-mail já está vinculado a outra conta CorVIA.")

    registro = db.get(AccountRecoveryEmail, user.id)
    if registro is None:
        registro = AccountRecoveryEmail(user_id=user.id, email=recovery_email)
        db.add(registro)
    else:
        registro.email = recovery_email
        registro.updated_at = datetime.now(timezone.utc)
    db.flush()
    return registro


def obter_email_recuperacao(db, user_id: int) -> str | None:
    registro = db.get(AccountRecoveryEmail, user_id)
    return registro.email if registro else None


def encontrar_usuario_por_identificador(db, identificador: str) -> User | None:
    """Aceita login OU segundo e-mail, sem transformar o segundo em login."""
    identificador = normalizar_email(identificador)
    user = db.query(User).filter(User.email == identificador, User.is_active.is_(True)).first()
    if user is not None:
        return user
    registro = (
        db.query(AccountRecoveryEmail)
        .filter(AccountRecoveryEmail.email == identificador)
        .first()
    )
    if registro is None:
        return None
    return db.query(User).filter(User.id == registro.user_id, User.is_active.is_(True)).first()


def destinatario_seguro(db, user: User) -> str:
    """Segundo canal primeiro; fallback preserva contas legadas."""
    return obter_email_recuperacao(db, user.id) or user.email


def _novo_token(db, user_id: int, *, horas: int) -> PasswordResetToken:
    token = PasswordResetToken(
        user_id=user_id,
        alvo="conta",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=horas),
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def enviar_recuperacao_senha(user_id: int) -> bool:
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if user is None or not user.is_active:
            return False
        token = _novo_token(db, user.id, horas=PRAZO_RECUPERACAO_HORAS)
        destino = destinatario_seguro(db, user)
        return emails._enviar(
            db,
            tipo="recuperar_senha",
            destinatario=destino,
            assunto="CorVIA — redefinição de senha",
            template="recuperar_senha",
            contexto={"link": f"{settings.public_url}/redefinir-senha?token={token.token}"},
            user_id=user.id,
        )
    finally:
        db.close()


def enviar_confirmacao_canal_recuperacao(user_id: int) -> bool:
    """Confirma no canal externo qual é o login, sem jamais mandar senha."""
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if user is None:
            return False
        destino = obter_email_recuperacao(db, user.id)
        if not destino:
            return False
        return emails._enviar(
            db,
            tipo="canal_recuperacao_confirmado",
            destinatario=destino,
            assunto="CorVIA — e-mail de recuperação confirmado",
            template="canal_recuperacao_confirmado",
            contexto={
                "nome": user.full_name,
                "email_login": user.email,
                "link_login": f"{settings.public_url}/entrar",
            },
            user_id=user.id,
            chave_idempotencia=f"canal_recuperacao_confirmado:{user.id}:{destino}",
        )
    finally:
        db.close()


def enviar_primeiro_acesso(user_id: int) -> bool:
    """Convite seguro para conta criada pelo Admin.

    O destinatário recebe o identificador de login e um link de uso único para
    escolher sua própria senha. A senha temporária definida no painel nunca é
    transmitida por e-mail.
    """
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if user is None:
            return False
        destino = destinatario_seguro(db, user)
        token = _novo_token(db, user.id, horas=PRAZO_PRIMEIRO_ACESSO_HORAS)
        return emails._enviar(
            db,
            tipo="primeiro_acesso",
            destinatario=destino,
            assunto="Bem-vindo ao CorVIA — configure seu acesso",
            template="primeiro_acesso",
            contexto={
                "nome": user.full_name,
                "email_login": user.email,
                "link": f"{settings.public_url}/redefinir-senha?token={token.token}",
            },
            user_id=user.id,
        )
    finally:
        db.close()


def enviar_acesso_aprovado(user_id: int) -> bool:
    """Avisa quem se autocadastrou que o acesso foi liberado.

    A pessoa já escolheu a própria senha no cadastro; portanto não criamos nem
    transmitimos outra credencial. Informamos o login e o botão de acesso no
    segundo canal externo sempre que disponível.
    """
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if user is None or not user.is_active or user.status != "aprovado":
            return False
        destino = destinatario_seguro(db, user)
        return emails._enviar(
            db,
            tipo="acesso_aprovado",
            destinatario=destino,
            assunto="CorVIA — seu acesso está liberado",
            template="acesso_aprovado",
            contexto={
                "nome": user.full_name,
                "email_login": user.email,
                "link_login": f"{settings.public_url}/entrar",
            },
            user_id=user.id,
            chave_idempotencia=f"acesso_aprovado:{user.id}",
        )
    finally:
        db.close()


def enviar_teste_transacional(destinatario: str, admin_user_id: int | None = None) -> bool:
    """Smoke real do SMTP usado pelo release gate; não inclui segredo/token."""
    destinatario = validar_email_basico(destinatario)
    db = SessionLocal()
    try:
        return emails._enviar(
            db,
            tipo="smtp_probe",
            destinatario=destinatario,
            assunto="CorVIA — teste do canal transacional",
            template="smtp_probe",
            contexto={
                "remetente": "contato@corvia.med.br",
                "data_hora": datetime.now(timezone.utc).isoformat(),
            },
            user_id=admin_user_id,
        )
    finally:
        db.close()
