"""Sessao unica e auditoria privada de acessos.

Revision ID: f85b20260825
Revises: f84a20260822
Create Date: 2026-08-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "f85b20260825"
down_revision = "f84a20260822"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("active_session_id", sa.String(length=64), nullable=True))
    op.create_index("ix_users_active_session_id", "users", ["active_session_id"])
    op.add_column("email_accounts", sa.Column("active_session_id", sa.String(length=64), nullable=True))
    op.create_index("ix_email_accounts_active_session_id", "email_accounts", ["active_session_id"])
    op.create_table(
        "user_accesses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("surface", sa.String(length=20), nullable=False),
        sa.Column("successful", sa.Boolean(), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_reason", sa.String(length=30), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("region", sa.String(length=120), nullable=True),
        sa.Column("country_code", sa.String(length=8), nullable=True),
        sa.Column("operating_system", sa.String(length=80), nullable=True),
        sa.Column("browser", sa.String(length=80), nullable=True),
        sa.Column("device_type", sa.String(length=30), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("risk_level", sa.String(length=12), nullable=False),
        sa.Column("risk_reasons", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("user_id", "surface", "successful", "session_id", "started_at", "ip_address", "risk_level"):
        op.create_index(f"ix_user_accesses_{column}", "user_accesses", [column])


def downgrade() -> None:
    op.drop_table("user_accesses")
    op.drop_index("ix_email_accounts_active_session_id", table_name="email_accounts")
    op.drop_column("email_accounts", "active_session_id")
    op.drop_index("ix_users_active_session_id", table_name="users")
    op.drop_column("users", "active_session_id")
