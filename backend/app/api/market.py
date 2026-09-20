from fastapi import APIRouter, Depends, HTTPException, Request

from backend.app.market_data.providers.cse_public import CSEPublicDataProvider, ProviderUnavailable
from backend.app.market_data.schemas import IndexSnapshot, MarketStatus, ProviderHealth, Quote

router = APIRouter(prefix="/api/v1/market", tags=["market"])


def provider(request: Request) -> CSEPublicDataProvider:
    return request.app.state.provider


@router.get("/status", response_model=MarketStatus)
async def market_status(source: CSEPublicDataProvider = Depends(provider)) -> MarketStatus:
    try:
        return await source.get_market_status()
    except ProviderUnavailable as exc:
        raise HTTPException(503, "MARKET DATA OFFLINE") from exc


@router.get("/quotes", response_model=list[Quote])
async def quotes(source: CSEPublicDataProvider = Depends(provider)) -> list[Quote]:
    try:
        return await source.get_all_quotes()
    except ProviderUnavailable as exc:
        raise HTTPException(503, "MARKET DATA OFFLINE") from exc


@router.get("/indices", response_model=list[IndexSnapshot])
async def indices(source: CSEPublicDataProvider = Depends(provider)) -> list[IndexSnapshot]:
    try:
        return [await source.get_aspi(), await source.get_sp_sl20()]
    except ProviderUnavailable as exc:
        raise HTTPException(503, "MARKET DATA OFFLINE") from exc


@router.get("/provider-health", response_model=ProviderHealth)
async def provider_health(source: CSEPublicDataProvider = Depends(provider)) -> ProviderHealth:
    return source.health

