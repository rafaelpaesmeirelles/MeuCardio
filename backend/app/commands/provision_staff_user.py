"""Provisiona uma conta interna sem registrar senha no repositório ou logs."""
from __future__ import annotations

import argparse
import getpass
import os

from sqlalchemy import func

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Cria conta interna aprovada e ativa.")
    p.add_argument("--email", required=True)
    p.add_argument("--name", default="Usuário a completar cadastro")
    p.add_argument("--role", choices=("admin", "medico", "residente", "leitor"), default="admin")
    p.add_argument("--require-profile-completion", action="store_true")
    return p


def main() -> None:
    args = parser().parse_args()
    email = args.email.strip().lower()
    password = os.getenv("PROVISION_USER_PASSWORD") or getpass.getpass("Senha inicial: ")
    if len(password) < 8:
        raise SystemExit("A senha precisa ter ao menos 8 caracteres.")

    db = SessionLocal()
    try:
        existing = db.query(User).filter(func.lower(User.email) == email).first()
        if existing:
            raise SystemExit(f"Conta já existente: {email}. Nenhuma alteração foi feita.")
        user = User(
            email=email,
            full_name=args.name.strip() or "Usuário a completar cadastro",
            role=args.role,
            password_hash=hash_password(password),
            is_active=True,
            status="aprovado",
            profile_completion_required=args.require_profile_completion,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Conta criada: id={user.id} email={user.email} role={user.role}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
