"""email_logs + patient_material_sends (e-mails transacionais, 02/08/2026)

Revision ID: a3f6d081c9e4
Revises: c4a1f7e93b6d
Create Date: 2026-08-02
"""
from alembic import op
import sqlalchemy as sa

revision = "a3f6d081c9e4"
down_revision = "c4a1f7e93b6d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tabelas = inspector.get_table_names()

    if "email_logs" not in tabelas:
        op.create_table(
            "email_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tipo", sa.String(60), nullable=False, index=True),
            sa.Column("destinatario", sa.String(255), nullable=False, index=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True, index=True),
            sa.Column("chave_idempotencia", sa.String(120), nullable=True),
            sa.Column("sucesso", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("erro", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
        )
        op.create_index(
            "uq_email_log_idempotencia", "email_logs", ["tipo", "chave_idempotencia"],
            unique=True, postgresql_where=sa.text("chave_idempotencia IS NOT NULL"),
        )

    if "patient_material_sends" not in tabelas:
        op.create_table(
            "patient_material_sends",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "share_link_id", sa.Integer(),
                sa.ForeignKey("document_share_links.id", ondelete="CASCADE"),
                nullable=False, unique=True, index=True,
            ),
            sa.Column("material_id", sa.Integer(), sa.ForeignKey("patient_materials.id"), nullable=False, index=True),
            sa.Column("enviado_por", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
            sa.Column("paciente_email_cifrado", sa.LargeBinary(), nullable=False),
            sa.Column("recado_cifrado", sa.LargeBinary(), nullable=True),
            sa.Column("consentimento_confirmado", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("canal", sa.Text(), nullable=False, server_default="mail360"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
        )

    # Teto de envio por médico (spec material-paciente-por-email): três
    # reclamações de spam numa mesma caixa suspendem o envio automaticamente.
    colunas_email_accounts = [c["name"] for c in inspector.get_columns("email_accounts")]
    if "reclamacoes_spam" not in colunas_email_accounts:
        op.add_column(
            "email_accounts",
            sa.Column("reclamacoes_spam", sa.Integer(), nullable=False, server_default="0"),
        )
    if "envio_material_suspenso" not in colunas_email_accounts:
        op.add_column(
            "email_accounts",
            sa.Column("envio_material_suspenso", sa.Boolean(), nullable=False, server_default=sa.false()),
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tabelas = inspector.get_table_names()

    colunas_email_accounts = [c["name"] for c in inspector.get_columns("email_accounts")]
    if "envio_material_suspenso" in colunas_email_accounts:
        op.drop_column("email_accounts", "envio_material_suspenso")
    if "reclamacoes_spam" in colunas_email_accounts:
        op.drop_column("email_accounts", "reclamacoes_spam")

    if "patient_material_sends" in tabelas:
        op.drop_table("patient_material_sends")

    if "email_logs" in tabelas:
        op.drop_index("uq_email_log_idempotencia", table_name="email_logs")
        op.drop_table("email_logs")
