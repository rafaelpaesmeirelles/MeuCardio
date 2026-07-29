"""`prescriptions.patient_id` passa a aceitar nulo (Tarefa 27).

O receituário tem destinatário próprio, cifrado, em `prescription_recipients` —
decisão do Rafael em 29/07/2026 para manter o `Patient` do round anonimizado.
Exigir um paciente de round para emitir receita obrigaria a criar um registro de
internação para um paciente de ambulatório, o que é dado errado no lugar errado.

As demais tabelas de documento clínico (`clinical_documents`, `appointments`) já
tratam `patient_id` como opcional; esta era a exceção, e era acidental.

Idempotente: confere o catálogo antes de alterar.

Revision ID: d8e42c91f3a7
Revises: c7d31f8a45b2
"""

import sqlalchemy as sa
from alembic import op

revision = "d8e42c91f3a7"
down_revision = "c7d31f8a45b2"
branch_labels = None
depends_on = None


def _e_anulavel() -> bool:
    cols = sa.inspect(op.get_bind()).get_columns("prescriptions")
    for c in cols:
        if c["name"] == "patient_id":
            return bool(c.get("nullable"))
    return False


def upgrade() -> None:
    if not _e_anulavel():
        op.alter_column("prescriptions", "patient_id",
                        existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    # Sem volta automática: reverter exigiria inventar um paciente para as
    # receitas criadas sem ele, e apagar receita para satisfazer uma constraint
    # é pior que a constraint.
    pass
