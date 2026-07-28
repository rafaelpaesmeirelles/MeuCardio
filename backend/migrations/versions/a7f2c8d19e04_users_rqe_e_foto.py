"""users: colunas rqe e photo_url para a página Minha Conta

O RQE identifica a especialidade registrada no conselho e entra no cabeçalho
de documento emitido pelo profissional; a foto é só de perfil. Ambas nullable:
todo cadastro existente continua válido sem preencher nada.

Revision ID: a7f2c8d19e04
Revises: c3d9a1f47b20
Create Date: 2026-07-28 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'a7f2c8d19e04'
down_revision = 'c3d9a1f47b20'
branch_labels = None
depends_on = None


def _colunas_existentes() -> set[str]:
    inspetor = sa.inspect(op.get_bind())
    return {c["name"] for c in inspetor.get_columns("users")}


def upgrade() -> None:
    # Idempotente de propósito. O histórico deste banco já teve o `alembic_version`
    # fora de sincronia com o schema real (ver CLAUDE.md), então uma migração que
    # assume o estado anterior pode estourar em vez de convergir. Conferir a
    # coluna antes de criar custa uma consulta ao catálogo e evita isso.
    colunas = _colunas_existentes()
    if 'rqe' not in colunas:
        op.add_column('users', sa.Column('rqe', sa.String(length=40), nullable=True))
    if 'photo_url' not in colunas:
        op.add_column('users', sa.Column('photo_url', sa.String(length=255), nullable=True))


def downgrade() -> None:
    colunas = _colunas_existentes()
    if 'photo_url' in colunas:
        op.drop_column('users', 'photo_url')
    if 'rqe' in colunas:
        op.drop_column('users', 'rqe')
