"""add request id to audit logs

Revision ID: f7d2b9c4a601
Revises: e6c1a8d4f209
Create Date: 2026-08-03
"""

from alembic import op
import sqlalchemy as sa

revision = "f7d2b9c4a601"
down_revision = "e6c1a8d4f209"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "audit_logs",
        sa.Column("request_id", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_audit_logs_request_id",
        "audit_logs",
        ["request_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_audit_logs_request_id", table_name="audit_logs")
    op.drop_column("audit_logs", "request_id")
