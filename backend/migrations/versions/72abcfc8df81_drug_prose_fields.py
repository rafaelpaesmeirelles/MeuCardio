"""drugs.duration_of_action_source e drugs.drug_class: varchar apertado -> Text

Achado ao reproduzir localmente o incidente de deploy de 11/08/2026
(issue #52, nova fase — depois de corrigir `TypeError: 'review_note' is an
invalid keyword argument for Drug`, o mesmo `reconcile_content
--publish-reviewed` rodado contra o conteúdo real do RC quebrou de novo,
desta vez com `StringDataRightTruncation`):

- `duration_of_action_source` (`String(500)`) recebe texto de citação
  completa (laboratório, número de registro MS, URL da bula, data de
  consulta) — natureza de prosa/referência, não rótulo curto. Dois
  registros reais do RC excedem 500 caracteres (530 e 728).
- `drug_class` (`String(120)`) já é descrito no próprio histórico do
  projeto como "cabeçalho em prosa" (ex.: "Betabloqueador não seletivo com
  atividade alfa-1 bloqueadora adicional"), não um rótulo fixo — um
  registro de combinação de dose fixa passa de 120 caracteres (143).

Os dois campos guardam texto de referência/descrição, igual à maioria dos
demais campos de `Drug` (já `Text`, sem limite) — a diferença de tipo era
inconsistência de origem, não intenção de esquema. Corrigido para `Text`
nos dois, sem limite artificial que a régua de citação completa do projeto
("nada fabricado, fonte real e verificável") vai voltar a estourar.

Mesmo padrão de f2b8c41d7a93 (audit_logs.entity_id): idempotente, e o
downgrade é no-op de propósito — encurtar de volta truncaria conteúdo já
gravado.

Revision ID: 72abcfc8df81
Revises: 5a786cb55611
Create Date: 2026-08-11 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '72abcfc8df81'
down_revision = '5a786cb55611'
branch_labels = None
depends_on = None

# nome do campo -> nullable real do modelo (Drug.duration_of_action_source
# é opcional; Drug.drug_class não é) — precisa bater exatamente, senão o
# ALTER TYPE do Alembic reafirmaria a nullability errada por engano.
_CAMPOS = {"duration_of_action_source": True, "drug_class": False}


def upgrade() -> None:
    colunas = {c["name"]: c for c in sa.inspect(op.get_bind()).get_columns("drugs")}
    for campo, nullable in _CAMPOS.items():
        atual = colunas.get(campo)
        if atual is not None and not isinstance(atual["type"], sa.Text):
            op.alter_column("drugs", campo, type_=sa.Text(), existing_nullable=nullable)


def downgrade() -> None:
    # Reduzir de volta a varchar truncaria conteúdo já gravado que hoje
    # excede o limite antigo — no-op de propósito, mesmo padrão de
    # f2b8c41d7a93.
    pass
