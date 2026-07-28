"""discharge_checklists.revisao

O `review_status` registra QUE houve revisão; este campo registra DE QUEM foi e
quando. Num produto cuja responsabilidade clínica é de um cardiologista
nomeado, essa informação não pode viver apenas no log de auditoria — ela
pertence ao conteúdo.

Revision ID: d1a68b3c47e2
Revises: c8e35f1a9d47
Create Date: 2026-07-28 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'd1a68b3c47e2'
down_revision = 'c8e35f1a9d47'
branch_labels = None
depends_on = None


def upgrade() -> None:
    colunas = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("discharge_checklists")}
    if "revisao" not in colunas:
        op.add_column("discharge_checklists", sa.Column("revisao", sa.Text(), nullable=True))


def downgrade() -> None:
    colunas = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("discharge_checklists")}
    if "revisao" in colunas:
        op.drop_column("discharge_checklists", "revisao")
