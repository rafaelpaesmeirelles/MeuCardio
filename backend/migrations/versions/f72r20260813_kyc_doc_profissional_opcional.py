"""Documento profissional passa a ser opcional em kyc_verifications (investidor).

Pedido do Rafael: contas de investidor (`users.investidor`) não são médicos
reais passando por credenciamento profissional — não têm profissão,
conselho, nem documento profissional para enviar. O KYC delas passa a ser
"pessoal simplificado" (documento pessoal + selfie ao vivo, sem documento
profissional), diferente do KYC completo que convidado e assinante normal
continuam exigindo.

`doc_profissional_frente`/`doc_profissional_verso` eram `NOT NULL` — coluna
obrigatória mesmo para quem nunca vai enviar esse documento. Alterado para
nullable; a obrigatoriedade dinâmica por tipo de conta passa a ser aplicada
em `app/services/kyc/verificacao.py::submeter()`, não mais só pelo schema
do banco. Nenhum dado existente muda — todo registro já gravado tem os dois
campos preenchidos (era `NOT NULL` até aqui), então relaxar a restrição não
apaga nem reescreve nenhuma linha.

Revision ID: f72r20260813
Revises: f71q20260812
Create Date: 2026-08-13
"""

from alembic import op
import sqlalchemy as sa

revision = "f72r20260813"
down_revision = "f71q20260812"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("kyc_verifications", "doc_profissional_frente", nullable=True)
    op.alter_column("kyc_verifications", "doc_profissional_verso", nullable=True)


def downgrade() -> None:
    op.alter_column("kyc_verifications", "doc_profissional_frente", nullable=False)
    op.alter_column("kyc_verifications", "doc_profissional_verso", nullable=False)
