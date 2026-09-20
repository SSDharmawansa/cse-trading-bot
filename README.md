# CSE Trading Assistant — foundation

Production-oriented Phase 1/2 foundation for an explainable Colombo Stock Exchange research and paper-trading platform. It currently provides a defensive unofficial CSE market-data client, normalized FastAPI routes, and PostgreSQL storage models/migration for market state, quotes, ASPI, and S&P SL20.

> **Important:** The CSE source is unofficial and can change. It is market-data-only. This software does not place real orders, does not connect to ATrad, does not store broker credentials, and makes no promise of returns. Verify all information before manually trading.

## Quick start with Docker

1. Copy `.env.example` to `.env` and replace the example database password.
2. Run `docker compose up --build`.
3. Open `http://localhost:8000/docs` or check `curl http://localhost:8000/health`.
4. Stop everything with `docker compose down`; add `-v` only when you deliberately want to erase local data.
5. Follow logs with `docker compose logs -f backend`.

Compose starts PostgreSQL, Redis, applies Alembic migrations, and then launches FastAPI. Live trading is hard-disabled and there is no automated paper-trading worker in this phase.

## Local development

Requires Python 3.12+, PostgreSQL 16+, and Redis 7+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
cp .env.example .env                # edit localhost credentials
alembic upgrade head                # initialize/update the database
uvicorn backend.app.main:app --reload
pytest
```

Normalized endpoints are:

- `GET /health`
- `GET /api/v1/market/status`
- `GET /api/v1/market/quotes`
- `GET /api/v1/market/indices`
- `GET /api/v1/market/provider-health`

The persistence service is ready for a scheduler/collector in the next increment; collection is not misleadingly advertised as automated yet. See [provider findings](CSE_DATA_PROVIDER.md) and [architecture](ARCHITECTURE.md).

## Configuration and safety

All settings use the `CSE_` prefix. Useful controls include request timeout, retry count, minimum request interval, database/Redis URLs, and stale threshold; see `.env.example`. Keep `.env` out of Git. `CSE_LIVE_ENABLED=false` must remain false. The current release supports analysis infrastructure only; paper automation, risk settings, and a frontend arrive in later phases and therefore cannot accidentally be started here.
