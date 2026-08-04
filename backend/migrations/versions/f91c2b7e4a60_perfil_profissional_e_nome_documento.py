"""Perfil profissional ampliado e nome cifrado em documentos.

Revision ID: f91c2b7e4a60
Revises: d63a0cc83807
Create Date: 2026-08-04
"""
from alembic import op
import sqlalchemy as sa

revision = "f91c2b7e4a60"
down_revision = "d63a0cc83807"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("professional_title", sa.String(30), nullable=True))
    op.add_column("users", sa.Column("workplace_name", sa.String(180), nullable=True))
    op.add_column("users", sa.Column("workplace_department", sa.String(180), nullable=True))
    op.add_column("users", sa.Column("workplace_role", sa.String(180), nullable=True))
    op.add_column("users", sa.Column("workplace_notes", sa.String(500), nullable=True))
    op.add_column(
        "users",
        sa.Column("include_workplace_on_documents", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("users", "include_workplace_on_documents", server_default=None)
    op.add_column("generated_documents", sa.Column("patient_name_cifrado", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column("generated_documents", "patient_name_cifrado")
    op.drop_column("users", "include_workplace_on_documents")
    op.drop_column("users", "workplace_notes")
    op.drop_column("users", "workplace_role")
    op.drop_column("users", "workplace_department")
    op.drop_column("users", "workplace_name")
    op.drop_column("users", "professional_title")
