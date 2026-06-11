# System Context

## Project Purpose

**sdlc-ai** is an AI-Native SDLC platform — a system that enables AI agents to operate across the full software development lifecycle alongside human developers.

The platform is both:
1. **A product host** — running **Investment Radar**, a local investment monitoring demo (not a trading platform).
2. **A meta-example** — built using the same SDLC model it implements.

## Investment Radar (Product Context)

| Attribute | Value |
|-----------|-------|
| Epic | INVES-19 |
| Goal | Locally runnable demo: search assets, watchlist, simulated portfolio |
| Out of scope | Real trades, brokerages, payments, money movement |
| Users (MVP) | Single implicit local user — no login |
| Data | Live market quotes when keys configured; fallback catalog otherwise |

## Stakeholders

| Role          | Concern                                              |
|---------------|------------------------------------------------------|
| Developer     | Fast, safe, well-governed development workflow       |
| AI Agent      | Clear context, deterministic gates, safe autonomy    |
| Tech Lead     | Visibility into decisions, risks, and validation     |
| Operations    | Deployable, observable, maintainable system          |
| Demo user     | Clear UI, honest `source` labels on market data      |

## External Dependencies

| System          | Purpose                              | Status        |
|-----------------|--------------------------------------|---------------|
| GitHub          | Version control and PR workflow      | configured    |
| Plane           | Task and project management          | configured    |
| OpenAI          | LLM inference (SDLC agents)          | configured    |
| Finnhub         | US equity quotes, search, candles    | optional key  |
| Alpha Vantage   | Secondary US equity data             | optional key  |
| CoinGecko       | Crypto quotes and search             | no key (MVP)  |
| Brapi           | Brazilian (B3) equities              | optional key  |

## System Boundaries

```
                    ┌──────────────────────────────┐
                    │   External market data APIs   │
                    │  (read-only, rate-limited)  │
                    └──────────────┬───────────────┘
                                   │
┌──────────────┐                   │              ┌──────────────┐
│   Developer  │─── SDLC tools ────┼──────────────│    Plane     │
│  + AI Agent  │    .cursor/.sdlc  │              │   (tasks)    │
└──────────────┘                   │              └──────────────┘
                                   ▼
                    ┌──────────────────────────────┐
                    │     Investment Radar (app/)   │
                    │  ┌─────────┐   ┌───────────┐ │
                    │  │ Backend │◄──│ Frontend  │ │
                    │  │ FastAPI │   │ React SPA │ │
                    │  └────┬────┘   └─────▲─────┘ │
                    │       │                │       │
                    │       ▼                │       │
                    │  SQLite (local)        │       │
                    └────────────────────────┼───────┘
                                             │
                              ┌──────────────┴──────────────┐
                              │  Browser (localhost user)    │
                              │  No auth — single-user demo  │
                              └─────────────────────────────┘
```

### Trust boundaries

| Boundary | Inside | Outside |
|----------|--------|---------|
| User | Browser on developer machine | No public internet exposure assumed in MVP |
| Secrets | `.env` API keys (server-side only) | Never sent to frontend |
| Money | Simulated `cash_balance` in SQLite | No payment processors or broker APIs |
| Market data | Aggregated quotes with `source` tag | Raw provider responses not exposed |

## Constraints

- **Not a trading platform** — simulated buy/sell updates local state only.
- **Local-first MVP** — backend `0.0.0.0:8000`, frontend `localhost:5173`.
- **Auth deferred** — see ADR-008; do not add login until hosted deployment ADR exists.
- **No web scraping** — `MARKET_DATA_SCRAPING_ENABLED=false`.

## Business Context

Investment Radar demonstrates the SDLC pipeline delivering a vertical slice: market data ingestion, persistence, API, and UI suitable for portfolio **monitoring** and education — not execution of real financial transactions.

## References

- API contract: [investment-radar-api.md](./investment-radar-api.md)
- ADRs: [decisions.md](./decisions.md) (ADR-004 through ADR-008)
- Epic: Plane INVES-19
