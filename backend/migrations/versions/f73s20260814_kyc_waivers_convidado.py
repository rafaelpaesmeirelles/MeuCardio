"""Dispensas KYC individuais para Convidado e selfie opcional no registro.

Revision ID: f73s20260814
Revises: f72r20260813
Create Date: 2026-08-14
"""

from alembic import op
import sqlalchemy as sa

revision = "f73s20260814"
down_revision = "f72r20260813"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "kyc_requirement_waivers",
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("professional_front", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("professional_back", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("personal_front", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("personal_back", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("personal_digital", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("selfie", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("owner_id"),
    )
    op.alter_column("kyc_verifications", "selfie", existing_type=sa.String(length=120), nullable=True)


def downgrade() -> None:
    # Mantém downgrade tecnicamente possível mesmo se uma submissão válida de
    # Convidado tiver dispensado selfie; string vazia é apenas sentinela de
    # rollback e não é criada no fluxo normal.
    op.execute("UPDATE kyc_verifications SET selfie = '' WHERE selfie IS NULL")
    op.alter_column("kyc_verifications", "selfie", existing_type=sa.String(length=120), nullable=False)
    op.drop_table("kyc_requirement_waivers")
