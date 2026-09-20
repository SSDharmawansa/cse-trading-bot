from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.market_data.providers.base import MarketDataProvider
from backend.app.market_data.schemas import IndexSnapshot, MarketStatus, Quote
from backend.app.models.market import IndexPrice, MarketQuote, MarketStatusRecord


class MarketService:
    def __init__(self, provider: MarketDataProvider):
        self.provider = provider

    async def refresh(self, session: AsyncSession) -> tuple[MarketStatus, list[Quote], list[IndexSnapshot]]:
        status = await self.provider.get_market_status()
        quotes = await self.provider.get_all_quotes()
        indices = [await self.provider.get_aspi(), await self.provider.get_sp_sl20()]
        session.add(MarketStatusRecord(observed_at=status.data_timestamp, state=status.state, source=status.source))
        if quotes:
            values = [q.model_dump() | {"observed_at": q.timestamp} for q in quotes]
            for value in values:
                value.pop("timestamp")
            statement = insert(MarketQuote).values(values).on_conflict_do_nothing(index_elements=["symbol", "observed_at"])
            await session.execute(statement)
        for item in indices:
            statement = insert(IndexPrice).values(
                index_code=item.index_code, observed_at=item.timestamp, value=item.value,
                change=item.change, change_percentage=item.change_percentage, source=item.source,
            ).on_conflict_do_nothing(index_elements=["index_code", "observed_at"])
            await session.execute(statement)
        await session.commit()
        return status, quotes, indices

