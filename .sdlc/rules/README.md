# Rules module

> **Data:** [`governance.yaml`](governance.yaml) · **Prose rules:** `.cursor/rules/*.mdc`

## Purpose

Machine-readable **governance rules** (severity, enforced stages). YAML rules are checked by Doctor; `.mdc` rules are agent behavior law.

## When to read

| Situation | File |
|-----------|------|
| Before claiming tests passed | `governance.yaml` → `no_fake_validation` |
| After structural repo change | `doctor_after_structural_change` |
| Docs changed with code | `docs_sync_required` |
| Finding Cursor rules | `.sdlc/sdlc.yaml` → `contract.rules_ref` |

## Key governance rules

| Id | Severity | Summary |
|----|----------|---------|
| `no_fake_validation` | required | Never fabricate test/doctor results |
| `docs_sync_required` | required | Update docs when architecture/APIs change |
| `doctor_after_structural_change` | required | Run `make sdlc-doctor` after `.sdlc/` or `.cursor/` changes |
| `small_diffs_preferred` | warning | Prefer reversible, scoped changes |

## Layer model

| Layer | Location | Audience |
|-------|----------|----------|
| L0 | `AGENTS.md` | Orchestrator entry |
| L1 | `.sdlc/process/*.md` | Full process |
| L2 | `.sdlc/sdlc.yaml` | Machine index |
| Governance prose | `.cursor/rules/*.mdc` | Agent behavior (alwaysApply) |
| Governance data | `rules/governance.yaml` | Doctor + stage enforcement |

## Related modules

- [`../doctor/README.md`](../doctor/README.md) — validates rule file presence
- [`../stages/README.md`](../stages/README.md) — `enforced_at` stage lists

## Do not

- Edit Doctor checks to hide real failures
- Override `.sdlc/process/master-workflow.md` with ad hoc chat instructions
