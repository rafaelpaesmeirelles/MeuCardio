"""Tarefa 29: endereços completos do médico, escolha de qual sai no PDF,
e campos exigidos por lei para receita de anabolizantes/hormônios

Decisão do Rafael em 30/07/2026: Minha Conta passa a ter endereço
residencial E profissional completos, e o médico escolhe, a cada
receita/documento emitido, qual dos dois aparece no cabeçalho/rodapé
(privacidade — nem todo médico quer endereço de casa num papel impresso).

Quatro mudanças:
1. `users` ganha 14 colunas de endereço (7 residencial + 7 profissional).
2. `users.practice_phone` — telefone profissional, exigido por lei
   especificamente para anabolizantes (Lei nº 9.965/2000, art. 1º,
   parágrafo único, conferido direto na fonte em 30/07/2026).
3. `prescription_documents.endereco_exibido` e
   `generated_documents.endereco_exibido` guardam a escolha feita na
   emissão — precisa ser um valor GRAVADO, não recalculado a cada acesso,
   porque o link público (Tarefa 29, `documentos_publicos.py`) reabre o
   mesmo PDF depois e ele tem que sair idêntico, não variar com o que o
   médico tiver em Minha Conta naquele momento.
4. `prescription_documents.cid` — idem, exigido pela mesma lei para
   anabolizantes. A emissão de RCE continua bloqueada (layout oficial não
   reproduzido); os campos existem só para não perder o requisito.
5. `users.document_logo_url` — logo pessoal/do consultório, usada JUNTO da
   logo da Corvia no cabeçalho de receita e documento.

Revision ID: 9faec593af6e
Revises: 425d4a2318d7
Create Date: 2026-07-30 05:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '9faec593af6e'
down_revision = '425d4a2318d7'
branch_labels = None
depends_on = None

CAMPOS_ENDERECO = [
    ("street", sa.String(200)), ("number", sa.String(20)), ("complement", sa.String(100)),
    ("neighborhood", sa.String(100)), ("city", sa.String(120)), ("state", sa.String(2)),
    ("zip", sa.String(10)),
]


def _colunas(bind, tabela):
    return {c["name"] for c in sa.inspect(bind).get_columns(tabela)}


def upgrade() -> None:
    bind = op.get_bind()
    existentes = _colunas(bind, "users")

    for prefixo in ("home", "practice"):
        for sufixo, tipo in CAMPOS_ENDERECO:
            nome = f"{prefixo}_{sufixo}"
            if nome not in existentes:
                op.add_column("users", sa.Column(nome, tipo, nullable=True))

    if "practice_phone" not in existentes:
        op.add_column("users", sa.Column("practice_phone", sa.String(20), nullable=True))

    if "document_logo_url" not in existentes:
        op.add_column("users", sa.Column("document_logo_url", sa.String(255), nullable=True))

    if "endereco_exibido" not in _colunas(bind, "prescription_documents"):
        op.add_column("prescription_documents", sa.Column("endereco_exibido", sa.String(20), nullable=True))

    if "cid" not in _colunas(bind, "prescription_documents"):
        op.add_column("prescription_documents", sa.Column("cid", sa.String(10), nullable=True))

    if "endereco_exibido" not in _colunas(bind, "generated_documents"):
        op.add_column("generated_documents", sa.Column("endereco_exibido", sa.String(20), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()

    if "endereco_exibido" in _colunas(bind, "generated_documents"):
        op.drop_column("generated_documents", "endereco_exibido")

    if "cid" in _colunas(bind, "prescription_documents"):
        op.drop_column("prescription_documents", "cid")

    if "endereco_exibido" in _colunas(bind, "prescription_documents"):
        op.drop_column("prescription_documents", "endereco_exibido")

    existentes = _colunas(bind, "users")
    if "document_logo_url" in existentes:
        op.drop_column("users", "document_logo_url")
    if "practice_phone" in existentes:
        op.drop_column("users", "practice_phone")
    for prefixo in ("home", "practice"):
        for sufixo, _tipo in CAMPOS_ENDERECO:
            nome = f"{prefixo}_{sufixo}"
            if nome in existentes:
                op.drop_column("users", nome)
