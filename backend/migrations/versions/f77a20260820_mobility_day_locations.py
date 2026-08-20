"""Origem inicial e destino final do deslocamento diário.

Revision ID: f77a20260820
Revises: f76a20260819
Create Date: 2026-08-20
"""

from alembic import op
import sqlalchemy as sa


revision = "f77a20260820"
down_revision = "f76a20260819"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("mobility_preferences")}
    if "day_start_origin_mode" not in columns:
        op.add_column(
            "mobility_preferences",
            sa.Column(
                "day_start_origin_mode", sa.String(length=30), nullable=False,
                server_default="current_location",
            ),
        )
    if "day_start_location_id" not in columns:
        op.add_column(
            "mobility_preferences",
            sa.Column(
                "day_start_location_id", sa.Integer(),
                sa.ForeignKey("calendar_locations.id", ondelete="SET NULL"), nullable=True,
            ),
        )
    if "day_end_destination_location_id" not in columns:
        op.add_column(
            "mobility_preferences",
            sa.Column(
                "day_end_destination_location_id", sa.Integer(),
                sa.ForeignKey("calendar_locations.id", ondelete="SET NULL"), nullable=True,
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("mobility_preferences")}
    if "day_end_destination_location_id" in columns:
        op.drop_column("mobility_preferences", "day_end_destination_location_id")
    if "day_start_location_id" in columns:
        op.drop_column("mobility_preferences", "day_start_location_id")
    if "day_start_origin_mode" in columns:
        op.drop_column("mobility_preferences", "day_start_origin_mode")
