"""market data tables"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

market_state = sa.Enum("PRE_OPEN", "OPEN_AUCTION", "REGULAR_TRADING", "CLOSED", "UNKNOWN", name="marketstate")

def upgrade():
    op.create_table("market_status", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False), sa.Column("state", market_state, nullable=False), sa.Column("source", sa.String(32), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_market_status_observed_at", "market_status", ["observed_at"])
    op.create_table("market_quotes", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("symbol", sa.String(32), nullable=False), sa.Column("company_name", sa.String(256)), sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False), sa.Column("last_price", sa.Numeric(18,4), nullable=False), sa.Column("open", sa.Numeric(18,4)), sa.Column("high", sa.Numeric(18,4)), sa.Column("low", sa.Numeric(18,4)), sa.Column("previous_close", sa.Numeric(18,4)), sa.Column("change", sa.Numeric(18,4)), sa.Column("change_percentage", sa.Numeric(12,4)), sa.Column("volume", sa.Integer()), sa.Column("turnover", sa.Numeric(24,4)), sa.Column("trades", sa.Integer()), sa.Column("source", sa.String(32), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("symbol", "observed_at"))
    op.create_index("ix_quote_symbol_time", "market_quotes", ["symbol", "observed_at"])
    op.create_table("index_prices", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("index_code", sa.String(16), nullable=False), sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False), sa.Column("value", sa.Numeric(18,4), nullable=False), sa.Column("change", sa.Numeric(18,4)), sa.Column("change_percentage", sa.Numeric(12,4)), sa.Column("source", sa.String(32), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("index_code", "observed_at"))
    op.create_index("ix_index_code_time", "index_prices", ["index_code", "observed_at"])

def downgrade():
    op.drop_table("index_prices"); op.drop_table("market_quotes"); op.drop_table("market_status"); market_state.drop(op.get_bind())
