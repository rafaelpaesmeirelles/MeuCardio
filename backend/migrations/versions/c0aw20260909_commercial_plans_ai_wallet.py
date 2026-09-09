"""Four commercial plans and durable prepaid AI balances.

Existing subscriptions retain their legacy contract; no billing activation.
"""
from alembic import op
import sqlalchemy as sa

revision = "c0aw20260909"
down_revision = "b9sx20260903"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("subscriptions", sa.Column("commercial_version", sa.String(32), nullable=False, server_default="legacy_v1"))
    op.add_column("subscriptions", sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True))
    op.add_column("subscriptions", sa.Column("ai_access_started_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("""
CREATE TABLE ai_wallet_accounts (
	id SERIAL NOT NULL,
	principal_key VARCHAR(120) NOT NULL,
	user_id INTEGER,
	budget_credit_micros BIGINT,
	paid_credit_micros BIGINT DEFAULT '0' NOT NULL,
	paid_spent_micros BIGINT DEFAULT '0' NOT NULL,
	paid_reserved_micros BIGINT DEFAULT '0' NOT NULL,
	billing_blocked BOOLEAN DEFAULT 'false' NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT ck_ai_wallet_paid_nonnegative CHECK (paid_spent_micros >= 0 AND paid_reserved_micros >= 0),
	CONSTRAINT ck_ai_wallet_budget_nonnegative CHECK (budget_credit_micros IS NULL OR budget_credit_micros >= 0),
	UNIQUE (principal_key),
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
)
""")
    op.execute('CREATE INDEX ix_ai_wallet_accounts_user_id ON ai_wallet_accounts (user_id)')
    op.execute("""
CREATE TABLE ai_wallet_periods (
	id SERIAL NOT NULL,
	account_id INTEGER NOT NULL,
	period_start DATE NOT NULL,
	period_end DATE NOT NULL,
	currency VARCHAR(3) NOT NULL,
	pricing_version VARCHAR(80) NOT NULL,
	markup_bps BIGINT NOT NULL,
	grant_credit_micros BIGINT NOT NULL,
	cost_ceiling_micros BIGINT NOT NULL,
	spent_credit_micros BIGINT NOT NULL,
	reserved_credit_micros BIGINT NOT NULL,
	spent_cost_micros BIGINT NOT NULL,
	reserved_cost_micros BIGINT NOT NULL,
	paid_spent_credit_micros BIGINT NOT NULL,
	paid_reserved_credit_micros BIGINT NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_ai_wallet_account_period UNIQUE (account_id, period_start),
	CONSTRAINT ck_ai_wallet_period_limits CHECK (markup_bps >= 10000 AND grant_credit_micros >= 0 AND cost_ceiling_micros >= 0),
	CONSTRAINT ck_ai_wallet_period_balances CHECK (spent_credit_micros >= 0 AND reserved_credit_micros >= 0 AND spent_cost_micros >= 0 AND reserved_cost_micros >= 0 AND paid_spent_credit_micros >= 0 AND paid_reserved_credit_micros >= 0),
	FOREIGN KEY(account_id) REFERENCES ai_wallet_accounts (id) ON DELETE RESTRICT
)
""")
    op.execute('CREATE INDEX ix_ai_wallet_periods_account_id ON ai_wallet_periods (account_id)')
    op.execute("""
CREATE TABLE ai_wallet_operations (
	id SERIAL NOT NULL,
	account_id INTEGER NOT NULL,
	period_id INTEGER NOT NULL,
	operation_key VARCHAR(180) NOT NULL,
	feature VARCHAR(80) NOT NULL,
	cost_center VARCHAR(80),
	model_name VARCHAR(160) NOT NULL,
	pricing_version VARCHAR(80) NOT NULL,
	fingerprint VARCHAR(64) NOT NULL,
	state VARCHAR(30) NOT NULL,
	reserved_cost_micros BIGINT NOT NULL,
	reserved_credit_micros BIGINT NOT NULL,
	included_reserved_cost_micros BIGINT NOT NULL,
	included_reserved_credit_micros BIGINT NOT NULL,
	paid_reserved_credit_micros BIGINT NOT NULL,
	actual_cost_micros BIGINT,
	actual_credit_micros BIGINT,
	tokens_input BIGINT NOT NULL,
	tokens_output BIGINT NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	settled_at TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (id),
	CONSTRAINT uq_ai_wallet_operation_key UNIQUE (account_id, operation_key),
	CONSTRAINT ck_ai_wallet_operation_state CHECK (state IN ('reserved','unknown','settled','released','settled_overrun')),
	CONSTRAINT ck_ai_wallet_operation_reserved CHECK (reserved_cost_micros >= 0 AND reserved_credit_micros >= 0 AND included_reserved_cost_micros >= 0 AND included_reserved_credit_micros >= 0 AND paid_reserved_credit_micros >= 0),
	CONSTRAINT ck_ai_wallet_operation_actual CHECK ((actual_cost_micros IS NULL OR actual_cost_micros >= 0) AND (actual_credit_micros IS NULL OR actual_credit_micros >= 0) AND tokens_input >= 0 AND tokens_output >= 0),
	FOREIGN KEY(account_id) REFERENCES ai_wallet_accounts (id) ON DELETE RESTRICT,
	FOREIGN KEY(period_id) REFERENCES ai_wallet_periods (id) ON DELETE RESTRICT
)
""")
    op.execute('CREATE INDEX ix_ai_wallet_operations_account_id ON ai_wallet_operations (account_id)')
    op.execute('CREATE INDEX ix_ai_wallet_operations_period_id ON ai_wallet_operations (period_id)')
    op.execute("""
CREATE TABLE ai_wallet_credit_grants (
	id SERIAL NOT NULL,
	account_id INTEGER NOT NULL,
	reference VARCHAR(180) NOT NULL,
	original_reference VARCHAR(180),
	credit_micros BIGINT NOT NULL,
	currency VARCHAR(3) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT ck_ai_wallet_grant_nonzero CHECK (credit_micros <> 0),
	FOREIGN KEY(account_id) REFERENCES ai_wallet_accounts (id) ON DELETE RESTRICT,
	UNIQUE (reference)
)
""")
    op.execute('CREATE INDEX ix_ai_wallet_credit_grants_account_id ON ai_wallet_credit_grants (account_id)')
    op.execute('CREATE INDEX ix_ai_wallet_credit_grants_original_reference ON ai_wallet_credit_grants (original_reference)')
    op.execute("""
CREATE TABLE ai_credit_purchases (
	id VARCHAR(36) NOT NULL,
	user_id INTEGER,
	request_key VARCHAR(36) NOT NULL,
	amount_centavos INTEGER NOT NULL,
	currency VARCHAR(3) NOT NULL,
	status VARCHAR(24) NOT NULL,
	checkout_session_id VARCHAR(255),
	payment_intent_id VARCHAR(255),
	checkout_url VARCHAR(2048),
	reversed_centavos INTEGER NOT NULL,
	refunded_centavos INTEGER DEFAULT '0' NOT NULL,
	disputed_centavos INTEGER DEFAULT '0' NOT NULL,
	dispute_id VARCHAR(255),
	dispute_status VARCHAR(30),
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	paid_at TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (id),
	CONSTRAINT uq_ai_credit_purchase_request UNIQUE (user_id, request_key),
	CONSTRAINT ck_ai_purchase_amount CHECK (amount_centavos > 0),
	CONSTRAINT ck_ai_purchase_reversed CHECK (reversed_centavos >= 0 AND reversed_centavos <= amount_centavos),
	CONSTRAINT ck_ai_purchase_reversals CHECK (refunded_centavos >= 0 AND refunded_centavos <= amount_centavos AND disputed_centavos >= 0 AND disputed_centavos <= amount_centavos),
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL,
	UNIQUE (checkout_session_id),
	UNIQUE (payment_intent_id),
	UNIQUE (dispute_id)
)
""")
    op.execute('CREATE INDEX ix_ai_credit_purchases_user_id ON ai_credit_purchases (user_id)')

def downgrade():
    op.drop_table('ai_credit_purchases')
    op.drop_table('ai_wallet_credit_grants')
    op.drop_table('ai_wallet_operations')
    op.drop_table('ai_wallet_periods')
    op.drop_table('ai_wallet_accounts')
    op.drop_column("subscriptions", "ai_access_started_at")
    op.drop_column("subscriptions", "current_period_start")
    op.drop_column("subscriptions", "commercial_version")
