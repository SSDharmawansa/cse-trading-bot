from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.api.market import router as market_router
from backend.app.core.config import get_settings
from backend.app.market_data.providers.cse_public import CSEPublicDataProvider


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.provider = CSEPublicDataProvider(get_settings())
    yield
    await app.state.provider.close()


app = FastAPI(title=get_settings().app_name, version="0.1.0", lifespan=lifespan)
app.include_router(market_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

