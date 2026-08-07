"""Assistente Clínica × Assistente Pessoal (Trabalho 15, 07/08/2026).

`ai_conversations.modo` separa o histórico das duas — nunca mistura
pergunta de rotina/agenda com pesquisa de literatura no mesmo fio. Toda
conversa já existente é implicitamente "clinica" (era o único modo até
aqui).

Revision ID: f64f20260807
Revises: f63e20260806
Create Date: 2026-08-07
"""

from alembic import op
import sqlalchemy as sa

revision = "f64f20260807"
down_revision = "f63e20260806"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ai_conversations",
        sa.Column("modo", sa.String(20), nullable=False, server_default="clinica"),
    )
    op.create_index("ix_ai_conversations_modo", "ai_conversations", ["modo"])


def downgrade() -> None:
    op.drop_index("ix_ai_conversations_modo", table_name="ai_conversations")
    op.drop_column("ai_conversations", "modo")
