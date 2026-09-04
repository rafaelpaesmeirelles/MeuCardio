"""UniqueConstraint em document_chunks(document_id, ordem) — achado da
revisão adversarial da correção coordenada de 03/09/2026.

Revision ID: b8sk20260903
Revises: b7ri20260903
Create Date: 2026-09-03

`knowledge_chunks` ganhou `UniqueConstraint(entity_type, entity_id, ordem)` na
migration anterior (`b7ri20260903`), mas `document_chunks` ficou sem o
equivalente — nunca teve, em nenhuma migration anterior. Um revisor
adversarial reproduziu ao vivo (duas transações Postgres concorrentes,
simulando duas chamadas de `indexar_documento()` para o MESMO documento) que
o padrão DELETE-então-INSERT de `rag.py::indexar_documento()`, sem essa trava,
permite duas linhas sobreviverem com o mesmo `(document_id, ordem)` — chunk
duplicado, servido duas vezes ao assistente clínico até a próxima reindexação
corrigir por `content_hash` (e mesmo assim, sem `ORDER BY` determinístico, a
checagem de "já está em dia" passaria a ler uma das duas linhas
arbitrariamente).

Com a constraint em vigor, a mesma corrida vira uma `IntegrityError` capturada
pelo `try/except` já existente em `indexar_tudo()`/`indexar_tipo()` — conta
como falha do item, é revertida (`db.rollback()`) e o documento continua
pendente, reindexado com sucesso na próxima chamada (idempotente). Nunca mais
duplicata silenciosa.

Produção conferida antes de escrever esta migration (read-only,
`03/09/2026`): zero pares `(document_id, ordem)` duplicados nas 16.330 linhas
atuais de `document_chunks` — a constraint aplica sem precisar de nenhum
DELETE de saneamento.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b8sk20260903"
down_revision = "b7ri20260903"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Falha alto e claro se, entre a auditoria acima e este `upgrade()` rodar
    # de verdade em produção, algum duplicado tiver aparecido — melhor a
    # migration abortar com mensagem explícita do que silenciosamente perder
    # uma das duas linhas (não fazemos DELETE automático de duplicata: dado
    # clínico não se descarta por inferência de migration).
    conexao = op.get_bind()
    duplicados = conexao.execute(
        sa.text(
            "SELECT document_id, ordem, count(*) AS n FROM document_chunks "
            "GROUP BY document_id, ordem HAVING count(*) > 1 LIMIT 5"
        )
    ).fetchall()
    if duplicados:
        raise RuntimeError(
            "document_chunks tem pares (document_id, ordem) duplicados — a "
            "UniqueConstraint não pode ser criada sem resolver manualmente "
            f"primeiro. Amostra (até 5): {list(duplicados)!r}"
        )

    op.create_unique_constraint(
        "uq_document_chunks_document_id_ordem", "document_chunks", ["document_id", "ordem"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_document_chunks_document_id_ordem", "document_chunks", type_="unique")
