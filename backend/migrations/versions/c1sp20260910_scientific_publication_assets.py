"""Shared licensed originals and full textual translations."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = 'c1sp20260910'
down_revision = 'c0aw20260909'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('scientific_publication_assets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('source_key', sa.String(64), nullable=False),
        sa.Column('doi', sa.String(240)), sa.Column('source_url', sa.Text(), nullable=False),
        sa.Column('status', sa.String(40), nullable=False), sa.Column('reason', sa.Text()),
        sa.Column('pmcid', sa.String(30)), sa.Column('license_url', sa.Text()),
        sa.Column('source_sha256', sa.String(64)), sa.Column('original_storage_key', sa.String(100)),
        sa.Column('translated_storage_key', sa.String(100)), sa.Column('summary_pt', sa.Text()),
        sa.Column('progress', postgresql.JSONB(), nullable=False), sa.Column('coverage', postgresql.JSONB(), nullable=False),
        sa.Column('retry_at', sa.DateTime(timezone=True)), sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False), sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_scientific_publication_assets_source_key', 'scientific_publication_assets', ['source_key'], unique=True)
    op.create_index('ix_scientific_publication_assets_status', 'scientific_publication_assets', ['status'])
    op.create_index('ix_scientific_publication_assets_retry_at', 'scientific_publication_assets', ['retry_at'])

def downgrade():
    op.drop_table('scientific_publication_assets')
