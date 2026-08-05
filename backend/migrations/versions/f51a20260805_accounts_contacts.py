"""Contas externas OAuth, contatos cifrados e cursores independentes.

Revision ID: f51a20260805
Revises: f50a20260805
Create Date: 2026-08-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "f51a20260805"
down_revision = "f50a20260805"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("calendar_integrations", sa.Column("contacts_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("calendar_integrations", sa.Column("external_account_id", sa.String(255), nullable=True))
    op.add_column("calendar_integrations", sa.Column("contacts_cursor_cipher", sa.LargeBinary(), nullable=True))
    op.add_column("calendar_integrations", sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True))
    op.create_unique_constraint(
        "uq_calendar_integration_external_account",
        "calendar_integrations",
        ["owner_id", "provider", "external_account_id"],
    )

    op.create_table(
        "external_contacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("integration_id", sa.Integer(), sa.ForeignKey("calendar_integrations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("external_id", sa.String(512), nullable=False),
        sa.Column("external_version", sa.String(512), nullable=True),
        sa.Column("display_name_cipher", sa.LargeBinary(), nullable=True),
        sa.Column("emails_cipher", sa.LargeBinary(), nullable=True),
        sa.Column("phones_cipher", sa.LargeBinary(), nullable=True),
        sa.Column("organization_cipher", sa.LargeBinary(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("external_updated_at", sa.String(80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("integration_id", "external_id", name="uq_external_contact_provider_id"),
    )
    op.create_index("ix_external_contacts_owner_id", "external_contacts", ["owner_id"])
    op.create_index("ix_external_contacts_integration_id", "external_contacts", ["integration_id"])
    op.create_index("ix_external_contacts_deleted", "external_contacts", ["deleted"])

    op.create_table(
        "integration_oauth_states",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("state_digest", sa.String(64), nullable=False),
        sa.Column("code_verifier_cipher", sa.LargeBinary(), nullable=False),
        sa.Column("request_data", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_integration_oauth_states_owner_id", "integration_oauth_states", ["owner_id"])
    op.create_index("ix_integration_oauth_states_provider", "integration_oauth_states", ["provider"])
    op.create_index("ix_integration_oauth_states_state_digest", "integration_oauth_states", ["state_digest"], unique=True)
    op.create_index("ix_integration_oauth_states_expires_at", "integration_oauth_states", ["expires_at"])


def downgrade() -> None:
    op.drop_table("integration_oauth_states")
    op.drop_table("external_contacts")
    op.drop_constraint(
        "uq_calendar_integration_external_account", "calendar_integrations", type_="unique"
    )
    op.drop_column("calendar_integrations", "revoked_at")
    op.drop_column("calendar_integrations", "contacts_cursor_cipher")
    op.drop_column("calendar_integrations", "external_account_id")
    op.drop_column("calendar_integrations", "contacts_enabled")
