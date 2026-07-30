"""Tarefa 30: modelos de documento do sistema (owner_id opcional)

Decisão do Rafael em 30/07/2026: "Tudo junto, mesma rodada" — construir de
uma vez os 4 modelos simples (atestado médico, declaração de acompanhante,
atestado para atividade física, documento em branco) e o modelo de
avaliação cardiológica de risco cirúrgico, todos disponíveis para QUALQUER
médico da plataforma, não só para quem os criou.

`document_templates.owner_id` era obrigatório — um médico só via os
próprios modelos. Fica opcional: `owner_id IS NULL` marca modelo do
sistema, pesquisado de fonte confiável, disponível a todos e protegido de
edição/exclusão pela checagem de posse já existente (`owner_id == user.id`
nunca casa com `None`, não precisou de exceção nova no código).

`slug_sistema` é a chave de upsert do semeador — mesmo padrão já usado em
`carregar_controlados.semear_tipos()` para `PrescriptionType` — para rodar
a seed mais de uma vez sem duplicar.

Revision ID: a1c8e4f92b6d
Revises: 9faec593af6e
Create Date: 2026-07-30 06:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1c8e4f92b6d'
down_revision = '9faec593af6e'
branch_labels = None
depends_on = None


def _colunas(bind, tabela):
    return {c["name"] for c in sa.inspect(bind).get_columns(tabela)}


def _indices(bind, tabela):
    return {i["name"] for i in sa.inspect(bind).get_indexes(tabela)}


def upgrade() -> None:
    bind = op.get_bind()

    op.alter_column(
        "document_templates", "owner_id",
        existing_type=sa.Integer(), nullable=True,
    )

    if "slug_sistema" not in _colunas(bind, "document_templates"):
        op.add_column(
            "document_templates",
            sa.Column("slug_sistema", sa.String(80), nullable=True),
        )
    if "uq_document_templates_slug_sistema" not in _indices(bind, "document_templates"):
        op.create_unique_constraint(
            "uq_document_templates_slug_sistema", "document_templates", ["slug_sistema"]
        )


def downgrade() -> None:
    bind = op.get_bind()

    if "uq_document_templates_slug_sistema" in _indices(bind, "document_templates"):
        op.drop_constraint(
            "uq_document_templates_slug_sistema", "document_templates", type_="unique"
        )
    if "slug_sistema" in _colunas(bind, "document_templates"):
        op.drop_column("document_templates", "slug_sistema")

    op.alter_column(
        "document_templates", "owner_id",
        existing_type=sa.Integer(), nullable=False,
    )
