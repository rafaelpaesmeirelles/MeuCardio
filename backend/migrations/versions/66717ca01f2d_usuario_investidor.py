"""Conta de investidor — acesso cortesia de demonstração (issue #52).

Frente de entitlement de convidados/investidores. Investigado antes de criar
esta coluna: não existe campo hoje que represente essa identidade sem
colisão semântica — `role="leitor"` é o papel padrão de cadastro PENDENTE
DE APROVAÇÃO (`app/api/auth.py::solicitar_acesso`), não um observador
aprovado; `profession`/`workplace_role`/`convidado_plano_preferido` já têm
outro significado. Decisão humana: campo novo, mesmo padrão exato de
`users.convidado` (migração f66h20260808) — booleano, `not null`,
`server_default=false`, ligado/desligado só por admin
(`PATCH /api/admin/users/{id}/investidor`).

Nasce `false`: por padrão nenhuma conta ganha acesso sem pagar. Investidor
nunca vira admin, nunca ganha acesso a dado de outro tenant — o flag só
alimenta `app/services/entitlement.py::tem_acesso_ao_produto()`, o mesmo
portão central que já decide acesso de assinante pago e de convidado.

Revision ID: 66717ca01f2d
Revises: 72abcfc8df81
Create Date: 2026-08-12
"""

from alembic import op
import sqlalchemy as sa

revision = "66717ca01f2d"
down_revision = "72abcfc8df81"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("investidor", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("users", "investidor")
