# Integrations module

> **Data:** [`services.yaml`](services.yaml) · **Config:** `.cursor/mcp.json` · **Env:** repo `.env` (not committed)

## Purpose

Describes **external service roles** (IDE, VCS, workboard, LLM) in a vendor-neutral way. Maps each integration to env vars and MCP servers — no secrets in YAML.

## When to read

| Task | Integration | Env var (typical) |
|------|-------------|-------------------|
| Create/update Plane cards | **workboard** (Plane) | `PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG` |
| Open PR, merge, CI | **vcs** (GitHub) | `GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC` |
| MCP in Cursor | **ide** | `.cursor/mcp.json` |
| Optional LLM scripts | **llm** | `OPENAI_API_KEY` |

## Vendor ids (from `sdlc.yaml` core)

| Role | Provider | Notes |
|------|----------|-------|
| IDE | Cursor | Agents/skills/hooks under `.cursor/` |
| VCS | GitHub | `DiegoCrassus/rpg-ai`, default branch `develop` |
| Workboard | Plane | Workspace `rpg`, project `RPG`, cards `RPG-N` |
| LLM | OpenAI | Optional; Doctor warns if unset |

## Related modules

- [`../workboard/README.md`](../workboard/README.md) — Plane card rules
- [`../manifest/README.md`](../manifest/README.md) — MCP entries in catalog
- [`../integrations/services.yaml`](services.yaml) — full service definitions

## Skills using integrations

- `.cursor/skills/board-sdlc/SKILL.md` — Plane MCP procedures
- `.cursor/skills/finish-change/SKILL.md` — GitHub merge + Plane Done

## Do not

- Commit API tokens to YAML or git
- Use GitHub Issues as primary tracker — Plane is source of truth
