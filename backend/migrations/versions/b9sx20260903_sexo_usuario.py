"""Adiciona sexo cadastral ao perfil do usuário.

Revision ID: b9sx20260903
Revises: b8sk20260903
Create Date: 2026-09-03

O campo é nullable para não inventar sexo para contas legadas. Novos cadastros
passam a coletar o valor explicitamente; usuários antigos podem preenchê-lo em
Minha Conta. O valor canônico é "M" ou "F" e é usado para concordância de
tratamento nas superfícies personalizadas do Cardiology Spaces.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b9sx20260903"
down_revision = "b8sk20260903"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("sex", sa.String(length=1), nullable=True))
    op.create_check_constraint("ck_users_sex_mf", "users", "sex IS NULL OR sex IN ('M', 'F')")


def downgrade() -> None:
    op.drop_constraint("ck_users_sex_mf", "users", type_="check")
    op.drop_column("users", "sex")
