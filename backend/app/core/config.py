from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="CSE_", extra="ignore")

    app_name: str = "CSE Trading Assistant"
    database_url: str = "postgresql+asyncpg://cse:cse@postgres:5432/cse"
    redis_url: str = "redis://redis:6379/0"
    cse_base_url: str = "https://www.cse.lk/api/"
    provider_timeout_seconds: float = Field(10, gt=0)
    provider_max_retries: int = Field(3, ge=1, le=10)
    provider_min_interval_seconds: float = Field(1, ge=0)
    stale_after_seconds: int = Field(300, gt=0)
    live_enabled: bool = False
    paper_enabled: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()

