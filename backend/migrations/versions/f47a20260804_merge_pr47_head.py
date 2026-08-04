"""Unifica a revisão operacional existente com os campos do PR47.

Revision ID: f47a20260804
Revises: e6a1c4d9f207, e47c20260804
Create Date: 2026-08-04
"""

revision = "f47a20260804"
down_revision = ("e6a1c4d9f207", "e47c20260804")
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Merge revision: todas as alterações vivem nas duas revisões-pai."""


def downgrade() -> None:
    """Volta a expor as duas cabeças sem desfazer seus esquemas."""
