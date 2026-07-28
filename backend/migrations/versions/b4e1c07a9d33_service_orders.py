"""service_orders: pedidos avulsos de laudo e consultoria

Revision ID: b4e1c07a9d33
Revises: a7f2c8d19e04
Create Date: 2026-07-28 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'b4e1c07a9d33'
down_revision = 'a7f2c8d19e04'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Idempotente pelo mesmo motivo da migração anterior: o histórico deste
    # banco já teve alembic_version fora de sincronia com o schema real.
    if 'service_orders' in sa.inspect(op.get_bind()).get_table_names():
        return

    op.create_table(
        'service_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('servico', sa.String(length=20), nullable=False),
        sa.Column('urgencia', sa.String(length=20), nullable=False),
        sa.Column('exame', sa.String(length=20), nullable=True),
        sa.Column('preco_centavos', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False,
                  server_default='aguardando_pagamento'),
        sa.Column('stripe_checkout_session_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('pago_em', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_checkout_session_id'),
    )
    op.create_index('ix_service_orders_user_id', 'service_orders', ['user_id'])
    op.create_index('ix_service_orders_status', 'service_orders', ['status'])
    op.create_index('ix_service_orders_stripe_payment_intent_id', 'service_orders',
                    ['stripe_payment_intent_id'])
    op.create_index('ix_service_orders_stripe_checkout_session_id', 'service_orders',
                    ['stripe_checkout_session_id'])


def downgrade() -> None:
    op.drop_table('service_orders')
