# Manifest module

> **Data:** [`catalog.yaml`](catalog.yaml) · **Index entry:** `sdlc.yaml` → `contract.modules.manifest`

## Purpose

Catalog of every **agent**, **skill**, **MCP server**, **command**, and **reading order** for the SDLC pipeline. This is the phone book — it does not execute anything.

## When to read

| Situation | What to look up |
|-----------|-----------------|
| Spawning a subagent | `agents.pipeline[]` → `path` (e.g. `.cursor/agents/implementer.md`) |
| Finding a skill | `skills[]` → `path` under `.cursor/skills/` |
| MCP setup | `mcps[]` + `.cursor/mcp.json` |
| New session bootstrap | `reading_order[]` — ordered file list |
| Plane/GitHub defaults | `project.*` (workspace `rpg`, card prefix `RPG`) |

## Key sections in `catalog.yaml`

| Section | Content |
|---------|---------|
| `reading_order` | Files every agent should load before work |
| `agents.pipeline` | Intent Analyst → Planner → … → DevOps |
| `agents.support` | Doctor, Observer, etc. |
| `skills` | Skill id, path, stage binding |
| `mcps` | Plane, GitHub server names |
| `commands` | Cursor slash commands under `.cursor/commands/` |

## Related modules

- [`../pipeline/README.md`](../pipeline/README.md) — stage → agent mapping (runtime flow)
- [`../memory/README.md`](../memory/README.md) — handoff and session state
- [`../integrations/README.md`](../integrations/README.md) — vendor tokens and roles

## Related paths (outside this folder)

- Agent prose: `.cursor/agents/*.md`
- Skill procedures: `.cursor/skills/*/SKILL.md`
- L0 entry: [`AGENTS.md`](../../AGENTS.md)

## Do not

- Add product code paths here — manifest is SDLC metadata only
- Duplicate agent definitions in `pipeline/agents.yaml` — manifest is catalog; pipeline is stage binding
