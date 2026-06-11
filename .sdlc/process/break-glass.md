# SDLC Break-Glass Policy

> **Scope:** Emergency bypass of fail-closed hooks and workflow enforcement flags only.

## When allowed

- Active **SDLC_META** Plane card documenting the incident, owner, and rollback plan.
- Time-boxed change; revert break-glass as soon as the gate can be restored.

## How to activate

**Write gates (protected paths):** set `core.gates.enforcement: off` in `.sdlc/sdlc.yaml`, or:

```bash
python3 .sdlc/dsl/cli.py workflow gates off
# session-only:
export SDLC_GATES=off
```

**CLI workflow flags** (force start, skip plane, etc.):

```bash
export SDLC_BREAK_GLASS=1
```

Then run the guarded CLI flag (`workflow start --force`, `--skip-*`, etc.). The process prints a stderr audit warning.

## What break-glass does **not** bypass

- Plane as workboard source of truth.
- Merge without green CI + Reviewer approval (unless a separate human-approved exception is recorded on the card).
- Writing product code without an open implementation gate on a product child card **when `core.gates.enforcement` is `strict`** (default). Use `core.gates.enforcement: off` or `workflow gates off` for structural pivots instead.

## Audit trail

1. Note `SDLC_BREAK_GLASS=1` usage in the SDLC_META card description or comment.
2. Reference card id in the commit/PR body.
3. Close the card when enforcement is restored.

Implementation: `.sdlc/dsl/break_glass.py`.
