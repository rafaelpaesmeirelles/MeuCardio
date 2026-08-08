# -*- coding: utf-8 -*-
"""Envio ao paciente por e-mail, integrado à prescrição/documento assinado e
ao Material ao Paciente (pedido do Rafael, 08/08/2026).

Tabela de auditoria genérica (`patient_document_email_sends`) para os dois
canais novos oferecidos ao concluir a assinatura digital (ou a geração de
Material ao Paciente, que não exige assinatura): envio automático pela conta
`contato@corvia.med.br` (SMTP, link seguro) ou envio pela própria caixa do
CorvIA Mail (Mail360, PDF anexado de verdade no compositor — ver
`app/models/patient_document_email_send.py` para a justificativa completa da
divergência entre os dois canais).

Revision ID: f69k20260808
Revises: f68j20260808
Create Date: 2026-08-08
"""

from alembic import op
import sqlalchemy as sa

revision = "f69k20260808"
down_revision = "f68j20260808"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "patient_document_email_sends",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tipo_origem", sa.String(length=30), nullable=False),
        sa.Column("referencia_id", sa.Integer(), nullable=False),
        sa.Column("canal", sa.String(length=30), nullable=False),
        sa.Column("share_link_id", sa.Integer(), sa.ForeignKey("document_share_links.id"), nullable=True),
        sa.Column("enviado_por", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("paciente_email_cifrado", sa.LargeBinary(), nullable=False),
        sa.Column("assinatura_confirmada", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sucesso", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_patient_document_email_sends_tipo_origem",
        "patient_document_email_sends", ["tipo_origem"],
    )
    op.create_index(
        "ix_patient_document_email_sends_referencia_id",
        "patient_document_email_sends", ["referencia_id"],
    )
    op.create_index(
        "ix_patient_document_email_sends_enviado_por",
        "patient_document_email_sends", ["enviado_por"],
    )
    op.create_index(
        "ix_patient_document_email_sends_created_at",
        "patient_document_email_sends", ["created_at"],
    )


def downgrade() -> None:
    op.drop_table("patient_document_email_sends")
