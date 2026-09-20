import asyncio
import random
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import httpx

from backend.app.core.config import Settings
from backend.app.market_data.providers.base import MarketDataProvider
from backend.app.market_data.schemas import IndexSnapshot, MarketStatus, ProviderHealth, Quote, decimal_or_none, first
from backend.app.models.market import MarketState


class ProviderUnavailable(RuntimeError):
    pass


class CSEPublicDataProvider(MarketDataProvider):
    """Defensive client for the unsupported, market-data-only CSE web API."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self.settings = settings
        self.client = client or httpx.AsyncClient(base_url=settings.cse_base_url, timeout=settings.provider_timeout_seconds)
        self._owns_client = client is None
        self._lock = asyncio.Lock()
        self._last_request = 0.0
        self._last_success: datetime | None = None
        self._failures = 0
        self._message: str | None = None

    async def _request(self, endpoint: str, data: dict[str, Any] | None = None) -> Any:
        error: Exception | None = None
        for attempt in range(self.settings.provider_max_retries):
            try:
                async with self._lock:
                    now = asyncio.get_running_loop().time()
                    await asyncio.sleep(max(0, self.settings.provider_min_interval_seconds - (now - self._last_request)))
                    response = await self.client.post(endpoint, data=data or {}, headers={"Accept": "application/json"})
                    self._last_request = asyncio.get_running_loop().time()
                response.raise_for_status()
                payload = response.json()
                self._last_success, self._failures, self._message = datetime.now(UTC), 0, None
                return payload
            except (httpx.HTTPError, ValueError) as exc:
                error = exc
                self._failures += 1
                self._message = f"{type(exc).__name__}: provider request failed"
                if attempt + 1 < self.settings.provider_max_retries:
                    await asyncio.sleep((2**attempt) * 0.25 + random.uniform(0, 0.1))
        raise ProviderUnavailable(f"CSE endpoint {endpoint} unavailable after retries") from error

    @property
    def health(self) -> ProviderHealth:
        stale = bool(self._last_success and (datetime.now(UTC) - self._last_success).total_seconds() > self.settings.stale_after_seconds)
        status = "STALE" if stale else "HEALTHY" if self._failures == 0 and self._last_success else "OFFLINE" if self._failures >= self.settings.provider_max_retries else "DEGRADED"
        return ProviderHealth(status=status, last_success=self._last_success, consecutive_failures=self._failures, message=self._message)

    async def get_market_status(self) -> MarketStatus:
        payload = await self._request("marketStatus")
        data = payload if isinstance(payload, dict) else {}
        raw = str(first(data, "status", "marketStatus", "marketstatus") or "UNKNOWN")
        normalized = raw.upper().replace(" ", "_").replace("-", "_")
        aliases = {"OPEN": MarketState.REGULAR_TRADING, "REGULAR": MarketState.REGULAR_TRADING, "PREOPEN": MarketState.PRE_OPEN}
        state = aliases.get(normalized, MarketState._value2member_map_.get(normalized, MarketState.UNKNOWN))
        return MarketStatus(state=state, raw_status=raw, data_timestamp=datetime.now(UTC))

    async def get_all_quotes(self) -> list[Quote]:
        payload = await self._request("todaySharePrice")
        rows = payload if isinstance(payload, list) else first(payload, "reqTradeSummery", "todaySharePrice", "data") if isinstance(payload, dict) else []
        if not isinstance(rows, list):
            raise ProviderUnavailable("unexpected quote response schema")
        fetched_at = datetime.now(UTC)
        quotes = []
        for row in rows:
            if isinstance(row, dict):
                try:
                    quotes.append(Quote.from_untrusted(row, fetched_at))
                except ValueError:
                    continue
        if rows and not quotes:
            raise ProviderUnavailable("no valid quotes in response (possible schema change)")
        return quotes

    async def _index(self, endpoint: str, code: str) -> IndexSnapshot:
        payload = await self._request(endpoint)
        data = payload[-1] if isinstance(payload, list) and payload else payload
        if isinstance(data, dict):
            nested = first(data, "data", "indexData")
            if isinstance(nested, list) and nested:
                data = nested[-1]
        if not isinstance(data, dict):
            raise ProviderUnavailable(f"unexpected {code} response schema")
        value = decimal_or_none(first(data, "value", "indexValue", "close", "price"))
        if value is None:
            raise ProviderUnavailable(f"{code} value missing")
        return IndexSnapshot(index_code=code, timestamp=datetime.now(UTC), value=value,
            change=decimal_or_none(first(data, "change", "indexChange")),
            change_percentage=decimal_or_none(first(data, "changePercentage", "percentageChange")))

    async def get_aspi(self) -> IndexSnapshot:
        return await self._index("aspiData", "ASPI")

    async def get_sp_sl20(self) -> IndexSnapshot:
        return await self._index("snpData", "SPSL20")

    async def close(self) -> None:
        if self._owns_client:
            await self.client.aclose()
