# Architecture

The initial vertical slice is deliberately small:

```text
CSE unofficial public API -> MarketDataProvider -> Pydantic validation
                          -> MarketService -> PostgreSQL time-series tables
                          -> FastAPI normalized read API
```

Application code depends on `MarketDataProvider`, not endpoint URLs. `CSEPublicDataProvider` owns transport reliability and untrusted-response normalization. `MarketService` owns persistence. PostgreSQL uniqueness constraints make repeated observations idempotent, and compound indexes support symbol/index time-range access.

Later phases will add database and mock providers, scheduled collection, Redis response caching, daily aggregation, analysis, deterministic strategies, mandatory risk review, backtesting, and paper execution. Live execution remains disabled. No ATrad adapter or account automation is present.

## Safety invariants

- Public CSE endpoints provide market data only.
- Strategy output will be a signal, never an executable order.
- Future execution must pass through the risk manager.
- `LIVE_AUTO` is not implemented and cannot be enabled by configuration.
- ATrad support requires official API, authentication, permission, and sandbox documentation.

