# Architecture Decision Records

## Format

```markdown
## ADR-NNN — <title>

- **Date:** YYYY-MM-DD
- **Status:** proposed | accepted | superseded | deprecated
- **Context:** Why the decision was needed.
- **Decision:** What was decided.
- **Consequences:** What this means going forward.
- **Superseded by:** ADR-NNN (if applicable)
```

---

## ADR-001 — AI-Native SDLC as Project Operating System

- **Date:** 2026-05-26
- **Status:** accepted
- **Context:** The project needs a structured approach to development that supports autonomous AI agents operating alongside human developers. Without a formal lifecycle model, agents risk making inconsistent, unsafe, or unverifiable changes.
- **Decision:** Adopt a 10-stage AI-Native SDLC model (ticket → requirements → architecture → implementation → validation → review → deployment → observability → incident → autofix) as the primary operating model. All agent activity is governed by `.sdlc/` configuration and `.cursor/` instructions.
- **Consequences:**
  - Every feature or fix must trace back to a stage and have explicit evidence.
  - Agents must load context before acting and validate after structural changes.
  - The Doctor is mandatory after structural changes.

---

## ADR-002 — Python as Primary Backend Language

- **Date:** 2026-05-26
- **Status:** accepted
- **Context:** The `.env` and configuration imply Python tooling (`rpg_dsl`, `aiosqlite`, `pyproject.toml`). The team has Python expertise.
- **Decision:** Python is the primary backend language. New code follows PEP 8, uses type hints, and uses `pyproject.toml` for dependency management.
- **Consequences:** Frontend language is still TBD. Shared types may need serialization contracts (JSON Schema or Pydantic) for future cross-language use.

---

## ADR-003 — SQLite for Local Development

- **Date:** 2026-05-26
- **Status:** accepted
- **Context:** The `.env` defines `DATABASE_URL=sqlite+aiosqlite:///./data/rpg_op.db`. Using SQLite locally avoids Docker dependency for the database during the initialization phase.
- **Decision:** SQLite (`aiosqlite`) for local development. Production database target is TBD — will be decided when the first deployable service is defined. Use an ORM abstraction layer to minimize database-specific code and ease future migration.
- **Consequences:** Production database decision deferred. ORM must abstract the connection layer from day one.

---

## ADR-004 — FastAPI + Pydantic v2 + Uvicorn for Investment Radar Backend

- **Date:** 2026-05-27
- **Status:** accepted
- **Context:** INVES-20..22 require a Python REST API with typed request/response models, OpenAPI for frontend contract sync, and async I/O for external market data calls. ADR-002 commits to Python; framework was TBD.
- **Decision:** Use **FastAPI** (latest 0.11x), **Pydantic v2** for schemas and validation, and **Uvicorn** as the ASGI server. Structure: `app/backend/` with routers per domain (`health`, `assets`, `watchlist`, `portfolio`), services for market data and persistence, Pydantic models mirroring `docs/architecture/investment-radar-api.md`.
- **Consequences:**
  - OpenAPI spec generated at `/api/v1/openapi.json` — ContractValidator can diff against frontend types later.
  - Async endpoints throughout; blocking provider SDKs wrapped in `asyncio.to_thread` if needed.
  - No WebSockets in MVP; polling via REST only.
  - Dependencies added via `pyproject.toml` when implementation starts (INVES-20).

---

## ADR-005 — React + Vite + TypeScript for Investment Radar Frontend

- **Date:** 2026-05-27
- **Status:** accepted
- **Context:** INVES-23 needs a locally runnable web UI for asset search, watchlist, portfolio dashboard, and price charts. Frontend framework was pending in ADR-002 consequences and `architecture.md`.
- **Decision:** Adopt **React 18+**, **Vite 5+**, and **TypeScript** in `app/frontend/`. Use lightweight data fetching (native `fetch` or TanStack Query optional), and a minimal chart library (e.g. Recharts) for history visualization. Styling: CSS modules or Tailwind — implementer choice; default to Vite React-TS template structure.
- **Consequences:**
  - Dev server on port **5173** (aligned with `CORS_ORIGINS` in `.env`).
  - Shared API types duplicated manually or generated from OpenAPI in a later iteration — not blocking MVP.
  - No SSR; static SPA served by Vite dev server locally, production build TBD (INVES-24 runbook covers local demo only).

