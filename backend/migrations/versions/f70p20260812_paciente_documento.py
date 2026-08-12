"""Cadastro de paciente reutilizável entre documentos (12/08/2026).

Tabela nova `patient_profiles` — nome, CPF, telefone, e-mail e endereço
cifrados em repouso (mesmo cofre AES-256-GCM já usado em
`prescription_recipients`), nascimento/sexo em claro (mesmo padrão de
`patients.birth_date`/`patients.sex` no round). Deliberadamente separada
de `patients` (round hospitalar, anonimizado por decisão de 29/07/2026) —
ver `app/models/patient_profile.py`.

`generated_documents` ganha `patient_profile_id` (ponteiro de conveniência,
`ON DELETE SET NULL` — apagar o cadastro nunca apaga nem invalida documento
já emitido) e `patient_snapshot_cifrado` (o dado do paciente EFETIVAMENTE
usado na emissão, congelado — nunca reconstruído a partir do estado atual
de `PatientProfile`).

Revision ID: f70p20260812
Revises: 66717ca01f2d
Create Date: 2026-08-12
"""

from alembic import op
import sqlalchemy as sa

revision = "f70p20260812"
down_revision = "66717ca01f2d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "patient_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("full_name_cifrado", sa.LargeBinary(), nullable=False),
        sa.Column("cpf_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("sex", sa.String(length=1), nullable=True),
        sa.Column("phone_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("email_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("endereco_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_patient_profiles_owner_id", "patient_profiles", ["owner_id"])

    op.add_column(
        "generated_documents",
        sa.Column(
            "patient_profile_id", sa.Integer(),
            sa.ForeignKey("patient_profiles.id", ondelete="SET NULL"), nullable=True,
        ),
    )
    op.create_index(
        "ix_generated_documents_patient_profile_id", "generated_documents", ["patient_profile_id"],
    )
    op.add_column(
        "generated_documents",
        sa.Column("patient_snapshot_cifrado", sa.LargeBinary(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("generated_documents", "patient_snapshot_cifrado")
    op.drop_index("ix_generated_documents_patient_profile_id", table_name="generated_documents")
    op.drop_column("generated_documents", "patient_profile_id")
    op.drop_table("patient_profiles")
