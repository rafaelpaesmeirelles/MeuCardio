"""Desativa compromissos sintéticos reservados deixados na agenda.

Revision ID: f93s20260901
Revises: f92s20260901
Create Date: 2026-09-01

O prefixo literal ``[SMOKE-TEST]`` é reservado aos testes de release e já é
filtrado no frontend. Esta migração faz o mesmo soft-delete usado pela API,
mantém os registros recuperáveis e grava auditoria por proprietário. Títulos
reais apenas semelhantes, com outra caixa ou com o termo no meio, não entram.
"""

from alembic import op
import sqlalchemy as sa


revision = "f93s20260901"
down_revision = "f92s20260901"
branch_labels = None
depends_on = None

AUDIT_ACTION = "reserved_smoke_test_cleanup"
AUDIT_ENTITY = "calendar_commitment_series"
_RESERVED_TITLE_PREDICATE = (
    "regexp_replace(series.title, '^[[:space:]]+', '') LIKE '[SMOKE-TEST]%'"
)


def _disable_reserved_smoke_series(connection) -> int:
    result = connection.execute(sa.text(f"""
        WITH disabled AS (
            UPDATE calendar_commitment_series AS series
            SET active = FALSE,
                updated_at = now()
            WHERE series.active IS TRUE
              AND {_RESERVED_TITLE_PREDICATE}
            RETURNING series.id, series.owner_id
        )
        INSERT INTO audit_logs (
            user_id, action, entity, entity_id, detail, created_at
        )
        SELECT
            NULL,
            :action,
            :entity,
            disabled.id::text,
            jsonb_build_object(
                'migration', :revision,
                'operation', 'soft_disable_reserved_test_series',
                'owner_id', disabled.owner_id
            ),
            now()
        FROM disabled
        RETURNING entity_id
    """), {
        "action": AUDIT_ACTION,
        "entity": AUDIT_ENTITY,
        "revision": revision,
    })
    return len(result.fetchall())


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if not inspector.has_table("calendar_commitment_series"):
        raise RuntimeError("expected calendar_commitment_series table is missing")
    if not inspector.has_table("audit_logs"):
        raise RuntimeError("expected audit_logs table is missing")

    # Um único statement desativa e audita exatamente o mesmo conjunto, sem
    # janela em que uma série pudesse ser alterada sem registro correspondente.
    _disable_reserved_smoke_series(connection)


def downgrade() -> None:
    # Reativar dados sintéticos em um downgrade faria os compromissos de teste
    # reaparecerem para os usuários. O soft-delete continua recuperável por uma
    # operação administrativa explícita baseada no registro de auditoria.
    pass
