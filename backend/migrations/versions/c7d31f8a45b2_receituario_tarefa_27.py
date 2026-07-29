"""Receituário — substâncias 344/98, tipos, regras de adendo e documentos (Tarefa 27).

Idempotente: este banco já teve `alembic_version` fora de sincronia com o schema
real — em 29/07/2026 ele estava em `a2f47d81c6b9` com as tabelas de
`b4e19a2c73f5` já criadas pelo `create_all` do startup. Migração que assume o
estado do catálogo em vez de conferir reproduz aquele incidente.

Revision ID: c7d31f8a45b2
Revises: b4e19a2c73f5
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "c7d31f8a45b2"
down_revision = "b4e19a2c73f5"
branch_labels = None
depends_on = None


def _tem(nome: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(nome)


def upgrade() -> None:
    if not _tem("controlled_substances"):
        op.create_table(
            "controlled_substances",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("nome", sa.String(length=300), nullable=False),
            sa.Column("nome_normalizado", sa.String(length=300), nullable=False),
            sa.Column("sinonimos", postgresql.ARRAY(sa.String()), nullable=False,
                      server_default="{}"),
            sa.Column("lista", sa.String(length=4), nullable=False),
            sa.Column("tipo_sncr", sa.String(length=8), nullable=True),
            sa.Column("proscrita", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("fonte_norma", sa.String(length=200), nullable=False),
            sa.Column("fonte_versao", sa.String(length=60), nullable=False),
            sa.PrimaryKeyConstraint("id", name="controlled_substances_pkey"),
            # Uma substância pode reaparecer numa versão nova da norma, em outra
            # lista. A unicidade é por versão, não global — senão a atualização
            # de RDC colide com o histórico em vez de conviver com ele.
            sa.UniqueConstraint("nome_normalizado", "fonte_versao",
                                name="uq_substancia_por_versao"),
        )
        op.create_index("ix_controlled_substances_nome_normalizado",
                        "controlled_substances", ["nome_normalizado"])
        op.create_index("ix_controlled_substances_lista", "controlled_substances", ["lista"])
        op.create_index("ix_controlled_substances_fonte_versao",
                        "controlled_substances", ["fonte_versao"])

    if not _tem("prescription_types"):
        op.create_table(
            "prescription_types",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("codigo", sa.String(length=8), nullable=False),
            sa.Column("nome", sa.String(length=160), nullable=False),
            sa.Column("cor", sa.String(length=30), nullable=True),
            sa.Column("vias", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("destinacao_vias", postgresql.ARRAY(sa.String()), nullable=False,
                      server_default="{}"),
            sa.Column("exige_numeracao_sncr", sa.Boolean(), nullable=False,
                      server_default=sa.false()),
            sa.Column("endpoint_sncr", sa.String(length=80), nullable=True),
            sa.Column("lote_min", sa.Integer(), nullable=True),
            sa.Column("lote_max", sa.Integer(), nullable=True),
            sa.Column("validade_dias", sa.Integer(), nullable=True),
            sa.Column("exige_retencao", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("campos_obrigatorios", postgresql.ARRAY(sa.String()), nullable=False,
                      server_default="{}"),
            sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.PrimaryKeyConstraint("id", name="prescription_types_pkey"),
            sa.UniqueConstraint("codigo", name="uq_prescription_type_codigo"),
        )
        op.create_index("ix_prescription_types_ativo", "prescription_types", ["ativo"])

    if not _tem("prescription_rules"):
        op.create_table(
            "prescription_rules",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("lista", sa.String(length=4), nullable=False),
            sa.Column("texto_normativo", sa.Text(), nullable=False),
            sa.Column("tipo_resultante", sa.String(length=8), nullable=True),
            sa.Column("codificada", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("condicao", postgresql.JSONB(), nullable=False, server_default="{}"),
            sa.Column("fonte_versao", sa.String(length=60), nullable=False),
            sa.PrimaryKeyConstraint("id", name="prescription_rules_pkey"),
        )
        op.create_index("ix_prescription_rules_lista", "prescription_rules", ["lista"])

    if not _tem("prescription_recipients"):
        op.create_table(
            "prescription_recipients",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("prescription_id", sa.Integer(), nullable=False),
            # LargeBinary e não texto: o valor é ciframento binário do cofre
            # (nonce + AES-256-GCM), não string. Guardar como texto obrigaria a
            # base64 no meio do caminho, sem ganho nenhum.
            sa.Column("nome_cifrado", sa.LargeBinary(), nullable=False),
            sa.Column("endereco_cifrado", sa.LargeBinary(), nullable=True),
            sa.Column("documento_cifrado", sa.LargeBinary(), nullable=True),
            sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), nullable=False,
                      server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(["prescription_id"], ["prescriptions.id"],
                                    name="prescription_recipients_prescription_id_fkey",
                                    ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id", name="prescription_recipients_pkey"),
        )
        op.create_index("ix_prescription_recipients_prescription_id",
                        "prescription_recipients", ["prescription_id"], unique=True)

    if not _tem("prescription_documents"):
        op.create_table(
            "prescription_documents",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("prescription_id", sa.Integer(), nullable=False),
            sa.Column("tipo_codigo", sa.String(length=8), nullable=False),
            sa.Column("numeracao", sa.String(length=30), nullable=True),
            sa.Column("itens", postgresql.JSONB(), nullable=False, server_default="[]"),
            sa.Column("status", sa.String(length=20), nullable=False,
                      server_default="rascunho"),
            sa.Column("classificacao_corrigida_de", sa.String(length=8), nullable=True),
            sa.Column("motivo_correcao", sa.Text(), nullable=True),
            sa.Column("pendencias", postgresql.JSONB(), nullable=False, server_default="[]"),
            sa.Column("fonte_versao_listas", sa.String(length=60), nullable=True),
            sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), nullable=False,
                      server_default=sa.text("now()")),
            sa.Column("emitido_em", postgresql.TIMESTAMP(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["prescription_id"], ["prescriptions.id"],
                                    name="prescription_documents_prescription_id_fkey",
                                    ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id", name="prescription_documents_pkey"),
        )
        op.create_index("ix_prescription_documents_prescription_id",
                        "prescription_documents", ["prescription_id"])
        op.create_index("ix_prescription_documents_tipo_codigo",
                        "prescription_documents", ["tipo_codigo"])
        op.create_index("ix_prescription_documents_status",
                        "prescription_documents", ["status"])
        # A numeração do SNCR é escassa e rastreada: número repetido em dois
        # documentos é problema regulatório, não bug cosmético. O índice parcial
        # permite muitos nulos (documento ainda sem numeração) e proíbe repetido.
        op.create_index("uq_prescription_documents_numeracao", "prescription_documents",
                        ["numeracao"], unique=True,
                        postgresql_where=sa.text("numeracao IS NOT NULL"))


def downgrade() -> None:
    for tabela in ("prescription_documents", "prescription_recipients",
                   "prescription_rules", "prescription_types", "controlled_substances"):
        if _tem(tabela):
            op.drop_table(tabela)
