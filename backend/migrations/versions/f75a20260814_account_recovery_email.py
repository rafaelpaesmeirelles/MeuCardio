"""E-mail secundário de recuperação de acesso.

Revision ID: f75a20260814
Revises: f73s20260814
Create Date: 2026-08-14
"""

from alembic import op
import sqlalchemy as sa

revision = "f75a20260814"
down_revision = "f73s20260814"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "account_recovery_emails",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email", name="uq_account_recovery_emails_email"),
    )
    op.create_index(
        "ix_account_recovery_emails_email", "account_recovery_emails", ["email"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_account_recovery_emails_email", table_name="account_recovery_emails")
    op.drop_table("account_recovery_emails")
