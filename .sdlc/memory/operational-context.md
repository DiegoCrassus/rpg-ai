# Operational Context Memory

> Runtime and environment context for Cursor agents. Update when infrastructure changes.

## Current State

**Status:** App reset for SDLC retest — `app/backend/` and `app/frontend/` placeholders. Plane RPG-19..24 Done (historical). Observability: `app/infra/sdlc_obs/`.

## Workflow

**Source of truth:** `.sdlc/process/change-lifecycle.md`

## Environments

| Environment | Status       | Notes                          |
|-------------|--------------|--------------------------------|
| local       | active       | SQLite (obs), no product services |
| dev         | not_ready    | Pending product implementation |
| production  | not_ready    | Pending deployment setup       |

## Local Development

- Observability DB: `app/infra/sdlc_obs/data/`
- Python environment: managed via `pyproject.toml`
- No product containers yet

## SDLC Observability

- **Tool:** `app/infra/sdlc_obs/` (SQLite + Python stdlib server)
- **Dashboard:** `make obs-server` → http://localhost:7700
- **Metrics:** precision, cost, time, tool success, hallucination rate, completion rate, regressions
- **Hooks:** `.cursor/hooks.json` (sessionStart/stop) + `pre_task.py` / `post_task.py`

## External Services (Active)

| Service    | Purpose              | Configured Via          | MCP      |
|------------|----------------------|-------------------------|----------|
| GitHub     | Version control / PR | GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC | ✅ active |
| Plane      | Task management      | PLANE_API_KEY           | MCP + `.sdlc/scripts/plane_state.py` |
| OpenAI     | LLM inference        | OPENAI_API_KEY          | —        |

## Plane — active project

- **Workspace:** `investments-sdlc` (`PLANE_WORKSPACE_SLUG`)
- **Project:** `investiments` (`PLANE_PROJECT_NAME`)
- **Card prefix:** `RPG-N` (branch: `feature/RPG-N-<slug>`)

Cards are created in project `investiments` **before** any code edit.

## Process automation (2026-05-27)

| Script | Purpose |
|--------|---------|
| `.sdlc/scripts/plane_state.py` | In Progress / Done / comment on RPG-N |
| `.sdlc/scripts/auto_merge_pr.py` | Autonomous squash merge when CI green |
| `.sdlc/scripts/github_issue_triage.py` | Close superseded GitHub issues |

Makefile: `make plane-in-progress CARD=RPG-N`, `make auto-merge-pr PR=N CARD=RPG-N`, `make issue-triage TRIAGE=1`

## Key Configuration

- `AGENT_MODEL=openai:gpt-4.1-mini`
- `PLANE_WORKSPACE_SLUG=investments-sdlc`
- `PLANE_PROJECT_NAME=investiments`
- `GITHUB_REPOSITORY=DiegoCrassus/sdlc-ai`
