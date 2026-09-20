from abc import ABC, abstractmethod

from backend.app.market_data.schemas import IndexSnapshot, MarketStatus, Quote


class MarketDataProvider(ABC):
    @abstractmethod
    async def get_market_status(self) -> MarketStatus: ...

    @abstractmethod
    async def get_all_quotes(self) -> list[Quote]: ...

    @abstractmethod
    async def get_aspi(self) -> IndexSnapshot: ...

    @abstractmethod
    async def get_sp_sl20(self) -> IndexSnapshot: ...

    async def close(self) -> None:
        return None

