"""4 colunas varchar apertadas -> Text (achadas na certificação da RC)

Achado na certificação da Release Candidate `release/corvia-launch-rc-2026-08-12`
(12/08/2026), rodando `test_reconcile_content_full_run.py` — o mesmo teste de
regressão do incidente de 11/08/2026 (issue #52, ver migração `72abcfc8df81`) —
contra o conteúdo real do RC. Uma varredura completa das 11 frentes JSON contra
os limites reais de coluna dos modelos correspondentes (em vez de descobrir uma
falha por rodada de reconcile) encontrou 4 colunas com o mesmo padrão —
`StringDataRightTruncation` em campo curto que na prática guarda prosa/citação
completa, exatamente a classe de erro que `72abcfc8df81` já documentou:

- `gallery_images.modality` (`String(40)`, categórico) — 2 registros usam
  descrição mais longa que a categoria fixa quando o exame não se encaixa
  exatamente numa das oito documentadas (ex.: "Monitorização Ambulatorial da
  Pressão Arterial (MAPA)", 53 caracteres).
- `scientific_studies.authors` (`String(300)`) — 3 registros de consenso
  multissocietário/comitê de diretriz listam autoria completa + sociedades
  por extenso, excedendo 300 caracteres (até 372).
- `discharge_checklists.condicao` (`String(200)`) — 1 registro de condição
  investigacional composta excede 200 caracteres (207).
- `emergency_protocols.gatilho` (`String(400)`) — 3 registros de quadro de
  emergência precisam de descrição mais longa que 400 caracteres para não
  perder precisão sob pressão (até 447).

Mesmo padrão de remediação já usado e documentado pelo projeto para esta
classe exata de erro (`72abcfc8df81`, drugs.duration_of_action_source e
drugs.drug_class): alargar a coluna para `Text` em vez de truncar/reescrever
o dado real, que já passou pela mesma régua de fonte verificável do resto
do acervo — a inconsistência de tipo era de origem, não de intenção de
esquema (campos vizinhos do mesmo modelo já são `Text` sem limite curto).

Idempotente; downgrade é no-op de propósito (reduzir de volta ao varchar
antigo truncaria os registros reais que hoje excedem o limite), mesmo
padrão de `72abcfc8df81`/`f2b8c41d7a93`.

Revision ID: f71q20260812
Revises: f70p20260812
Create Date: 2026-08-12
"""
from alembic import op
import sqlalchemy as sa

revision = "f71q20260812"
down_revision = "f70p20260812"
branch_labels = None
depends_on = None

# (tabela, coluna, nullable real do modelo) — precisa bater exatamente,
# senão o ALTER TYPE do Alembic reafirmaria a nullability errada por engano.
_ALVOS = [
    ("gallery_images", "modality", False),
    ("scientific_studies", "authors", True),
    ("discharge_checklists", "condicao", False),
    ("emergency_protocols", "gatilho", True),
]


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    for tabela, campo, nullable in _ALVOS:
        colunas = {c["name"]: c for c in inspector.get_columns(tabela)}
        atual = colunas.get(campo)
        if atual is not None and not isinstance(atual["type"], sa.Text):
            op.alter_column(tabela, campo, type_=sa.Text(), existing_nullable=nullable)


def downgrade() -> None:
    # Reduzir de volta ao varchar antigo truncaria os registros reais que
    # hoje excedem o limite — no-op de propósito, mesmo padrão de
    # 72abcfc8df81/f2b8c41d7a93.
    pass
