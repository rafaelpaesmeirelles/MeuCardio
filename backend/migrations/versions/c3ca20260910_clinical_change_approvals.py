"""Owner-reviewed clinical changes with exact immutable proposal snapshots."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = "c3ca20260910"
down_revision = "c2fv20260910"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("clinical_change_proposals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("guideline_id", sa.Integer(), sa.ForeignKey("guidelines.id"), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("rejection_reason", sa.String(2000), nullable=True),
        sa.UniqueConstraint("guideline_id", "fingerprint", name="uq_clinical_proposal_source_payload"),
        sa.CheckConstraint("status IN ('pending','approved','rejected')", name="ck_clinical_proposal_status"))
    op.create_index("ix_clinical_change_proposals_guideline_id", "clinical_change_proposals", ["guideline_id"])
    op.create_index("ix_clinical_change_proposals_status", "clinical_change_proposals", ["status"])

def downgrade():
    if op.get_bind().execute(sa.text("SELECT count(*) FROM clinical_change_proposals")).scalar():
        raise RuntimeError("Preserve o histórico de decisões clínicas antes de reverter a migração.")
    op.drop_table("clinical_change_proposals")
