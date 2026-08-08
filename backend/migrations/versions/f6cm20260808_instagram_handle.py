"""Instagram opcional no cadastro (tarefa #43, 08/08/2026).

Campo livre, digitado pelo próprio médico em /solicitar-acesso — nunca
buscado/adivinhado pelo sistema. instagram_photo_url é preenchido em
segundo plano, melhor esforço, a partir do handle acima (ver
app/services/instagram_profile.py); fica nulo enquanto não resolvido, ou
se a busca falhar/perfil for privado/não existir.

Revision ID: f6cm20260808
Revises: f69k20260808
Create Date: 2026-08-08
"""

from alembic import op
import sqlalchemy as sa

revision = "f6cm20260808"
down_revision = "f69k20260808"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("instagram_handle", sa.String(length=60), nullable=True))
    op.add_column("users", sa.Column("instagram_photo_url", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "instagram_photo_url")
    op.drop_column("users", "instagram_handle")
