"""last_seen_at em users + tabela chat_messages

Revision ID: c4a1f7e93b6d
Revises: 78ee6d515a27
Create Date: 2026-07-31
"""
from alembic import op
import sqlalchemy as sa

revision = "c4a1f7e93b6d"
down_revision = "78ee6d515a27"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    colunas_users = [c["name"] for c in inspector.get_columns("users")]
    if "last_seen_at" not in colunas_users:
        op.add_column(
            "users",
            sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        )

    tabelas = inspector.get_table_names()
    if "chat_messages" not in tabelas:
        op.create_table(
            "chat_messages",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
            sa.Column("recipient_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index(
            "ix_chat_messages_par_conversa", "chat_messages", ["sender_id", "recipient_id", "created_at"]
        )
        op.create_index(
            "ix_chat_messages_nao_lidas", "chat_messages", ["recipient_id", "read_at"]
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if "chat_messages" in inspector.get_table_names():
        op.drop_index("ix_chat_messages_nao_lidas", table_name="chat_messages")
        op.drop_index("ix_chat_messages_par_conversa", table_name="chat_messages")
        op.drop_table("chat_messages")

    colunas_users = [c["name"] for c in inspector.get_columns("users")]
    if "last_seen_at" in colunas_users:
        op.drop_column("users", "last_seen_at")
