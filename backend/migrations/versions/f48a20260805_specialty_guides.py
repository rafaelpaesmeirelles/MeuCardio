"""Cria guias especializados e triagem por sintomas.

Revision ID: f48a20260805
Revises: f47a20260804
Create Date: 2026-08-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "f48a20260805"
down_revision = "f47a20260804"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "specialty_diseases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=400), nullable=False),
        sa.Column("aliases", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("area", sa.String(length=60), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("subtype", sa.String(length=120), nullable=True),
        sa.Column("cyanosis_class", sa.String(length=20), nullable=True),
        sa.Column("prevalence_rank", sa.Integer(), nullable=False, server_default="999"),
        sa.Column("completeness", sa.String(length=20), nullable=False, server_default="basico"),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("epidemiology", sa.Text(), nullable=True),
        sa.Column("presentation", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("diagnostic_approach", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("differentials", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("tests", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("red_flags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("ambulatory_flow", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("emergency_flow", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("treatment_summary", sa.Text(), nullable=True),
        sa.Column("monitoring", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("special_populations", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("assistant_questions", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("assistant_rules", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("source_refs", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("source_urls", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("related_document_slugs", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("patient_material_slug", sa.String(length=255), nullable=True),
        sa.Column("review_status", sa.String(length=40), nullable=False, server_default="pendente_revisao"),
        sa.Column("review_note", sa.Text(), nullable=True),
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("reviewed_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("slug"),
    )
    for column in (
        "slug", "name", "area", "category", "subtype", "cyanosis_class",
        "prevalence_rank", "completeness", "review_status", "published",
    ):
        op.create_index(f"ix_specialty_diseases_{column}", "specialty_diseases", [column])

    op.create_table(
        "symptom_triage_guides",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("aliases", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("areas", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("questions", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("rules", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("default_tests", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("differentials", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("red_flags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("ambulatory_flow", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("emergency_flow", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("source_refs", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("source_urls", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("review_status", sa.String(length=40), nullable=False, server_default="pendente_revisao"),
        sa.Column("review_note", sa.Text(), nullable=True),
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("reviewed_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("slug"),
    )
    for column in ("slug", "name", "review_status", "published"):
        op.create_index(f"ix_symptom_triage_guides_{column}", "symptom_triage_guides", [column])


def downgrade() -> None:
    for column in ("slug", "name", "review_status", "published"):
        op.drop_index(f"ix_symptom_triage_guides_{column}", table_name="symptom_triage_guides")
    op.drop_table("symptom_triage_guides")

    for column in (
        "slug", "name", "area", "category", "subtype", "cyanosis_class",
        "prevalence_rank", "completeness", "review_status", "published",
    ):
        op.drop_index(f"ix_specialty_diseases_{column}", table_name="specialty_diseases")
    op.drop_table("specialty_diseases")
