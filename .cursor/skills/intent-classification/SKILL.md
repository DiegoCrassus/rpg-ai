# Skill: Intent Classification

> **Authority:** `.sdlc/process/master-workflow.md`

## Purpose

Classify user input before any SDLC action. Output drives Orchestrator routing.

## When to use

- Every new user message (Orchestrator delegates Task Intent Analyst)
- Skip only if `session-gate.json` has active open gate for continuing work

## Procedure

1. Read user message + `session-gate.json` + repo state (`app/` placeholders).
2. Run heuristic classifier (optional bootstrap):

   ```bash
   python3 .sdlc/dsl/cli.py workflow classify --text "<message>"
   ```

3. Refine with LLM reasoning — override heuristic if confidence < 0.8.
4. Discovery hook (GREENFIELD / FEATURE in product repo):
   - Glob `docs/product/*`, `docs/architecture/*-api.md`
   - List as `legacy_docs[]` in handoff
5. Write **Markdown** handoff to `.sdlc/memory/orchestrator-handoff.md` (template: `.sdlc/memory/README.md` — no YAML fences).
6. Update `session-gate.json` → `intent` field only (do not open gate).

## Urgency policy

User phrases (examples, any language): e.g. Portuguese *"sem interrupções"*, *"urgente"*, *"faz direto"*; English *"no interruptions"*, *"urgent"*, *"just do it"*.

→ Set `autonomous: true` in handoff meta — **does not** set `skip_gates: true`.

## Output checklist

- [ ] intent enum set
- [ ] requires_plane correct
- [ ] next_agent set
- [ ] handoff file written
- [ ] legacy_docs listed if product work

## Return to Orchestrator

Never call Implementer. Never create branch. Never open gate.
