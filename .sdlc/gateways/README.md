# Gateways Module

> **Policy:** [`policy.yaml`](policy.yaml) · **Hooks:** `.cursor/hooks/sdlc_pre_gateway.py`, `.cursor/hooks/sdlc_post_gateway.py`

## Purpose

Deterministic quality harness around agent interactions. Gateways evaluate what is about to happen and what just happened, then allow, deny, or route the agent back to the previous step when required evidence is missing.

## When to read

| Situation | File |
|-----------|------|
| Hook denies or redirects a step | `policy.yaml` |
| Need to understand pre-execution checks | `.cursor/hooks/sdlc_pre_gateway.py` |
| Need to understand post-step checks | `.cursor/hooks/sdlc_post_gateway.py` |
| Handoff validation fails | `../memory/README.md` |

## Gateway flow

```text
pre gateway
  -> deny destructive/local-ticket actions
  -> enforce expected next subagent when handoff is explicit
  -> allow safe/unknown actions without rewriting input

agent/tool/subagent runs

post gateway
  -> parse orchestrator-handoff.md
  -> validate required Markdown sections and routing fields
  -> if Stage complete = no or fields are missing, follow up with a deterministic return instruction
```

## Owned files

| File | Purpose |
|------|---------|
| `policy.yaml` | Stage order, valid agents, denied shell patterns, and handoff requirements |

## Boundaries

- This module defines deterministic harness policy only.
- Write permission is still enforced by `.sdlc/gates/paths.yaml` and `sdlc_gate_hook.py`.
- Plane remains the source of truth for work items and evidence.
- Hooks are **fail-closed** (`failClosed: true` in `.cursor/hooks.json`). If `policy.yaml` or PyYAML is missing, pre/post gateways deny.
- Emergency bypass: set `SDLC_BREAK_GLASS=1` and document on a Plane **SDLC_META** card before using `workflow start --force`, `--skip-plane`, `--skip-validate`, or `auto_merge_pr.py --skip-ci-wait`.

## Related modules

- [`../gates/README.md`](../gates/README.md) — mechanical write gates
- [`../pipeline/README.md`](../pipeline/README.md) — valid agent order
- [`../memory/README.md`](../memory/README.md) — handoff contract
- [`../doctor/README.md`](../doctor/README.md) — structural validation
