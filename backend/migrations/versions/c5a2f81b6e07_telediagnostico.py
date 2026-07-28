"""telediagnóstico: conteúdo clínico do pedido e dados do paciente

Revision ID: c5a2f81b6e07
Revises: b4e1c07a9d33
Create Date: 2026-07-28 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'c5a2f81b6e07'
down_revision = 'b4e1c07a9d33'
branch_labels = None
depends_on = None

COLUNAS = [
    ('duvida', sa.Text()),
    ('contato_email', sa.String(length=255)),
    ('contato_whatsapp', sa.String(length=40)),
    ('arquivo_exame', sa.String(length=80)),
    ('arquivo_nome_original', sa.String(length=255)),
    ('arquivo_tipo', sa.String(length=40)),
    ('consentimento_em', sa.DateTime(timezone=True)),
    ('prazo_em', sa.DateTime(timezone=True)),
    ('atendido_em', sa.DateTime(timezone=True)),
    ('resposta', sa.Text()),
]


def upgrade() -> None:
    inspetor = sa.inspect(op.get_bind())

    existentes = {c["name"] for c in inspetor.get_columns("service_orders")}
    for nome, tipo in COLUNAS:
        if nome not in existentes:
            op.add_column('service_orders', sa.Column(nome, tipo, nullable=True))

    if 'service_order_patient' not in inspetor.get_table_names():
        op.create_table(
            'service_order_patient',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('order_id', sa.Integer(), nullable=False),
            sa.Column('nome', sa.String(length=255), nullable=False),
            sa.Column('cpf', sa.String(length=14), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(['order_id'], ['service_orders.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('order_id'),
        )
        op.create_index('ix_service_order_patient_order_id', 'service_order_patient', ['order_id'])

    # Índice para a fila de atendimento, que ordena por prazo.
    indices = {i["name"] for i in inspetor.get_indexes("service_orders")}
    if 'ix_service_orders_prazo_em' not in indices:
        op.create_index('ix_service_orders_prazo_em', 'service_orders', ['prazo_em'])


def downgrade() -> None:
    op.drop_index('ix_service_orders_prazo_em', table_name='service_orders')
    op.drop_table('service_order_patient')
    for nome, _ in reversed(COLUNAS):
        op.drop_column('service_orders', nome)
