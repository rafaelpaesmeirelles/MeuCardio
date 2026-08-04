#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    content = read(path)
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: esperado 1 trecho, encontrado {count}: {old[:80]!r}")
    write(path, content.replace(old, new, 1))


# Banco/modelo: flag explícita, default falso para não afetar usuários atuais.
replace_once(
    "backend/migrations/versions/f91c2b7e4a60_perfil_profissional_e_nome_documento.py",
    '''    op.alter_column("users", "include_workplace_on_documents", server_default=None)
    op.add_column("generated_documents", sa.Column("patient_name_cifrado", sa.LargeBinary(), nullable=True))
''',
    '''    op.alter_column("users", "include_workplace_on_documents", server_default=None)
    op.add_column(
        "users",
        sa.Column("profile_completion_required", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("users", "profile_completion_required", server_default=None)
    op.add_column("generated_documents", sa.Column("patient_name_cifrado", sa.LargeBinary(), nullable=True))
''',
)
replace_once(
    "backend/migrations/versions/f91c2b7e4a60_perfil_profissional_e_nome_documento.py",
    '''def downgrade() -> None:
    op.drop_column("generated_documents", "patient_name_cifrado")
''',
    '''def downgrade() -> None:
    op.drop_column("generated_documents", "patient_name_cifrado")
    op.drop_column("users", "profile_completion_required")
''',
)
replace_once(
    "backend/app/models/user.py",
    '    include_workplace_on_documents: Mapped[bool] = mapped_column(Boolean, default=False)\n',
    '    include_workplace_on_documents: Mapped[bool] = mapped_column(Boolean, default=False)\n'
    '    profile_completion_required: Mapped[bool] = mapped_column(Boolean, default=False)\n',
)
replace_once(
    "backend/app/services/professional_profile.py",
    '        "include_workplace_on_documents": user.include_workplace_on_documents,\n',
    '        "include_workplace_on_documents": user.include_workplace_on_documents,\n'
    '        "profile_completion_required": user.profile_completion_required,\n',
)
replace_once(
    "backend/app/api/auth.py",
    '    user.include_workplace_on_documents = dados.include_workplace_on_documents\n\n',
    '    user.include_workplace_on_documents = dados.include_workplace_on_documents\n'
    '    user.profile_completion_required = False\n\n',
)

# Admin: permite marcar a conta criada diretamente para completar perfil.
replace_once(
    "backend/app/api/admin.py",
    '    include_workplace_on_documents: bool = False\n    role: str = "medico"',
    '    include_workplace_on_documents: bool = False\n'
    '    profile_completion_required: bool = False\n'
    '    role: str = "medico"',
)
replace_once(
    "backend/app/api/admin.py",
    '        include_workplace_on_documents=dados.include_workplace_on_documents,\n        role=dados.role,',
    '        include_workplace_on_documents=dados.include_workplace_on_documents,\n'
    '        profile_completion_required=dados.profile_completion_required,\n'
    '        role=dados.role,',
)
replace_once(
    "backend/app/api/admin.py",
    '        "include_workplace_on_documents": u.include_workplace_on_documents,\n',
    '        "include_workplace_on_documents": u.include_workplace_on_documents,\n'
    '        "profile_completion_required": u.profile_completion_required,\n',
)

# Frontend: bloqueia a navegação até a usuária salvar o perfil.
replace_once(
    "frontend/src/lib/api.ts",
    '  include_workplace_on_documents: boolean;\n',
    '  include_workplace_on_documents: boolean;\n'
    '  profile_completion_required: boolean;\n',
)
replace_once(
    "frontend/src/App.tsx",
    'import { Navigate, Route, Routes } from "react-router-dom";\n',
    'import { Navigate, Route, Routes, useLocation } from "react-router-dom";\n',
)
replace_once(
    "frontend/src/App.tsx",
    '  const { usuario, carregando } = useAuth();\n',
    '  const { usuario, carregando } = useAuth();\n  const location = useLocation();\n',
)
replace_once(
    "frontend/src/App.tsx",
    '''  return (
    <RotasSuspensas>
''',
    '''  if (usuario.profile_completion_required && location.pathname !== "/minha-conta") {
    return <Navigate to="/minha-conta" replace />;
  }

  return (
    <RotasSuspensas>
''',
)
replace_once(
    "frontend/src/pages/MinhaConta.tsx",
    '      <h1>Minha conta</h1>\n\n',
    '      <h1>Minha conta</h1>\n'
    '      {perfil.profile_completion_required && (\n'
    '        <div className="cartao" role="status" style={{ borderLeft: "4px solid var(--destaque)" }}>\n'
    '          <strong>Complete seus dados pessoais e profissionais para continuar.</strong>\n'
    '          <p style={{ marginBottom: 0 }}>A senha atual continuará válida; não é necessário alterá-la.</p>\n'
    '        </div>\n'
    '      )}\n\n',
)

# Comando genérico e seguro: senha via variável de ambiente ou prompt oculto.
write("backend/app/commands/provision_staff_user.py", '''"""Provisiona uma conta interna sem registrar senha no repositório ou logs."""
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
''')

write("backend/tests/test_profile_completion.py", '''from app.models.user import User
from app.services.professional_profile import profile_payload


def test_profile_payload_expõe_bloqueio_de_complementação():
    user = User(
        email="nova@teste.local", full_name="Nova Usuária", password_hash="x",
        profile_completion_required=True,
    )
    user.professional_title = None
    user.workplace_name = None
    user.workplace_department = None
    user.workplace_role = None
    user.workplace_notes = None
    user.include_workplace_on_documents = False
    user.document_logo_url = None
    assert profile_payload(user)["profile_completion_required"] is True
''')

(ROOT / "tools/apply_onboarding_provision.py").unlink(missing_ok=True)
print("Onboarding e comando de provisionamento aplicados.")
