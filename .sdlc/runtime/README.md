# Runtime manifest module

> **Data:** [`manifest.yaml`](manifest.yaml) · **Index:** `.sdlc/sdlc.yaml` → `contract.modules.runtime`

## Purpose

Machine-readable **path index** for observability and session runtime. Studio, hooks, and Makefile resolve stores through this file — not hardcoded paths in prose docs.

## When to read

| Situation | Section |
|-----------|---------|
| Studio obs broken / wrong DB | `obs.*` |
| Learning loop empty | `learning.*` |
| Gate correlation missing | `session.*` |
| Lifecycle SoT question | `lifecycle.canonical` |

## Related

- [`../manifest/catalog.yaml`](../manifest/catalog.yaml) — agent/skill phonebook
- [`../process/lifecycle-model.yaml`](../process/lifecycle-model.yaml) — graph + write_policy
- [`../../app/infra/sdlc_obs/README.md`](../../app/infra/sdlc_obs/README.md) — SQLite implementation

## Do not

- Store business logic here — paths and schema refs only
- Commit ephemeral session files listed under `session.*`
