"""Opt-in independente para assinatura digital S/MIME de e-mail.

Revision ID: f76a20260819
Revises: f75a20260814
Create Date: 2026-08-19
"""

from alembic import op
import sqlalchemy as sa

revision = "f76a20260819"
down_revision = "f75a20260814"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "email_assinatura_digital_ativa",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    # Preserva o comportamento anterior: assinatura visual + A1 conectado
    # já tornava S/MIME obrigatório. Usuários nesse estado continuam com a
    # proteção ativa; os demais ganham o novo opt-in desligado.
    op.execute(
        sa.text(
            """
            UPDATE users AS u
               SET email_assinatura_digital_ativa = TRUE
             WHERE u.email_assinatura_ativa = TRUE
               AND EXISTS (
                   SELECT 1
                     FROM digital_certificates AS dc
                    WHERE dc.owner_id = u.id
               )
            """
        )
    )


def downgrade() -> None:
    op.drop_column("users", "email_assinatura_digital_ativa")
