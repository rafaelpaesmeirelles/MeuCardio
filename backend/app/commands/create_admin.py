"""Cria explicitamente o primeiro administrador da plataforma."""

import argparse

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.runtime import validar_configuracao_de_execucao
from app.services.bootstrap import create_admin_if_absent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cria o administrador inicial sem alterar contas existentes.",
    )
    parser.add_argument("--email", default=settings.admin_email)
    parser.add_argument("--password", default=settings.admin_password)
    parser.add_argument("--name", default="Administrador")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    validar_configuracao_de_execucao(settings)

    db = SessionLocal()
    try:
        user, created = create_admin_if_absent(
            db,
            email=args.email,
            password=args.password,
            full_name=args.name,
        )
    finally:
        db.close()

    if created:
        print(f"Administrador criado: {user.email}")
    else:
        print(f"Administrador já existente: {user.email}")


if __name__ == "__main__":
    main()
