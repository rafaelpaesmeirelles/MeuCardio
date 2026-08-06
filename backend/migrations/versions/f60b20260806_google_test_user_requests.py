"""Fila de liberação manual de testador do Google (app OAuth em modo
"Testing", teto de 100 contas, sem API pra automatizar — ver docstring de
GoogleTestUserRequest em app/models/agenda.py).

Revision ID: f60b20260806
Revises: f53a20260806
Create Date: 2026-08-06
"""

from alembic import op
import sqlalchemy as sa

revision = "f60b20260806"
down_revision = "f53a20260806"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "google_test_user_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("google_email", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pendente"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("liberado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("liberado_por", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notificado_em", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_google_test_user_requests_user_id", "google_test_user_requests", ["user_id"])
    op.create_index("ix_google_test_user_requests_status", "google_test_user_requests", ["status"])


def downgrade() -> None:
    op.drop_index("ix_google_test_user_requests_status", table_name="google_test_user_requests")
    op.drop_index("ix_google_test_user_requests_user_id", table_name="google_test_user_requests")
    op.drop_table("google_test_user_requests")
