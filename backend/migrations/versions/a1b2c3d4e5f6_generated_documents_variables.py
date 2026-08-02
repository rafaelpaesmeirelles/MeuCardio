"""Tarefa 4: arquivo de receituário/documentos e recriar a partir de um anterior

Pedido do Rafael (02/08/2026): uma seção com tudo que já foi gerado
(receituário e documento), e a opção de recriar um novo baseado num anterior.
Para receituário, a base do "recriar" já existe (`Prescription.items`, cru,
desde sempre) — só faltava expor via API. Para documento gerado a partir de
modelo, faltava uma coluna: `generated_documents.variables` guarda os valores
que preencheram as `{{variaveis}}` na geração — sem isso, "recriar baseado
neste" não tem como pré-preencher o formulário, só sabe reabrir o texto já
renderizado (`rendered_body`), que não separa mais variável de texto fixo.

Revision ID: a1b2c3d4e5f6
Revises: f2c8a4d19b73
Create Date: 2026-08-02 23:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'a1b2c3d4e5f6'
down_revision = 'f2c8a4d19b73'
branch_labels = None
depends_on = None


def _colunas(bind, tabela):
    return {c["name"] for c in sa.inspect(bind).get_columns(tabela)}


def upgrade() -> None:
    bind = op.get_bind()
    if "variables" not in _colunas(bind, "generated_documents"):
        op.add_column(
            "generated_documents",
            sa.Column("variables", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    if "variables" in _colunas(bind, "generated_documents"):
        op.drop_column("generated_documents", "variables")
