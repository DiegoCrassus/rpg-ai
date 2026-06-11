# Operational Context Memory

> Runtime and environment context for Cursor agents. Update when infrastructure changes.

## Current State

**Status:** RPG Platform MVP on `develop` (epic RPG-1 Done). Product code live under `app/` — FastAPI backend, React SPA, Supabase migrations, shared JSON contracts. SDLC Studio orthogonal in `studio/`. Observability: `app/infra/sdlc_obs/`.

**develop HEAD:** `88d54d2` — includes RPG-2/3/4/5 delivery + bootstrap (PRs #1, #2, #4, #5, #6).

## Workflow

**Source of truth:** `.sdlc/process/change-lifecycle.md`

**Gate:** closed (no active card). Handoff idle — await new intent.

## Environments

| Environment | Status    | Notes |
|-------------|-----------|-------|
| local       | active    | Supabase CLI + Docker for product; `make -C app dev` |
| dev         | not_ready | No cloud deploy yet |
| production  | not_ready | Pending deployment setup |

## Local Development — RPG Platform

```bash
cp .env.example .env
cp app/frontend/.env.example app/frontend/.env
make -C app supabase-start    # copy CLI keys to .env files
make -C app install
make -C app dev               # API :8000, UI :5173
```

| Service | URL |
|---------|-----|
| Frontend | http://127.0.0.1:5173 |
| API / OpenAPI | http://127.0.0.1:8000/docs |
| Supabase Studio | http://127.0.0.1:54323 |

**Tests:** `make -C app test` · **Contracts:** `make -C app contracts`

## Local Development — SDLC / Studio

- **Doctor:** `make sdlc-doctor`
- **Studio stack:** `make studio-dev` (API :8100, UI :5174)
- **Observability:** `make obs-server` -> http://localhost:7700

## SDLC Observability

- **Tool:** `app/infra/sdlc_obs/` (SQLite + Python stdlib server)
- **Hooks:** `.cursor/hooks.json` + gateway hooks

## External Services (Active)

| Service | Purpose | Configured Via |
|---------|---------|----------------|
| GitHub | Version control / PR | `GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC` |
| Plane | Task management | `PLANE_API_KEY` / `BOARD_*` |
| OpenAI | LLM + Sheet Import Agent | `OPENAI_API_KEY` |
| Supabase | Auth + Postgres + Storage | `SUPABASE_*` in `.env` |

## Plane — active project

- **Workspace:** `RPG-AI` (`BOARD_WORKSPACE_SLUG`)
- **Project:** `RPG` (`BOARD_PROJECT_ID`)
- **Card prefix:** `RPG-N` (branch: `feature/RPG-N-<slug>`)
- **Epic RPG-1:** Done (children RPG-2..5 Done)

## Process automation

| Script | Purpose |
|--------|---------|
| `.sdlc/scripts/plane_state.py` | In Progress / Done / comment on RPG-N |
| `.sdlc/scripts/auto_merge_pr.py` | Autonomous squash merge when CI green |

Makefile: `make workflow-status`, `make board-in-progress CARD=RPG-N`

## Key Configuration

- `AGENT_MODEL=openai:gpt-4.1-mini`
- `BOARD_WORKSPACE_SLUG=RPG-AI`
- `REPOSITORY_SLUG=DiegoCrassus/rpg-ai`
- Python **3.11+** required (`pyproject.toml`)

## Pending sign-off

Manual MVP journeys 1-3 (`docs/product/mvp-scope.md`) not exercised in CI — run against local stack before release demo.
