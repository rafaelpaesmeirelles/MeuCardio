"""adiciona tabela subscriptions

Revision ID: f95465113955
Revises: 84eeeb026a98
Create Date: 2026-07-26 22:43:13.351830
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'f95465113955'
down_revision = '84eeeb026a98'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('current_period_end', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='subscriptions_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='subscriptions_pkey'),
    )
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'], unique=True)
    op.create_index(
        'ix_subscriptions_stripe_subscription_id', 'subscriptions', ['stripe_subscription_id'], unique=True
    )
    op.create_index(
        'ix_subscriptions_stripe_customer_id', 'subscriptions', ['stripe_customer_id'], unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_subscriptions_stripe_customer_id', table_name='subscriptions')
    op.drop_index('ix_subscriptions_stripe_subscription_id', table_name='subscriptions')
    op.drop_index('ix_subscriptions_user_id', table_name='subscriptions')
    op.drop_table('subscriptions')
