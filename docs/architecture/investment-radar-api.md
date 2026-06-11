# Investment Radar — REST API Contract

> **Status:** Architecture (MVP) — authoritative contract for INVES-20, INVES-21, INVES-22  
> **Base URL (local):** `http://localhost:8000`  
> **API prefix:** `/api/v1`  
> **Auth:** none (single-user local demo; see ADR-008)

## Conventions

### Asset ID format

Canonical identifier: `{class}:{symbol}` (lowercase class, uppercase symbol).

| Class   | Pattern        | Example        |
|---------|----------------|----------------|
| `stock` | `stock:{TICKER}` | `stock:AAPL` |
| `crypto`| `crypto:{SYMBOL}` | `crypto:BTC` |

- Tickers use provider-native symbols (US equities: Finnhub; crypto: CoinGecko id or symbol).
- IDs are stable across search, quotes, watchlist, and portfolio.
- Invalid format → `400 VALIDATION_ERROR`.

### Source metadata

Any response that includes market prices **must** expose data provenance:

| Field    | Type   | Values              | Description                          |
|----------|--------|---------------------|--------------------------------------|
| `source` | string | `live` \| `fallback` | Whether price came from provider or bundled catalog |

Nested under `quote` objects or top-level on history/search hits where applicable.

### Timestamps

- All datetimes: ISO 8601 UTC (`2026-05-27T14:30:00Z`).
- History buckets: `timestamp` per `PricePoint`.

### Pagination

List endpoints accept optional query params:

| Param  | Default | Max |
|--------|---------|-----|
| `limit`| 20      | 100 |
| `offset`| 0      | —   |

Response wrapper for paginated lists:

```json
{
  "items": [],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

### Error responses

HTTP status reflects failure class. Body shape (all endpoints):

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Human-readable summary",
    "details": {}
  }
}
```

| HTTP | `code`              | When                                      |
|------|---------------------|-------------------------------------------|
| 400  | `VALIDATION_ERROR`  | Bad query, invalid asset ID, bad body     |
| 404  | `NOT_FOUND`         | Unknown asset, watchlist item, transaction|
| 422  | `UNPROCESSABLE`     | Semantically invalid (e.g. sell > holdings)|
| 502  | `PROVIDER_ERROR`    | All live providers failed; no fallback    |
| 503  | `SERVICE_UNAVAILABLE`| Backend not ready / DB unavailable       |

---

## Shared types

### Asset

| Field         | Type   | Required | Notes                                      |
|---------------|--------|----------|--------------------------------------------|
| `id`          | string | yes      | `{class}:{symbol}`                         |
| `class`       | string | yes      | `stock` \| `crypto`                        |
| `symbol`      | string | yes      | Display ticker                             |
| `name`        | string | yes      | Full name                                  |
| `currency`    | string | yes      | ISO 4217 (e.g. `USD`)                      |
| `exchange`    | string | no       | e.g. `NASDAQ`, `CRYPTO`                    |
| `source`      | string | no       | `live` \| `fallback` on search/discovery   |

### Quote

| Field           | Type   | Required | Notes                                |
|-----------------|--------|----------|--------------------------------------|
| `asset_id`      | string | yes      | Canonical ID                         |
| `price`         | number | yes      | Last price                           |
| `change`        | number | no       | Absolute change vs previous close    |
| `change_percent`| number | no       | Percent change                       |
| `currency`      | string | yes      | Quote currency                       |
| `timestamp`     | string | yes      | Quote time (ISO 8601)                |
| `source`        | string | yes      | `live` \| `fallback`                 |

### PricePoint

| Field       | Type   | Required | Notes                    |
|-------------|--------|----------|--------------------------|
| `timestamp` | string | yes      | Bucket open time (UTC)   |
| `open`      | number | yes      |                          |
| `high`      | number | yes      |                          |
| `low`       | number | yes      |                          |
| `close`     | number | yes      |                          |
| `volume`    | number | no       | May be null for crypto   |

### WatchlistItem

| Field        | Type   | Required | Notes                          |
|--------------|--------|----------|--------------------------------|
| `asset_id`   | string | yes      | Canonical ID                   |
| `asset`      | Asset  | no       | Embedded on GET list           |
| `quote`      | Quote  | no       | Embedded latest quote on GET   |
| `notes`      | string | no       | User note (max 500 chars)      |
| `sort_order` | int    | no       | Display order (default 0)      |
| `added_at`   | string | yes      | ISO 8601                       |

