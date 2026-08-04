"""PR47: conteúdo científico, presença, diretrizes e arquivamento do round.

Revision ID: e47c20260804
Revises: d63a0cc83807
Create Date: 2026-08-04
"""
from alembic import op
import sqlalchemy as sa

revision = "e47c20260804"
down_revision = "d63a0cc83807"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("evidence_records", sa.Column("summary", sa.Text(), nullable=True))
    op.add_column("evidence_records", sa.Column("source_url", sa.String(length=1000), nullable=True))
    op.add_column("evidence_records", sa.Column("doi", sa.String(length=160), nullable=True))

    op.add_column("drugs", sa.Column("duration_of_action_hours", sa.Float(), nullable=True))
    op.add_column("drugs", sa.Column("duration_of_action_note", sa.Text(), nullable=True))
    op.add_column("drugs", sa.Column("duration_of_action_source", sa.String(length=500), nullable=True))

    op.add_column(
        "discharge_checklists",
        sa.Column("scope_type", sa.String(length=20), nullable=False, server_default="doenca"),
    )
    op.create_index(
        "ix_discharge_checklists_scope_type",
        "discharge_checklists",
        ["scope_type"],
        unique=False,
    )

    op.add_column("guidelines", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "guidelines",
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.add_column("guidelines", sa.Column("source_fingerprint", sa.String(length=64), nullable=True))
    op.add_column(
        "guidelines",
        sa.Column("detection_status", sa.String(length=30), nullable=False, server_default="manual"),
    )
    op.create_index(
        "ix_guidelines_source_fingerprint",
        "guidelines",
        ["source_fingerprint"],
        unique=True,
    )
    op.create_index("ix_guidelines_published_at", "guidelines", ["published_at"], unique=False)

    op.create_table(
        "guideline_notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("guideline_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pendente"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["guideline_id"], ["guidelines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("guideline_id", "user_id", "channel", name="uq_guideline_notification_delivery"),
    )
    op.create_index(
        "ix_guideline_notifications_user_status",
        "guideline_notifications",
        ["user_id", "status"],
        unique=False,
    )

    op.add_column(
        "users",
        sa.Column("show_online_status", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.add_column("patients", sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("patients", sa.Column("archived_by", sa.Integer(), nullable=True))
    op.add_column("patients", sa.Column("archive_reason", sa.String(length=300), nullable=True))
    op.create_foreign_key(
        "fk_patients_archived_by_users",
        "patients",
        "users",
        ["archived_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_patients_archived_at", "patients", ["archived_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_patients_archived_at", table_name="patients")
    op.drop_constraint("fk_patients_archived_by_users", "patients", type_="foreignkey")
    op.drop_column("patients", "archive_reason")
    op.drop_column("patients", "archived_by")
    op.drop_column("patients", "archived_at")

    op.drop_column("users", "show_online_status")

    op.drop_index("ix_guideline_notifications_user_status", table_name="guideline_notifications")
    op.drop_table("guideline_notifications")

    op.drop_index("ix_guidelines_published_at", table_name="guidelines")
    op.drop_index("ix_guidelines_source_fingerprint", table_name="guidelines")
    op.drop_column("guidelines", "detection_status")
    op.drop_column("guidelines", "source_fingerprint")
    op.drop_column("guidelines", "discovered_at")
    op.drop_column("guidelines", "published_at")

    op.drop_index("ix_discharge_checklists_scope_type", table_name="discharge_checklists")
    op.drop_column("discharge_checklists", "scope_type")

    op.drop_column("drugs", "duration_of_action_source")
    op.drop_column("drugs", "duration_of_action_note")
    op.drop_column("drugs", "duration_of_action_hours")

    op.drop_column("evidence_records", "doi")
    op.drop_column("evidence_records", "source_url")
    op.drop_column("evidence_records", "summary")
