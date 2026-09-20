from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from pydantic import BaseModel, Field, field_validator

from backend.app.models.market import MarketState


def first(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in data and data[key] not in (None, ""):
            return data[key]
    return None


def decimal_or_none(value: Any) -> Decimal | None:
    if value in (None, "", "-"):
        return None
    try:
        return Decimal(str(value).replace(",", ""))
    except (InvalidOperation, ValueError):
        return None


class MarketStatus(BaseModel):
    state: MarketState
    source: str = "cse_public"
    data_timestamp: datetime
    raw_status: str | None = None


class Quote(BaseModel):
    symbol: str
    company_name: str | None = None
    timestamp: datetime
    last_price: Decimal = Field(gt=0)
    open: Decimal | None = None
    high: Decimal | None = None
    low: Decimal | None = None
    previous_close: Decimal | None = None
    change: Decimal | None = None
    change_percentage: Decimal | None = None
    volume: int | None = Field(default=None, ge=0)
    turnover: Decimal | None = Field(default=None, ge=0)
    trades: int | None = Field(default=None, ge=0)
    source: str = "cse_public"

    @field_validator("symbol")
    @classmethod
    def valid_symbol(cls, value: str) -> str:
        value = value.strip().upper()
        if not value or len(value) > 32:
            raise ValueError("invalid symbol")
        return value

    @classmethod
    def from_untrusted(cls, data: dict[str, Any], fetched_at: datetime) -> "Quote":
        symbol = first(data, "symbol", "stockSymbol", "securityCode")
        price = decimal_or_none(first(data, "lastTradedPrice", "lastTradePrice", "price", "close"))
        if symbol is None or price is None:
            raise ValueError("quote lacks symbol or positive last price")
        return cls(
            symbol=str(symbol), company_name=first(data, "name", "companyName", "securityName"),
            timestamp=fetched_at, last_price=price,
            open=decimal_or_none(first(data, "open", "openPrice")),
            high=decimal_or_none(first(data, "high", "highPrice")), low=decimal_or_none(first(data, "low", "lowPrice")),
            previous_close=decimal_or_none(first(data, "previousClose", "previousClosingPrice")),
            change=decimal_or_none(first(data, "change", "priceChange")),
            change_percentage=decimal_or_none(first(data, "changePercentage", "percentageChange")),
            volume=first(data, "sharevolume", "volume", "tradeVolume"),
            turnover=decimal_or_none(first(data, "turnover", "tradeTurnover")), trades=first(data, "numberOfTrades", "trades"),
        )


class IndexSnapshot(BaseModel):
    index_code: str
    timestamp: datetime
    value: Decimal
    change: Decimal | None = None
    change_percentage: Decimal | None = None
    source: str = "cse_public"


class ProviderHealth(BaseModel):
    status: str
    last_success: datetime | None
    consecutive_failures: int
    message: str | None = None

