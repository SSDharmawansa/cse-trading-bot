import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import Base, TimestampMixin


class MarketState(str, enum.Enum):
    PRE_OPEN = "PRE_OPEN"
    OPEN_AUCTION = "OPEN_AUCTION"
    REGULAR_TRADING = "REGULAR_TRADING"
    CLOSED = "CLOSED"
    UNKNOWN = "UNKNOWN"


class MarketStatusRecord(TimestampMixin, Base):
    __tablename__ = "market_status"
    id: Mapped[int] = mapped_column(primary_key=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    state: Mapped[MarketState] = mapped_column(Enum(MarketState))
    source: Mapped[str] = mapped_column(String(32), default="cse_public")


class MarketQuote(TimestampMixin, Base):
    __tablename__ = "market_quotes"
    __table_args__ = (UniqueConstraint("symbol", "observed_at"), Index("ix_quote_symbol_time", "symbol", "observed_at"))
    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    company_name: Mapped[str | None] = mapped_column(String(256))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    last_price: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    open: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    high: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    low: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    previous_close: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    change: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    change_percentage: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    volume: Mapped[int | None]
    turnover: Mapped[Decimal | None] = mapped_column(Numeric(24, 4))
    trades: Mapped[int | None]
    source: Mapped[str] = mapped_column(String(32), default="cse_public")


class IndexPrice(TimestampMixin, Base):
    __tablename__ = "index_prices"
    __table_args__ = (UniqueConstraint("index_code", "observed_at"), Index("ix_index_code_time", "index_code", "observed_at"))
    id: Mapped[int] = mapped_column(primary_key=True)
    index_code: Mapped[str] = mapped_column(String(16))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    value: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    change: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    change_percentage: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    source: Mapped[str] = mapped_column(String(32), default="cse_public")

