"""trilhas de estudo e progresso por medico

Tarefa 11b. O progresso guarda o slug da etapa concluida, e nao a posicao na
lista: reordenar a trilha depois nao pode reescrever o que a pessoa ja leu.

Revision ID: e5c72a90f14b
Revises: d1a68b3c47e2
Create Date: 2026-07-28 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'e5c72a90f14b'
down_revision = 'd1a68b3c47e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    tabelas = set(sa.inspect(op.get_bind()).get_table_names())
    if "study_tracks" not in tabelas:
        op.create_table(
            "study_tracks",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("slug", sa.String(120), nullable=False, unique=True),
            sa.Column("titulo", sa.String(200), nullable=False),
            sa.Column("tema", sa.String(120), nullable=True),
            sa.Column("objetivo", sa.Text(), nullable=True),
            sa.Column("nivel", sa.String(30), nullable=True),
            sa.Column("etapas", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
            sa.Column("review_status", sa.String(30), nullable=False, server_default="pendente_revisao"),
            sa.Column("revisao", sa.Text(), nullable=True),
            sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
        op.create_index("ix_study_tracks_slug", "study_tracks", ["slug"], unique=True)
        op.create_index("ix_study_tracks_published", "study_tracks", ["published"])
        op.create_index("ix_study_tracks_tema", "study_tracks", ["tema"])

    if "study_track_progress" not in tabelas:
        op.create_table(
            "study_track_progress",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("track_id", sa.Integer(), sa.ForeignKey("study_tracks.id", ondelete="CASCADE"), nullable=False),
            sa.Column("concluidas", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
            sa.Column("concluida_em", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.UniqueConstraint("user_id", "track_id", name="uq_progresso_trilha"),
        )
        op.create_index("ix_progress_user", "study_track_progress", ["user_id"])
        op.create_index("ix_progress_track", "study_track_progress", ["track_id"])


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS study_track_progress CASCADE")
    op.execute("DROP TABLE IF EXISTS study_tracks CASCADE")