---

## ADR-006 — Market Data Providers and Fallback Catalog

- **Date:** 2026-05-27
- **Status:** accepted
- **Context:** Investment Radar must show real market data when API keys are configured, degrade gracefully when providers fail or keys are absent, and never block the demo. Product is not a trading platform — read-only market data plus simulated portfolio.
- **Decision:**
  - **US equities (primary):** [Finnhub](https://finnhub.io/) — quote, search, daily candles when `FINNHUB_API_KEY` is set.
  - **US equities (secondary):** [Alpha Vantage](https://www.alphavantage.co/) — fallback when Finnhub rate-limits or errors (`TWELVE_DATA_API_KEY` in `.env` reserved as tertiary optional).
  - **Crypto:** [CoinGecko](https://www.coingecko.com/en/api) public API — no key required for MVP; optional `COINGECKO_API_KEY` for higher limits.
  - **Brazilian equities (optional):** [Brapi](https://brapi.dev/) when `BRAPI_API_KEY` is set — extends search/quote for B3 tickers.
  - **Fallback catalog:** Bundled static JSON in backend (`fallback_catalog`) with a curated set of stocks/crypto and last-known or synthetic prices. Used when all live providers fail or keys are missing.
  - **Provenance:** Every price-bearing response includes `source: "live" | "fallback"` (see API contract).
- **Consequences:**
  - Provider adapter interface in backend; order: primary → secondary → fallback.
  - No web scraping (`MARKET_DATA_SCRAPING_ENABLED=false` enforced).
  - Rate limits documented in INVES-24 runbook; demo works offline via fallback.
  - Redis in `.env` is **out of scope** for MVP — no caching layer until needed.

---

## ADR-007 — Single-User Local SQLite Persistence (SQLAlchemy Async)

- **Date:** 2026-05-27
- **Status:** accepted
- **Context:** Watchlist (INVES-21) and simulated portfolio (INVES-22) need durable local state. ADR-003 established SQLite for local dev; ORM was TBD. MVP is single-user with no authentication.
- **Decision:**
  - Database file: `sqlite+aiosqlite:///./data/investment_radar.db` (product DB separate from SDLC obs DB).
  - **SQLAlchemy 2.0** async ORM with **aiosqlite** driver.
  - Single implicit user: one default portfolio row seeded on first startup (`cash_balance: 100000 USD`).
  - Tables: `watchlist_items`, `portfolios`, `holdings`, `transactions`.
  - Migrations: Alembic optional for MVP; SQLAlchemy `create_all` acceptable for local demo if documented in runbook.
- **Consequences:**
  - No auth middleware; binding to localhost in runbook is the security boundary for demo.
  - Production multi-user would require new ADR (auth + Postgres/Supabase).
  - Implementers share models across INVES-21 and INVES-22 via `app/backend/` internal modules.

---

## ADR-008 — REST API Conventions and Auth Deferral

- **Date:** 2026-05-27
- **Status:** accepted
- **Context:** Three backend sub-tasks must expose consistent URLs, errors, and identifiers. Authentication strategy was an open question; product owner confirmed local single-user MVP without login.
- **Decision:**
  - **Prefix:** `/api/v1/` on all JSON endpoints.
  - **Asset IDs:** `{class}:{symbol}` — e.g. `stock:AAPL`, `crypto:BTC` (lowercase class, uppercase symbol).
  - **Errors:** JSON body `{ "error": { "code", "message", "details" } }` with HTTP status mapping (see `investment-radar-api.md`).
  - **Auth:** **Deferred** — no JWT, sessions, or API keys on client requests for MVP. CORS restricted to local frontend origins.
  - **Versioning:** Path-based (`v1`); breaking changes require `v2` or explicit ADR supersession.
- **Consequences:**
  - Frontend needs no auth headers for local demo.
  - Adding auth later is a breaking change — track via new ADR before any hosted deployment.
  - Full endpoint list and schemas: `docs/architecture/investment-radar-api.md`.

---

## ADR-009 — Studio Service as Isolated SDLC Control Plane

- **Date:** 2026-06-03
- **Status:** accepted
- **Context:** INVES-76 requires a usable Studio product (dashboard, canvas, observability) without colliding with MarketPulse (`app/backend/`, `app/frontend/`) or duplicating Foundation logic in `studio/`. Cursor chat, Plane, and GitHub remain authorities for agents, workboard, and delivery.
- **Decision:**
  - Add **separate packages** `app/studio-backend/` (`studio_service` Python module) and `app/studio-frontend/` (`studio-frontend` npm package).
  - Expose all Studio HTTP routes under prefix **`/studio/*`** on port **8100**; UI dev server on **5174**.
  - Backend **wraps** `studio/` imports — no fork of compiler/validator/canvas logic.
  - **Propose-only mutations:** API may generate patch previews; no route applies writes to `.sdlc/` or `.cursor/` — operators use existing Plane + git workflow.
  - **Realtime observability:** unify `sdlc_obs`, gateway hooks, session gate, and handoff via a shared `StudioEvent` envelope over SSE (`GET /studio/obs/events`).
  - **React Flow** renders derived `CanvasViewModel` JSON; layout coordinates are frontend-local and non-authoritative.
- **Consequences:**
  - Root `pyproject.toml` gains a `[studio]` optional extra or PYTHONPATH dev wiring (INVES-78).
  - MarketPulse and Studio can run concurrently on different ports.
  - OpenAPI for Studio is independent of `/api/v1/` — ContractValidator runs separately per product surface.
  - Full route map and event schema: `docs/architecture/studio-service-platform.md`.
  - Auth deferred to S7 (local bind `127.0.0.1` until then).

---

## ADR-010 — Studio S4 Propose-Only Mutation Contract

- **Date:** 2026-06-03
- **Status:** accepted
- **Context:** INVES-84 requires a frozen contract before S4 Workflow Builder and `POST /studio/proposals` land. Risk: Studio API bypasses `.cursor/hooks` write gate and silently mutates `.sdlc/` or `.cursor/`. Implementers need a single allowlist, patch format, and dry-run exit semantics.
- **Decision:**
  - **No apply route.** Proposals are preview + dry-run only; apply remains Plane child → `workflow start` → branch → git commit → PR.
  - **Allowlist:** strict prefixes under `.sdlc/workflows|stages|pipeline|manifest|gates/` and `.cursor/agents|rules|skills|commands/`; explicit denylist for `.sdlc/memory/`, hooks, `app/`, `specs/`, etc. (see `.sdlc/memory/architecture.md` § Propose-only mutation contract).
  - **Wire format:** `patch_format: unified_diff` in API responses; builder may send `structured_ops` compiled server-side to unified diff.
  - **Dry-run order:** validate (engine) → doctor (subprocess, exit 0/1) → gateway-check (`gate.check_write` per path, exit 0/1). Gateway-check is **mandatory** before UI apply checklist (no MVP bypass).
  - **Policy reference:** `.sdlc/gateways/policy.yaml` `studio_proposals` block documents the same rules for reviewers and simulation tests.
- **Consequences:**
  - S4 backend implements `mutation.py` + `proposals.py` against this contract only.
  - QA must assert absence of `/apply` and forbidden writes in integration tests.
  - Enforcement roadmap fail-closed work remains separate; this ADR does not weaken hooks.

---

## ADR-011 — Supabase as Auth and PostgreSQL Provider (RPG Platform)

- **Date:** 2026-06-11
- **Status:** accepted
- **Context:** RPG Platform MVP requires multi-user auth (Master/Player per Mesa), OAuth, and relational metadata. ADR-003/007 targeted SQLite for Investment Radar. Product refinement (Q-010, Q-019) chose Supabase.
- **Decision:**
  - Use **Supabase Auth** for identity — email/password + **Google OAuth** (required MVP).
  - Use **Supabase PostgreSQL** for all product metadata (`users`, `mesas`, permissions, `storage_files`, versions).
  - `users.id` mirrors `auth.users.id` (UUID).
  - **Authorization in FastAPI** for MVP; Supabase RLS deferred to v1.1.
  - Local development via `supabase start` (Docker).
- **Consequences:**
  - ADR-003 SQLite scope limited to SDLC obs and legacy demos — not RPG Platform product DB.
  - Backend validates Supabase JWT via JWKS; no custom password storage.
  - New env vars: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `DATABASE_URL`.

---

## ADR-012 — Supabase Storage as Campaign Content Store

- **Date:** 2026-06-11
- **Status:** accepted
- **Context:** Sheet templates and character data are JSON; documents are Markdown; media attachments required (Q-013). Product refinement chose Storage over Postgres JSONB for campaign payloads.
- **Decision:**
  - Buckets: `profiles` (avatars), `campaigns` (all Mesa content).
  - Layout: `campaigns/{mesa_id}/templates|characters|documents|assets/` per [storage-layout.md](../product/storage-layout.md).
  - Postgres rows hold `storage_path`, contract metadata, and cache fields only.
  - All writes via FastAPI service role; clients receive **signed URLs** (1h TTL) for permitted reads.
  - Version snapshots as immutable files under `versions/` subfolders.
- **Consequences:**
  - Every write path updates `storage_files` with `checksum_sha256` and contract version.
  - Export/backup = folder zip per Mesa.
  - Implementation must handle compensating deletes on failed transactions.

---

## ADR-013 — Sheet Import via LangChain Deep Agents

- **Date:** 2026-06-11
- **Status:** accepted
- **Context:** Mesa creation requires bootstrapping sheet templates from uploaded PDF/PNG (Q-017). Manual schema authoring does not scale.
- **Decision:**
  - Use **`deepagents`** (`create_deep_agent`) as the agent harness.
  - Model: **`openai:gpt-4.1-mini`** from `AGENT_MODEL` env var.
  - Custom tools: render PDF pages, load D&D reference glossary, submit/validate `sheet-import-proposal`.
  - Subagents for classification, per-page layout, contract mapping.
  - Agent output stops at `proposed`; Master approval required before Storage persist.
  - Ephemeral workspace for page images — not the `campaigns` bucket.
- **Consequences:**
  - Dependencies: `deepagents`, `langchain-openai`, `pymupdf`.
  - `sheet_import_jobs` table tracks pipeline state.
  - Upgrade model by changing `AGENT_MODEL` only.

---

## ADR-014 — Versioned JSON Envelopes for Storage Payloads

- **Date:** 2026-06-11
- **Status:** accepted
- **Context:** Dynamic sheet templates per Mesa require strict validation to prevent corrupt campaign data.
- **Decision:**
  - All Storage JSON files use envelope: `contract`, `contract_version`, `meta`, `payload`.
  - JSON Schema source of truth in `app/shared/contracts/`.
  - API rejects invalid payloads (HTTP 422) before Storage write.
  - Contract IDs: `rpg.sheet-template`, `rpg.character-sheet`, `rpg.document-meta`, etc.
- **Consequences:**
  - CI validates seed files and example proposals against schemas.
  - Contract major version bumps require migration window documented per contract.

---

## ADR-015 — RPG Platform Supersedes Investment Radar as Product Focus

- **Date:** 2026-06-11
- **Status:** accepted
- **Context:** Repository pivot to RPG campaign management platform. Investment Radar implementation was never merged as active product.
- **Decision:**
  - **RPG Platform** is the sole active product vertical in `app/backend/` and `app/frontend/`.
  - Investment Radar docs remain as legacy reference only.
  - New Plane cards use prefix `RPG-N` on project RPG (board config in `.sdlc/sdlc.yaml`).
- **Consequences:**
  - `app/backend/` greenfield implementation follows [rpg-platform-overview.md](./rpg-platform-overview.md).
  - ADR-006 through ADR-008 market-data specifics do not apply to RPG MVP.