### Portfolio

| Field              | Type   | Required | Notes                         |
|--------------------|--------|----------|-------------------------------|
| `id`               | string | yes      | UUID; single default portfolio|
| `name`             | string | yes      | Default: `"My Portfolio"`   |
| `base_currency`    | string | yes      | Default: `USD`                |
| `cash_balance`     | number | yes      | Simulated cash (no real money)|
| `total_value`      | number | yes      | cash + holdings mark-to-market|
| `total_cost_basis` | number | yes      | Sum of buy costs minus sells  |
| `unrealized_pnl`   | number | yes      | `total_value - cost basis`    |
| `updated_at`       | string | yes      | ISO 8601                      |

### Holding

| Field            | Type   | Required | Notes                          |
|------------------|--------|----------|--------------------------------|
| `asset_id`       | string | yes      |                                |
| `asset`          | Asset  | no       | Embedded                       |
| `quantity`       | number | yes      | Units held (> 0)               |
| `avg_cost`       | number | yes      | Weighted average cost per unit |
| `market_price`   | number | yes      | Latest quote price             |
| `market_value`   | number | yes      | `quantity * market_price`      |
| `cost_basis`     | number | yes      | `quantity * avg_cost`          |
| `unrealized_pnl` | number | yes      | `market_value - cost_basis`    |
| `source`         | string | yes      | Quote `source` used for price  |

### Transaction

| Field        | Type   | Required | Notes                                      |
|--------------|--------|----------|--------------------------------------------|
| `id`         | string | yes      | UUID                                       |
| `type`       | string | yes      | `buy` \| `sell`                            |
| `asset_id`   | string | yes      |                                            |
| `quantity`   | number | yes      | > 0                                        |
| `price`      | number | yes      | Executed price (from quote at submit time) |
| `total`      | number | yes      | `quantity * price`                         |
| `source`     | string | yes      | Quote `source` at execution                |
| `executed_at`| string | yes      | ISO 8601                                   |
| `note`       | string | no       | Optional memo                              |

---

## Endpoints — Market data (INVES-20)

### `GET /api/v1/health`

Liveness for runbook and frontend boot.

**Response 200**

```json
{
  "status": "ok",
  "version": "0.1.0",
  "database": "ok"
}
```

---

### `GET /api/v1/assets/search`

Search/discover assets across live providers and fallback catalog.

**Query**

| Param   | Required | Description                          |
|---------|----------|--------------------------------------|
| `q`     | yes      | Min 1 char; matches symbol or name   |
| `class` | no       | `stock` \| `crypto` \| omit = both   |
| `limit` | no       | Default 20, max 50 for search        |

**Response 200**

