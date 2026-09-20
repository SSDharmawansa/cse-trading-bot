# CSE public market-data provider

## Status and boundaries

This integration is based on the community-maintained [CSE API documentation](https://github.com/GH0STH4CKER/Colombo-Stock-Exchange-CSE-API-Documentation). It is unofficial, unsupported, and may change without notice. It is used **only for public market data**. It is not an order API and must never be used to submit a real trade.

The upstream documentation says the base URL is `https://www.cse.lk/api/` and that the endpoints below use form-encoded `POST` requests. On 20 September 2026, requests from the development environment were blocked by its outbound proxy (`403 Forbidden` while creating the HTTPS tunnel), so live response bodies could not be responsibly asserted. The provider consequently accepts known field aliases, treats absent required values as validation failures, and reports schema failure rather than inventing data.

## Documented endpoint inventory

| Endpoint | Purpose | Request data | Implemented now |
|---|---|---|---|
| `marketStatus` | Exchange state | none | yes |
| `todaySharePrice` | Current security quotes | none | yes |
| `aspiData` | ASPI observations | none | yes |
| `snpData` | S&P SL20 observations | none | yes |
| `marketSummery` | Market totals | none | later |
| `tradeSummary` / `detailedTrades` | Trade summaries | none | later |
| `companyInfoSummery` | Security/company details | `symbol` | later |
| `chartData` | Chart series | `symbol`, `chartId`, `period` | later |
| `companyChartDataByStock` | Company chart series | `stockId`, `period=1` | later |
| `allSectors` | Sector data | none | later |
| `topGainers`, `topLooses`, `mostActiveTrades` | Ranked securities | none | later |
| `approvedAnnouncement`, `getFinancialAnnouncement` | Announcements | none | later |
| `getNewListingsRelatedNoticesAnnouncements`, `getNonComplianceAnnouncements` | Regulatory notices | none | later |
| `circularAnnouncement`, `directiveAnnouncement` | Circulars/directives | none | later |

## Normalization and failure behavior

Responses are interpreted defensively because the upstream repository documents only one `companyInfoSummery` example, not stable schemas for every endpoint. Unknown fields are ignored. A quote requires a symbol and a strictly positive last price; invalid individual rows are skipped. A non-empty response containing no valid quote rows is treated as a possible schema change. Index responses require a numeric value. Unavailable optional fields remain `null`.

Each response receives a UTC fetch timestamp; this is explicitly not claimed to be the exchange event time. Requests have configurable timeout, serialized throttling, bounded exponential backoff with jitter, and health accounting. API routes return HTTP 503 with `MARKET DATA OFFLINE` when fresh upstream data cannot be normalized. No automated signals exist in this phase, so stale data cannot result in a trade.

