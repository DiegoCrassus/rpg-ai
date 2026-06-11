# Skill: Documentation

## Purpose

Create and synchronize human-readable documentation that accurately reflects the current system state.

## When to Use

- When architecture, infrastructure, or public interfaces change
- When completing a major stage transition
- When generating a handoff summary
- When onboarding materials need updating

## Required Inputs

- Changed files and components
- Current state of `docs/`
- Handoff context (what changed, why, next steps)

## Procedure

1. **Identify what changed** — List all changed components.
2. **Identify affected docs** — Which docs cover these components?
3. **Update each affected doc** — Reflect the actual current state.
4. **Verify no empty sections remain** — Replace placeholders with real content or mark explicitly as TBD.
5. **Update `docs/handoff/current-state.md`** — Record the transition.
6. **Add ADR if applicable** — For architecture decisions, use `docs/architecture/decisions.md`.

## Docs by Stage

| Stage            | Docs to consider                                      |
|------------------|-------------------------------------------------------|
| Architecture     | `docs/architecture/overview.md`, `decisions.md`      |
| Implementation   | `docs/architecture/overview.md` (if boundaries change)|
| Deployment       | `docs/infrastructure/deployment.md`                  |
| Observability    | `docs/operations/observability.md`                   |
| Incident         | `docs/operations/incident-response.md`, `incidents.md`|
| Handoff          | `docs/handoff/current-state.md`                      |

## Outputs

- Updated docs files
- Handoff summary (if stage transition)
- ADR entry (if decision made)

## Validation Checklist

- [ ] No doc file left in a state that misrepresents current reality
- [ ] No empty sections in updated files
- [ ] Handoff summary complete if transitioning stages
- [ ] ADR written for significant decisions

## Failure Modes

- **Stale docs** — Docs that describe the old state are worse than no docs; always update
- **Aspirational docs** — Never document a future state as if it exists now; use "TBD" or "planned"
- **Empty placeholder files** — Every doc must have useful content, not just headers
