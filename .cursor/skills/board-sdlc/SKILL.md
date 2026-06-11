# Skill: Board SDLC (MCP)

> **Workflow authority:** `.sdlc/process/change-lifecycle.md`

## Purpose

Create, update states, and close **work items exclusively on the configured workboard** (provider: Plane). Never local backlog (`specs/`).

## State lifecycle (mandatory)

| Moment | Board state | How |
|---------|-------------|-----|
| Plan created (Planner) | **Todo** or Backlog | MCP create issue |
| `start-change` / start implementation | **In Progress** | `python3 .sdlc/scripts/plane_state.py in-progress --card RPG-N` |
| PR opened | In Progress (+ PR comment) | comment on card |
| Merge + green CI | **Done** | `auto_merge_pr.py --plane-comment` or `plane_state.py done` |

**Process failure:** implementing with card in Todo/Backlog, or marking Done without passing through In Progress.

## MCP

- Config: `.cursor/mcp.json` — server `plane` (token **must** match board API key in `.env`)
- Env (logical): `BOARD_API_KEY` / legacy `PLANE_API_KEY`, `BOARD_WORKSPACE_SLUG` / `PLANE_WORKSPACE_SLUG`

| Field | Value (from `.sdlc/sdlc.yaml` → `core.vendors.board`) |
|-------|--------------------------------------------------------|
| Workspace | `RPG-AI` |
| Project | `RPG` |
| Card ID | `RPG-N` |

## Procedure — create work item

1. Connect via board MCP or REST (`.sdlc/scripts/plane_state.py` uses Plane REST).
2. Create issue in project `RPG`.
3. Title: `[AI][TYPE] Short imperative title`
4. **Description:** HTML TipTap via `plane_html.build_plan_html` — `.cursor/skills/board-formatting/SKILL.md`
5. Initial state: **Todo** (epic) or **Todo** (sub-task awaiting start-change)
6. Record returned `RPG-N`

## Procedure — In Progress

Run **on start-change**, before branch/code:

```bash
python3 .sdlc/scripts/plane_state.py in-progress --card RPG-N --branch feature/RPG-N-<slug>
```

## Procedure — evidence and Done

1. Fill `.sdlc/templates/plane/evidence-template.json` with the active `RPG-N` evidence (Implementer/Reviewer)
2. Post formatted evidence — **not** a one-liner comment
3. **Done** after merge + CI via `auto_merge_pr.py --plane-comment --evidence-file …`

## Prohibitions

- Never `specs/` or local tickets
- Never repository issues as primary tracker (Issue Analyst triages/closes duplicates)
- Never invent `RPG-N`
