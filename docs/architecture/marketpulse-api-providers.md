# MarketPulse API Providers — Research & Comparison

MarketPulse uses a **provider pattern** (`MarketDataProvider`) so market data sources can be swapped via `MARKET_DATA_PROVIDER` without changing API routes or the frontend.

## Primary recommendation: Twelve Data

**Twelve Data** ([twelvedata.com](https://twelvedata.com)) is the recommended primary provider for a unified stocks + forex + crypto dashboard.

| Dimension | Twelve Data |
|-----------|-------------|
| Asset coverage | Stocks (global), ETFs, forex, crypto, indices, commodities |
| Free tier | ~800 API credits/day (plan-dependent); rate limits apply |
| Latency | REST ~100–300 ms typical; WebSocket on paid tiers |
| WebSocket | Yes (real-time quotes, paid plans) |
| Best for | Single-vendor MVP with consistent symbol schema across asset classes |

**Integration notes for MarketPulse**

- Map symbols consistently (`AAPL`, `BTC/USD`, `EUR/USD`).
- Use `/time_series` for OHLCV and `/quote` for snapshots.
- Cache responses server-side to respect daily credit limits.
- Stub implementation returns HTTP 501 until `TWELVE_DATA_API_KEY` is set.

---

## Alpha Vantage

**Alpha Vantage** ([alphavantage.co](https://www.alphavantage.co)) is strong for equities and technical indicators.

| Dimension | Alpha Vantage |
|-----------|---------------|
| Asset coverage | Stocks, forex, crypto (limited), commodities |
| Free tier | 25 requests/day (free key); 75/min on premium |
| Latency | REST; no native low-latency stream on free tier |
| WebSocket | No |
| Best for | Equity-heavy apps needing built-in technical indicators |

**Trade-offs:** Free tier is too small for a polling dashboard (MarketPulse refetches every 30s). Better as a secondary source for indicator enrichment or batch jobs.

---

## Finnhub

**Finnhub** ([finnhub.io](https://finnhub.io)) excels at US equities and company fundamentals.

| Dimension | Finnhub |
|-----------|---------|
| Asset coverage | US/global stocks, forex, crypto (limited), news |
| Free tier | 60 calls/minute |
| Latency | REST + WebSocket (free tier has socket limits) |
| WebSocket | Yes (trade/quote streams) |
| Best for | Stock watchlists, news sentiment, US-centric portfolios |

**Trade-offs:** Crypto coverage is narrower than dedicated crypto APIs. Pair with CoinGecko for digital assets.

---

## Polygon.io

**Polygon** ([polygon.io](https://polygon.io)) targets professional-grade US market data.

| Dimension | Polygon |
|-----------|---------|
| Asset coverage | US stocks, options, forex, crypto |
| Free tier | Limited/delayed on free; real-time on paid |
| Latency | Low on paid REST/WebSocket |
| WebSocket | Yes |
| Best for | Production US equities with strict latency SLAs |

**Trade-offs:** Free tier is not ideal for interactive dashboards; cost scales with usage.

---

## CoinGecko

**CoinGecko** ([coingecko.com](https://www.coingecko.com/en/api)) is the reference for crypto market aggregates.

| Dimension | CoinGecko |
|-----------|-----------|
| Asset coverage | 10k+ crypto assets, dominance, fear/greed proxies |
| Free tier | Demo plan ~10–30 calls/min (varies by endpoint) |
| Latency | REST; Pro plans improve limits |
| WebSocket | No (REST polling) |
| Best for | Crypto overview cards, dominance, altcoin search |

**Trade-offs:** No traditional equities. Use as crypto complement or for `MarketOverview` crypto-specific fields.

---

## Comparison matrix

| Provider | Stocks | Crypto | Forex | Free tier | WebSocket | Latency (typical) | Recommendation |
|----------|--------|--------|-------|-----------|-----------|-------------------|----------------|
| **Twelve Data** | ✅ | ✅ | ✅ | ~800 credits/day | Paid | Medium | **Primary unified provider** |
| Alpha Vantage | ✅ | ⚠️ | ✅ | 25 req/day | ❌ | Medium | Indicator / batch enrichment |
| Finnhub | ✅ | ⚠️ | ✅ | 60/min | ✅ | Low–medium | US stocks + live tape |
| Polygon | ✅ | ✅ | ✅ | Delayed/free limited | ✅ | Low (paid) | Production US focus |
| CoinGecko | ❌ | ✅ | ❌ | ~10–30/min | ❌ | Medium | Crypto overview & search |

---

## Recommended architecture per use case

| Use case | Suggested stack |
|----------|-----------------|
| Local dev / CI | `mock` (seeded AAPL, MSFT, NVDA, BTC, ETH, SOL, EUR/USD) |
| MVP unified dashboard | `twelve_data` + server-side cache (60s TTL) |
| Crypto-first product | CoinGecko (overview) + Twelve Data or Binance for OHLCV |
| US equities realtime | Finnhub or Polygon WebSocket → backend fan-out |
| Research / backtests | Alpha Vantage (indicators) + cached OHLCV store |

---

## Environment variables (MarketPulse)

```bash
MARKET_DATA_PROVIDER=mock          # mock | twelve_data
TWELVE_DATA_API_KEY=               # required when provider=twelve_data
```

---

## Next steps

1. Implement Twelve Data HTTP client in `providers/twelve_data.py`.
2. Add Redis or in-memory TTL cache to protect quota.
3. Optional **composite provider**: CoinGecko for crypto dominance + Twelve Data for quotes/OHLCV.
4. Add provider health metrics (`latency_ms`, `source`) already modeled in `SourceMeta`.
