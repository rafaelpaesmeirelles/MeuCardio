"""Base oficial do CFM e auditoria de sincronização.

Revision ID: f95c20260902
Revises: f94a20260902
Create Date: 2026-09-02
"""
from alembic import op
import sqlalchemy as sa

revision = "f95c20260902"
down_revision = "f94a20260902"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cfm_sync_runs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("source_type", sa.String(length=24), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("dataset_sha256", sa.String(length=64), nullable=True),
        sa.Column("record_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("invalid_identifier_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("deactivated_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cfm_sync_runs_source_type", "cfm_sync_runs", ["source_type"])
    op.create_index("ix_cfm_sync_runs_status", "cfm_sync_runs", ["status"])
    op.create_index("ix_cfm_sync_runs_dataset_sha256", "cfm_sync_runs", ["dataset_sha256"])

    op.create_table(
        "cfm_physicians",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uf", sa.String(length=2), nullable=False),
        sa.Column("crm_raw", sa.String(length=64), nullable=False),
        sa.Column("crm_consulta", sa.String(length=7), nullable=True),
        sa.Column("crm_exibicao", sa.String(length=64), nullable=True),
        sa.Column("nome", sa.String(length=200), nullable=False),
        sa.Column("tipo_inscricao_texto", sa.String(length=120), nullable=False),
        sa.Column("tipo_inscricao_codigo", sa.String(length=8), nullable=True),
        sa.Column("situacao_texto", sa.String(length=160), nullable=False),
        sa.Column("situacao_codigo", sa.String(length=8), nullable=True),
        sa.Column("especialidades_raw", sa.Text(), nullable=False, server_default=""),
        sa.Column("data_atualizacao_cfm", sa.Date(), nullable=True),
        sa.Column("identificador_valido", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_regular", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("source_last", sa.String(length=24), nullable=False, server_default="totalzip"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_live_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_sync_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["last_seen_sync_id"], ["cfm_sync_runs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uf", "crm_raw", name="uq_cfm_physician_uf_crm_raw"),
    )
    op.create_index("ix_cfm_physicians_uf", "cfm_physicians", ["uf"])
    op.create_index("ix_cfm_physicians_crm_consulta", "cfm_physicians", ["crm_consulta"])
    op.create_index("ix_cfm_physicians_nome", "cfm_physicians", ["nome"])
    op.create_index("ix_cfm_physicians_situacao_codigo", "cfm_physicians", ["situacao_codigo"])
    op.create_index("ix_cfm_physicians_identificador_valido", "cfm_physicians", ["identificador_valido"])
    op.create_index("ix_cfm_physicians_is_regular", "cfm_physicians", ["is_regular"])
    op.create_index("ix_cfm_physicians_is_current", "cfm_physicians", ["is_current"])
    op.create_index("ix_cfm_physicians_last_seen_at", "cfm_physicians", ["last_seen_at"])
    op.create_index("ix_cfm_physicians_last_live_verified_at", "cfm_physicians", ["last_live_verified_at"])
    op.create_index("ix_cfm_physicians_last_seen_sync_id", "cfm_physicians", ["last_seen_sync_id"])
    op.create_index("ix_cfm_physicians_lookup_live", "cfm_physicians", ["uf", "crm_consulta", "is_current"])
    op.create_index("ix_cfm_physicians_regular_current", "cfm_physicians", ["is_regular", "is_current"])


def downgrade() -> None:
    op.drop_table("cfm_physicians")
    op.drop_table("cfm_sync_runs")
