"""Operações explícitas de bootstrap administrativo.

Este módulo não altera schema, extensões, triggers ou índices. Essas mudanças
pertencem ao fluxo Alembic. A criação do primeiro administrador também não roda
no startup da API: deve ser chamada conscientemente pelo operador.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User


def create_admin_if_absent(
    db: Session,
    *,
    email: str,
    password: str,
    full_name: str = "Administrador",
) -> tuple[User, bool]:
    """Cria um administrador apenas quando o e-mail ainda não existe.

    Retorna ``(usuario, criado)``. A operação é idempotente e nunca redefine a
    senha de uma conta existente silenciosamente.
    """
    normalized_email = email.strip().lower()
    normalized_name = full_name.strip() or "Administrador"

    if not normalized_email:
        raise ValueError("E-mail do administrador não pode ser vazio.")
    if not password:
        raise ValueError("Senha do administrador não pode ser vazia.")

    existing = (
        db.query(User)
        .filter(func.lower(User.email) == normalized_email)
        .first()
    )
    if existing is not None:
        return existing, False

    user = User(
        email=normalized_email,
        full_name=normalized_name,
        role="admin",
        password_hash=hash_password(password),
        is_active=True,
        status="aprovado",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, True
