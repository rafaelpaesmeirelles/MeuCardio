"""Conta de médico convidado — acesso cortesia completo (08/08/2026).

Pedido do Rafael: um amigo médico que vai trabalhar com a Corvia precisa
passar pelo fluxo REAL de cadastro (autocadastro, envio de documento/selfie
para o KYC, tela de pagamento), mas sem cobrança e com aprovação automática
do KYC — porque a checagem automática do CFM ainda não está disponível
(pendência registrada em CLAUDE.md), e para este caso específico a revisão
manual é dispensada por decisão direta do Rafael, não por falha do sistema.

`convidado` é um flag reutilizável, ligado/desligado só por admin
(`PATCH /api/admin/users/{id}/convidado`) — não um caso hardcoded de um
único e-mail. Nasce `false`: por padrão nenhuma conta pula pagamento ou
revisão de identidade.

Revision ID: f66h20260808
Revises: f65g20260807
Create Date: 2026-08-08
"""

from alembic import op
import sqlalchemy as sa

revision = "f66h20260808"
down_revision = "f65g20260807"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("convidado", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("users", "convidado")
