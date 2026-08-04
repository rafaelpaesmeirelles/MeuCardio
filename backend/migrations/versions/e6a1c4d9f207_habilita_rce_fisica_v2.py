"""Habilita Receita de Controle Especial física no modelo Anvisa V2.

Revision ID: e6a1c4d9f207
Revises: f91c2b7e4a60
Create Date: 2026-08-04
"""
from alembic import op
import sqlalchemy as sa

revision = "e6a1c4d9f207"
down_revision = "f91c2b7e4a60"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text("""
        UPDATE prescription_types
           SET ativo = TRUE,
               exige_numeracao_sncr = FALSE,
               endpoint_sncr = NULL,
               lote_min = NULL,
               lote_max = NULL,
               validade_dias = 30,
               vias = 2,
               exige_retencao = TRUE,
               destinacao_vias = ARRAY[
                   '1ª via - Retenção pela Farmácia',
                   '2ª via - Paciente'
               ]::varchar[],
               campos_obrigatorios = ARRAY[
                   'emitente', 'paciente_nome', 'paciente_documento',
                   'prescricao', 'data', 'assinatura'
               ]::varchar[]
         WHERE codigo = 'RCE'
    """))


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text("""
        UPDATE prescription_types
           SET ativo = FALSE,
               exige_numeracao_sncr = TRUE,
               endpoint_sncr = '/numeracoes/receita-especial-retencao',
               lote_min = 1000,
               lote_max = 1000,
               validade_dias = NULL,
               destinacao_vias = ARRAY[]::varchar[],
               campos_obrigatorios = ARRAY[]::varchar[]
         WHERE codigo = 'RCE'
    """))
