"""Resumo clínico longitudinal: problemas, alergias e medicações em uso.

Revision ID: f82a20260822
Revises: f81a20260822
Create Date: 2026-08-22
"""
from alembic import op
import sqlalchemy as sa

revision = "f82a20260822"
down_revision = "f81a20260822"
branch_labels = None
depends_on = None

_TABLE = "patient_clinical_items"


def upgrade() -> None:
    bind = op.get_bind()
    if _TABLE in sa.inspect(bind).get_table_names():
        return
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("patient_profile_id", sa.Integer(), nullable=False),
        sa.Column("source_encounter_id", sa.Integer(), nullable=True),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("payload_cifrado", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_profile_id"], ["patient_profiles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["source_encounter_id"], ["clinical_encounters.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_patient_clinical_items_owner_id", _TABLE, ["owner_id"], unique=False)
    op.create_index("ix_patient_clinical_items_patient_profile_id", _TABLE, ["patient_profile_id"], unique=False)
    op.create_index("ix_patient_clinical_items_source_encounter_id", _TABLE, ["source_encounter_id"], unique=False)
    op.create_index("ix_patient_clinical_items_kind", _TABLE, ["kind"], unique=False)
    op.create_index("ix_patient_clinical_items_is_active", _TABLE, ["is_active"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    if _TABLE in sa.inspect(bind).get_table_names():
        op.drop_table(_TABLE)
