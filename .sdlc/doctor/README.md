# Doctor module

> **Data:** [`checks.yaml`](checks.yaml) · **Runner:** `.sdlc/dsl/doctor.py` · **Canvas:** `.sdlc/dsl/doctor_health_canvas.py`

## Purpose

Minimal structural validation of the repository: required runtime files, README indexes, module consistency, integration hints, and post-change gates. **Every run** produces a health Canvas and `memory/doctor-health.json`.

The Doctor is the guardrail for the current v5.2 structure. It validates both
presence of modular files and **absence** of legacy flat files.

## When to read

| Situation | Action |
|-----------|--------|
| After changing `.sdlc/` layout | Update `checks.yaml` if needed → `make sdlc-doctor` |
| After adding `.cursor/` config | Same |
| Before merge of SDLC_META PR | Doctor must exit **0** (FAIL blocks) |
| WARN only (missing API keys) | Non-blocking — integrations not configured locally |
| Legacy flat YAML appears at `.sdlc/` root | Doctor must fail; remove it or migrate data into the module folder |
| Handoff returns to YAML code fence | Doctor must fail; use Markdown sections |

## Toolchain

```
make sdlc-doctor
  → doctor.py loads checks.yaml (+ modular paths via loader.py)
  → doctor_health_canvas.py writes Canvas + doctor-health.json
```

## Edit checklist

1. Change [`checks.yaml`](checks.yaml) (add/remove/rename checks)
2. Run `make sdlc-doctor` — expect 0 failures
3. Run `make sdlc-validate` for YAML consistency
4. If new top-level module: update [`../sdlc.yaml`](../sdlc.yaml) `contract.modules` + module README

## Related modules

- [`../rules/README.md`](../rules/README.md) — `doctor_after_structural_change`
- [`../sdlc.yaml`](../sdlc.yaml) — module and path index

## Output artifacts

| File | Git |
|------|-----|
| `.sdlc/memory/doctor-health.json` | Untracked runtime summary |
| `sdlc-doctor-health.canvas.tsx` | IDE Canvas (user projects dir) |

## Current structure assertions

`checks.yaml` enforces:

- Long-lived module README files exist and contain navigation markers (`Purpose`, `When to read`)
- Canonical YAML files live under module folders (`manifest/catalog.yaml`, `gates/paths.yaml`, etc.)
- Legacy root YAML files are absent (`manifest.yaml`, `pipeline.yaml`, `stages.yaml`, etc.)
- `orchestrator-handoff.md` does not contain ` ```yaml `
- Removed heavyweight guide/reference/tracking paths do not reappear

## Do not

- Weaken checks to pass a broken layout
- Claim Doctor passed without running it
