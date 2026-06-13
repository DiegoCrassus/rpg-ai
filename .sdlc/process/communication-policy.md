# SDLC Communication Policy — Caveman vs Human

> **Authority:** complements `AGENTS.md` Token law. Agents MUST follow this file.

## Purpose

Reduce token waste and handoff drift. Inter-agent traffic stays minimal. Human-facing artifacts stay readable.

## Two channels

| Channel | Audience | Style | Examples |
|---------|----------|-------|----------|
| **Caveman** | Orchestrator, subagents, handoffs, Task prompts, hook messages | Verb first. One fact per line. No fluff. Max density. | `.sdlc/memory/orchestrator-handoff.md`, Task spawn, subagent internal notes |
| **Human** | User chat (Portuguese), Plane cards, plan docs, PR bodies, evidence JSON summaries | Clear sentences. Structured sections. Slightly verbose OK. | `.sdlc/process/harness-v6-plan.md`, Plane HTML, `execution-RPG-N.json` summary fields |

## Caveman rules (mandatory for agents)

1. **Handoff** — use template only; ≤ `core.tokens.handoff_max_lines` (45).
2. **Task spawn** — `card | branch | stage | do | out | block` — one line each.
3. **Errors** — `WHAT / WHERE / FIX` — three lines max.
4. **No repeat** — do not restate AGENTS.md, chat history, or prior handoff.
5. **No essays** — bullets, tables, IDs, paths, commands only.
6. **Internal reasoning** — keywords + decision only (`intent=SDLC_META → implementer`).

## Human rules (mandatory for human artifacts)

1. **Plane cards** — full AC, non-goals, risks (see board-task-creation skill).
2. **Plan docs** — complete sentences; diagrams OK; English in `.sdlc/`.
3. **User chat** — Portuguese; explain trade-offs when asked.
4. **Evidence snapshots** — `summary`, `context_for_future` readable by humans reviewing Done.

## Exceptions

| Artifact | Style |
|----------|-------|
| Code, commits | Normal conventions |
| JSON ledger events | Machine-first; optional `human_note` field for summaries |
| Doctor output | Technical; may be dense |

## Enforcement

- Post-gateway validates handoff shape, not prose quality.
- Reviewer SHOULD reject handoffs that exceed line budget or contain essay blocks.
- Orchestrator MUST rewrite verbose subagent handoffs to caveman before next spawn.

## Related

- `AGENTS.md` — L0 token law
- `.sdlc/templates/orchestrator/handoff-template.md`
- `.cursor/rules/060-communication.mdc`
