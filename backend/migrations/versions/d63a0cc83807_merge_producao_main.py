"""Unifica a cadeia histórica da produção com a cadeia certificada da main.

Revision ID: d63a0cc83807
Revises: a4c8e1f2b703, b3f8a1d92e64
Create Date: 2026-08-04
"""

from collections.abc import Sequence

revision: str = "d63a0cc83807"
down_revision: str | Sequence[str] | None = (
    "a4c8e1f2b703",
    "b3f8a1d92e64",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Merge de histórico; nenhuma alteração adicional de schema."""
    pass


def downgrade() -> None:
    """Remove somente o marco de merge."""
    pass