```json
{
  "items": [
    {
      "id": "stock:AAPL",
      "class": "stock",
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "currency": "USD",
      "exchange": "NASDAQ",
      "source": "live"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

---

### `GET /api/v1/assets/{asset_id}`

Resolve metadata for one asset.

**Response 200:** single `Asset` object.

**Response 404:** `NOT_FOUND` if ID unknown in live + fallback.

---

### `GET /api/v1/quotes/{asset_id}`

Latest quote for one asset.

**Response 200**

```json
{
  "asset_id": "stock:AAPL",
  "price": 189.42,
  "change": -1.23,
  "change_percent": -0.65,
  "currency": "USD",
  "timestamp": "2026-05-27T20:00:00Z",
  "source": "live"
}
```

---

### `GET /api/v1/quotes`

Batch quotes.

**Query:** `ids` — comma-separated asset IDs (max 20).

**Response 200**

```json
{
  "items": [ { "...": "Quote fields" } ],
  "missing": ["stock:ZZZZ"]
}
```

---

### `GET /api/v1/history/{asset_id}`

OHLCV history for charts.

**Query**

| Param      | Required | Description                              |
|------------|----------|------------------------------------------|
| `interval` | no       | `1d` (default) \| `1h` (MVP: `1d` only)  |
| `from`     | no       | ISO date `YYYY-MM-DD`; default 90d ago   |
| `to`       | no       | ISO date; default today                  |

**Response 200**

```json
{
  "asset_id": "stock:AAPL",
  "interval": "1d",
  "source": "live",
  "points": [
    {
      "timestamp": "2026-05-26T00:00:00Z",
      "open": 190.1,
      "high": 191.0,
      "low": 188.5,
      "close": 189.42,
      "volume": 51234567
    }
  ]
}
```

When live history unavailable, backend may return fallback synthetic/static series with `source: "fallback"`.

---

## Endpoints — Projections (MarketPulse / INVES-32)

> **Canonical schema:** `app/shared/contracts/forecast.schema.json`  
> **TypeScript mirror:** `app/shared/types/forecast.ts` (import via `@shared` in frontend)

### `GET /api/v1/projections/{symbol}`

Single-asset price projection with technical indicators and confidence bands.

**Path**

| Param    | Description                          |
|----------|--------------------------------------|
| `symbol` | Provider-native symbol (e.g. `BTC`, `AAPL`) |

**Query**

| Param          | Required | Description                    |
|----------------|----------|--------------------------------|
| `horizon_days` | no       | Default `7`; range `1`–`90`    |

**Response 200 — `AssetProjection`**

| Field           | Type                    | Required | Notes                                      |
|-----------------|-------------------------|----------|--------------------------------------------|
| `asset_id`      | string                  | yes      | Uppercase symbol used for the request      |
| `horizon_days`  | integer                 | yes      | Projection horizon (matches query param)   |
| `current_price` | number                  | yes      | Latest price at projection time            |
| `indicators`    | `TechnicalIndicators`   | yes      | RSI, MACD, SMA, Bollinger from recent OHLCV |
| `scenarios`     | `ProjectionScenario[]` | yes     | At least one scenario (MVP: `linear_trend`) |
| `disclaimer`    | string                  | yes      | Non-advice disclaimer text                 |
| `meta`          | `SourceMeta`            | yes      | Provider provenance                        |

#### `TechnicalIndicators`

| Field              | Type   | Required | Notes                    |
|--------------------|--------|----------|--------------------------|
| `rsi_14`           | number | yes      | 14-period RSI            |
| `macd`             | number | yes      | MACD line                |
| `macd_signal`      | number | yes      | MACD signal line         |
| `sma_20`           | number | yes      | 20-period simple MA      |
| `sma_50`           | number | yes      | 50-period simple MA      |
| `bollinger_upper`  | number | yes      | Upper Bollinger band     |
| `bollinger_lower`  | number | yes      | Lower Bollinger band     |

#### `ProjectionScenario`

| Field        | Type                 | Required | Notes                                      |
|--------------|----------------------|----------|--------------------------------------------|
| `name`       | string               | yes      | Scenario id (e.g. `linear_trend`)          |
| `direction`  | string               | yes      | `bullish` \| `bearish` \| `neutral`       |
| `confidence` | number               | yes      | `0`–`1` inclusive                          |
| `points`     | `ProjectionPoint[]`  | yes      | One point per projected day                |

#### `ProjectionPoint`

| Field         | Type   | Required | Notes                          |
|---------------|--------|----------|--------------------------------|
| `timestamp`   | string | yes      | ISO 8601 UTC projected date    |
| `price`       | number | yes      | Projected price                |
| `lower_bound` | number | yes      | Lower confidence band          |
| `upper_bound` | number | yes      | Upper confidence band          |

#### `SourceMeta`

| Field         | Type           | Required | Notes                              |
|---------------|----------------|----------|------------------------------------|
| `source`      | string         | yes      | `mock` \| `live` \| `fallback`     |
| `provider`    | string         | yes      | Provider adapter name              |
| `fetched_at`  | string         | yes      | ISO 8601 UTC fetch time            |
| `latency_ms`  | number \| null | no       | Round-trip latency when available  |

**Example 200**

```json
{
  "asset_id": "BTC",
  "horizon_days": 7,
  "current_price": 65000.0,
  "indicators": {
    "rsi_14": 55.2,
    "macd": 120.5,
    "macd_signal": 108.45,
    "sma_20": 64200.0,
    "sma_50": 63100.0,
    "bollinger_upper": 66300.0,
    "bollinger_lower": 63700.0
  },
  "scenarios": [
    {
      "name": "linear_trend",
      "direction": "bullish",
      "confidence": 0.62,
      "points": [
        {
          "timestamp": "2026-05-29T12:00:00Z",
          "price": 65100.0,
          "lower_bound": 64500.0,
          "upper_bound": 65700.0
        }
      ]
    }
  ],
  "disclaimer": "Projections are illustrative only and based on a simple linear trend from recent price history. Not financial advice.",
  "meta": {
    "source": "mock",
    "provider": "mock",
    "fetched_at": "2026-05-28T12:00:00Z",
    "latency_ms": 1.0
  }
}
```

**Response 404:** unknown symbol.

**Response 501:** projection provider not configured.

---

## Endpoints — Watchlist (INVES-21)

Single implicit watchlist per local instance (no user ID in paths).

### `GET /api/v1/watchlist`

**Response 200**

```json
{
  "items": [
    {
      "asset_id": "crypto:BTC",
      "asset": { "...": "Asset" },
      "quote": { "...": "Quote" },
      "notes": "Core holding watch",
      "sort_order": 0,
      "added_at": "2026-05-27T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

---

### `POST /api/v1/watchlist/items`

Add asset to watchlist (idempotent: duplicate `asset_id` → `200` with existing item).

**Request body**

```json
{
  "asset_id": "stock:AAPL",
  "notes": "optional",
  "sort_order": 0
}
```

**Response 201:** created `WatchlistItem` (without embedded quote optional).

**Response 404:** `NOT_FOUND` if `asset_id` cannot be resolved.

---

### `PATCH /api/v1/watchlist/items/{asset_id}`

Update `notes` and/or `sort_order`.

**Request body:** partial `{ "notes": "...", "sort_order": 1 }`

**Response 200:** updated `WatchlistItem`.

---

### `DELETE /api/v1/watchlist/items/{asset_id}`

**Response 204:** removed.

**Response 404:** not on watchlist.

---

## Endpoints — Simulated portfolio (INVES-22)

> **Not real trading.** Transactions adjust local SQLite state and simulated cash only.

### `GET /api/v1/portfolio`

**Response 200:** `Portfolio` object.

---

### `GET /api/v1/portfolio/holdings`

**Response 200**

```json
{
  "items": [ { "...": "Holding" } ],
  "total": 2,
  "limit": 20,
  "offset": 0
}
```

---

### `GET /api/v1/portfolio/transactions`

**Query:** optional `asset_id`, `type`, `limit`, `offset`.

**Response 200**

```json
{
  "items": [ { "...": "Transaction" } ],
  "total": 5,
  "limit": 20,
  "offset": 0
}
```

---

### `POST /api/v1/portfolio/transactions`

Record simulated buy or sell at **current quote price** (server-side fetch).

**Request body**

```json
{
  "type": "buy",
  "asset_id": "stock:AAPL",
  "quantity": 10,
  "note": "Demo purchase"
}
```

**Validation**

- `buy`: `quantity * price` must not exceed `cash_balance` → else `422 UNPROCESSABLE`.
- `sell`: `quantity` must not exceed holding → else `422 UNPROCESSABLE`.
- `quantity` > 0.

**Response 201**

```json
{
  "transaction": { "...": "Transaction" },
  "portfolio": { "...": "Portfolio" },
  "holding": { "...": "Holding or null if fully sold" }
}
```

---

### `GET /api/v1/portfolio/summary`

Aggregated dashboard payload (convenience for frontend INVES-23).

**Response 200**

```json
{
  "portfolio": { "...": "Portfolio" },
  "holdings": [ { "...": "Holding" } ],
  "watchlist_count": 5,
  "top_movers": [ { "...": "Quote + asset metadata" } ]
}
```

---

## Cross-cutting implementation notes

| Topic | Decision |
|-------|----------|
| CORS | Allow `http://localhost:5173` (Vite default); see `.env` `CORS_ORIGINS` |
| OpenAPI | Auto-generated from FastAPI/Pydantic at `/api/v1/openapi.json` |
| DB tables | `watchlist_items`, `portfolio`, `holdings`, `transactions` (single row portfolio) |
| Initial cash | Seed `cash_balance: 100000.00` USD on first boot |
| Provider keys | Optional in `.env`; missing key → fallback catalog without failing search |

## Sub-task mapping

| Card     | Endpoints |
|----------|-----------|
| INVES-20 | `/health`, `/assets/*`, `/quotes/*`, `/history/*` |
| INVES-21 | `/watchlist/*` |
| INVES-22 | `/portfolio/*` |
| INVES-23 | Consumes all; no new backend routes required for MVP |
| INVES-24 | Documents base URL, env vars, `make`/uvicorn run |
| INVES-35 | Shared forecast schema + TS types (`app/shared/contracts/forecast.schema.json`) |

## References

- ADR-004 — FastAPI stack  
- ADR-005 — React + Vite frontend  
- ADR-006 — Market data providers  
- ADR-007 — SQLite persistence  
- ADR-008 — API conventions and auth deferral  
