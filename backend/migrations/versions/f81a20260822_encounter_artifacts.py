"""Vincular prescrições e documentos ao Encounter sem duplicar seus modelos.

Revision ID: f81a20260822
Revises: f80a20260822
Create Date: 2026-08-22
"""
from alembic import op
import sqlalchemy as sa

revision = "f81a20260822"
down_revision = "f80a20260822"
branch_labels = None
depends_on = None

_TABLE = "encounter_artifacts"


def upgrade() -> None:
    bind = op.get_bind()
    if _TABLE in sa.inspect(bind).get_table_names():
        return
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("encounter_id", sa.Integer(), nullable=False),
        sa.Column("artifact_type", sa.String(length=20), nullable=False),
        sa.Column("artifact_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["encounter_id"], ["clinical_encounters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "owner_id", "artifact_type", "artifact_id",
            name="uq_encounter_artifact_owner_type_id",
        ),
    )
    op.create_index("ix_encounter_artifacts_owner_id", _TABLE, ["owner_id"], unique=False)
    op.create_index("ix_encounter_artifacts_encounter_id", _TABLE, ["encounter_id"], unique=False)
    op.create_index("ix_encounter_artifacts_artifact_type", _TABLE, ["artifact_type"], unique=False)
    op.create_index("ix_encounter_artifacts_artifact_id", _TABLE, ["artifact_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    if _TABLE in sa.inspect(bind).get_table_names():
        op.drop_table(_TABLE)
