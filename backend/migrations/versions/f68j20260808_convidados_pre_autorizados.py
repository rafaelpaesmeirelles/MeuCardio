"""Pré-autorização de convidado por e-mail (08/08/2026).

Pedido do Rafael: em vez de só liberar `users.convidado` depois que a pessoa
já se cadastrou (via `PATCH /api/admin/users/{id}/convidado`, painel Admin),
o admin cadastra o e-mail ANTES — quando esse e-mail se cadastrar em
`POST /auth/solicitar-acesso`, o sistema já cria o usuário com
`convidado = True` sozinho, sem precisar lembrar de marcar depois.

Mecanismo genérico e reutilizável (não hardcoded para nenhum e-mail
específico) — a linha para o primeiro convidado real (Dr. Márcio Peixoto)
é inserida à parte, por dado, não por código.

Revision ID: f68j20260808
Revises: f67i20260808
Create Date: 2026-08-08
"""

from alembic import op
import sqlalchemy as sa

revision = "f68j20260808"
down_revision = "f67i20260808"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "convidados_pre_autorizados",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column("observacao", sa.String(length=300), nullable=True),
        sa.Column("criado_por", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        # Preenchidos quando o e-mail de fato se cadastra e consome a
        # pré-autorização — None enquanto ainda não usado. Consumo é
        # único: uma vez usado, não se aplica de novo (ver comentário em
        # app/models/convidado_pre_autorizado.py).
        sa.Column("usado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("usado_por_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("convidados_pre_autorizados")
