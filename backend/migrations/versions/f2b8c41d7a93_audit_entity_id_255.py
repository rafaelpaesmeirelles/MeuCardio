"""audit_logs.entity_id: 80 -> 255 caracteres

`documents.slug` é String(255), mas `audit_logs.entity_id` nasceu String(80).
Publicar ou despublicar um documento com slug mais longo estourava
StringDataRightTruncation ao gravar a auditoria, devolvia 500 e revertia a
transação inteira — inclusive a mudança de `published`, que já tinha sido
aplicada no objeto. Efeito prático: **16 documentos do acervo não podiam ser
publicados nem despublicados**, e o sintoma só aparecia ao tentar.

Descoberto ao despublicar o documento absorvido pela fusão de endocardite,
cujo slug tem 82 caracteres.

Revision ID: f2b8c41d7a93
Revises: e1a7b93c2d64
Create Date: 2026-07-28 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'f2b8c41d7a93'
down_revision = 'e1a7b93c2d64'
branch_labels = None
depends_on = None


def upgrade() -> None:
    colunas = {c["name"]: c for c in sa.inspect(op.get_bind()).get_columns("audit_logs")}
    atual = colunas.get("entity_id")
    if atual is not None and getattr(atual["type"], "length", None) != 255:
        op.alter_column("audit_logs", "entity_id",
                        existing_type=sa.String(80), type_=sa.String(255),
                        existing_nullable=True)


def downgrade() -> None:
    # Encurtar de volta truncaria dados já gravados; deixado como no-op de
    # propósito, para o downgrade não destruir registro de auditoria.
    pass
