"""Stable slug identities alongside all existing numeric favorites."""
from alembic import op
import sqlalchemy as sa
revision = 'c2fv20260910'
down_revision = 'c1sp20260910'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('favorites', sa.Column('item_slug',sa.String(500),nullable=True))
    op.alter_column('favorites','item_id',existing_type=sa.Integer(),nullable=True)
    op.create_unique_constraint('uq_favorito_slug_unico','favorites',['user_id','item_type','item_slug'])
    op.create_check_constraint('ck_favorito_identity','favorites','item_id IS NOT NULL OR item_slug IS NOT NULL')

def downgrade():
    # A downgrade must not silently destroy slug-only user favorites.
    connection=op.get_bind()
    if connection.execute(sa.text('SELECT count(*) FROM favorites WHERE item_id IS NULL')).scalar():
        raise RuntimeError('Favoritos por slug precisam ser preservados antes de reverter a migração.')
    op.drop_constraint('ck_favorito_identity','favorites',type_='check')
    op.drop_constraint('uq_favorito_slug_unico','favorites',type_='unique')
    op.alter_column('favorites','item_id',existing_type=sa.Integer(),nullable=False)
    op.drop_column('favorites','item_slug')
