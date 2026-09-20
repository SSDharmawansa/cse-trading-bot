from datetime import UTC, datetime, timedelta

import httpx
import pytest

from backend.app.core.config import Settings
from backend.app.market_data.providers.cse_public import CSEPublicDataProvider, ProviderUnavailable
from backend.app.models.market import MarketState


def settings(**changes):
    return Settings(provider_max_retries=changes.get("retries", 1), provider_min_interval_seconds=0)


@pytest.mark.asyncio
async def test_defensively_parses_market_and_quotes():
    async def handler(request: httpx.Request):
        if request.url.path.endswith("marketStatus"):
            return httpx.Response(200, json={"marketStatus": "Open"})
        return httpx.Response(200, json={"reqTradeSummery": [{"symbol": " comb.n0000 ", "lastTradedPrice": "125.50", "sharevolume": 1000, "unexpected": True}, {"broken": True}]})

    client = httpx.AsyncClient(base_url="https://example.test/api/", transport=httpx.MockTransport(handler))
    provider = CSEPublicDataProvider(settings(), client)
    assert (await provider.get_market_status()).state is MarketState.REGULAR_TRADING
    quotes = await provider.get_all_quotes()
    assert len(quotes) == 1
    assert quotes[0].symbol == "COMB.N0000"
    assert quotes[0].volume == 1000


@pytest.mark.asyncio
async def test_schema_change_is_not_silently_accepted():
    client = httpx.AsyncClient(base_url="https://example.test/api/", transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"unknown": []})))
    provider = CSEPublicDataProvider(settings(), client)
    with pytest.raises(ProviderUnavailable, match="schema"):
        await provider.get_all_quotes()


@pytest.mark.asyncio
async def test_retries_and_marks_provider_offline():
    attempts = 0
    async def handler(_: httpx.Request):
        nonlocal attempts
        attempts += 1
        return httpx.Response(503)
    client = httpx.AsyncClient(base_url="https://example.test/api/", transport=httpx.MockTransport(handler))
    provider = CSEPublicDataProvider(settings(retries=2), client)
    with pytest.raises(ProviderUnavailable):
        await provider.get_market_status()
    assert attempts == 2
    assert provider.health.status == "OFFLINE"


def test_stale_data_detection():
    provider = CSEPublicDataProvider(settings())
    provider._last_success = datetime.now(UTC) - timedelta(seconds=301)
    assert provider.health.status == "STALE"
