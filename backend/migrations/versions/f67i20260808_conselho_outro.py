"""Conselho "Outro": campos livres para nome real e estado/região (08/08/2026).

`council_name` continua guardando o valor literal "OUTRO" — é o que
`app/services/kyc/escopo_profissional.py::escopo_de()` usa para decidir o
escopo de prescrição (fail closed: qualquer conselho fora de CRM/CRO cai no
escopo mais restrito). Não mexer nisso. Os dois campos novos são só para
EXIBIÇÃO — o nome real do conselho e o estado/região que o médico digitou,
usados no lugar do rótulo genérico "OUTRO" em documentos/perfil.

Revision ID: f67i20260808
Revises: f66h20260808
Create Date: 2026-08-08
"""

from alembic import op
import sqlalchemy as sa

revision = "f67i20260808"
down_revision = "f66h20260808"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("council_name_other", sa.String(length=120), nullable=True))
    op.add_column("users", sa.Column("council_state_other", sa.String(length=60), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "council_state_other")
    op.drop_column("users", "council_name_other")
