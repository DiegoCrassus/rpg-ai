# Process module

> **Authority:** SDLC operating process · **Machine complement:** [`../sdlc.yaml`](../sdlc.yaml), [`../stages/definitions.yaml`](../stages/definitions.yaml)

## Purpose

Own the human-readable SDLC process authority. Keep this module small: one workflow document and one lifecycle/git/Plane authority document.

## When to read

| Situation | Start with |
|-----------|------------|
| Any new request or pipeline doubt | [`master-workflow.md`](master-workflow.md) |
| Branch, PR, merge, Plane state, or lifecycle authority | [`change-lifecycle.md`](change-lifecycle.md) |
| Stage graph, transitions, write policy | [`lifecycle-model.yaml`](lifecycle-model.yaml) |
| Emergency enforcement bypass | [`break-glass.md`](break-glass.md) |

## Classification

| File | Class | Notes |
|------|-------|-------|
| `master-workflow.md` | `agent-procedure`, `human-reference` | L1 pipeline authority |
| `change-lifecycle.md` | `agent-procedure`, `human-reference` | L1 git, Plane, PR, and merge authority |

## Related modules

- [`../gates/README.md`](../gates/README.md) — writable path policy
- [`../workflows/README.md`](../workflows/README.md) — declarative transition graph
- [`../doctor/README.md`](../doctor/README.md) — structure validation
- [`../stages/README.md`](../stages/README.md) — lifecycle stages and evidence

## Boundaries

- Product/app documentation belongs under `docs/`.
- Cursor execution instructions belong under `.cursor/`.
- Machine-readable SDLC data belongs in the matching `.sdlc/<module>/` YAML.

## Do not

- Create local tickets, backlogs, or Plane evidence here.
- Add product architecture docs here; use `docs/architecture/`.
- Override `AGENTS.md` or `.cursor/rules/`; this module explains process authority, it does not replace executable rules.
