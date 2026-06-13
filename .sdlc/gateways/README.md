# Gateways Module

> **Policy:** [`policy.yaml`](policy.yaml) · **Hooks:** `.cursor/hooks/sdlc_pre_gateway.py`, `.cursor/hooks/sdlc_post_gateway.py` · **Write gate:** [`../gates/paths.yaml`](../gates/paths.yaml) · [`../process/lifecycle-model.yaml`](../process/lifecycle-model.yaml) → `write_policy`

## Purpose

Deterministic quality harness around agent interactions. Gateways evaluate what is about to happen and what just happened, then allow, deny, or route the agent back to the previous step when required evidence is missing.

Mechanical **write permissions** by SDLC stage are documented in [Write gate (mechanical ACL)](#write-gate-mechanical-acl) below.

## When to read

| Situation | File |
|-----------|------|
| Hook denies or redirects a step | `policy.yaml` |
| Need to understand pre-execution checks | `.cursor/hooks/sdlc_pre_gateway.py` |
| Need to understand post-step checks | `.cursor/hooks/sdlc_post_gateway.py` |
| Handoff validation fails | `../memory/README.md` |
| Before editing `app/` or `.sdlc/` | [Write gate (mechanical ACL)](#write-gate-mechanical-acl) below |
| Hook blocked your Write | `../gates/paths.yaml` → `gate_paths.stages.<stage>.allowed_prefixes` |

## Write gate (mechanical ACL)

> **Data:** [`../gates/paths.yaml`](../gates/paths.yaml) · **Config:** `.sdlc/sdlc.yaml` → `core.gates.enforcement` · **Runtime:** `.sdlc/dsl/gate.py` + `.cursor/hooks/sdlc_gate_hook.py`

Canonical policy: [`../process/lifecycle-model.yaml`](../process/lifecycle-model.yaml) → `write_policy`. Generated view: [`../gates/paths.yaml`](../gates/paths.yaml) (run `python .sdlc/scripts/sdlc_sync_model.py --write`).

### When to read (write gate)

| Situation | Action |
|-----------|--------|
| Before editing `app/` | Confirm `session-gate.json` → `gate_status: open` and stage = `implementation` |
| SDLC_META work on `.sdlc/` | Stage must be `sdlc_meta` or `planning` |
| Structural repo pivot (greenfield, rename, pyproject) | Set `core.gates.enforcement: off` (see below) |
| Hook blocked your Write | Read `paths.yaml` → `gate_paths.stages.<stage>.allowed_prefixes` |
| Starting work | `python3 .sdlc/dsl/cli.py workflow start --card RPG-N --slug … --stage implementation` |

### Disable gate checks (structural work)

When repivoting the repository, renaming modules, or editing paths that no stage covers (`pyproject.toml` during SDLC_META, bulk `app/` cleanup), turn enforcement **off** in `.sdlc/sdlc.yaml`:

```yaml
core:
  gates:
    enforcement: off   # strict | off
```

Or via CLI (writes the same field):

```bash
python3 .sdlc/dsl/cli.py workflow gates off
python3 .sdlc/dsl/cli.py workflow gates status
python3 .sdlc/dsl/cli.py workflow gates strict   # re-enable when done
```

**Session-only override** (does not edit YAML):

```bash
$env:SDLC_GATES="off"   # PowerShell
export SDLC_GATES=off   # bash
```

Document usage on a Plane **SDLC_META** card and run `workflow gates strict` before resuming normal feature work.

### Protected prefixes (when enforcement is strict)

From `paths.yaml` → `gate_paths.protected_prefixes`:

- `app/backend/`, `app/frontend/`, `app/shared/`
- `pyproject.toml`

### Stage → allowed paths (summary)

| Stage | Typical allowed prefixes |
|-------|--------------------------|
| `planning` | `.sdlc/`, `.cursor/` |
| `architecture` | same as planning |
| `implementation` | `app/**`, `pyproject.toml`, `data/` |
| `sdlc_meta` | `.sdlc/`, `.cursor/`, `.github/`, `Makefile`, `AGENTS.md` |
| `validation` / `review` | read-heavy; see YAML for exceptions |

### Commands

```bash
python3 .sdlc/scripts/sdlc_gate.py status
python3 .sdlc/scripts/sdlc_gate.py check --path app/backend/src/foo.py
python3 .sdlc/scripts/sdlc_gate.py enforcement off
python3 .sdlc/dsl/cli.py workflow status
python3 .sdlc/dsl/cli.py workflow gates status
```

### Do not

- Leave `enforcement: off` during normal feature delivery
- Open gate on an **epic** card — only **child** cards (`RPG-N` with `[AI][BACKEND]` etc.)

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
| `../gates/paths.yaml` | Generated write ACL view (shim; canonical source is lifecycle-model) |

## Boundaries

- This module defines deterministic harness policy only.
- Write permission is enforced by `lifecycle-model.yaml` → `write_policy` and `sdlc_gate_hook.py` (generated view: `.sdlc/gates/paths.yaml`).
- Plane remains the source of truth for work items and evidence.
- Hooks are **fail-closed** (`failClosed: true` in `.cursor/hooks.json`). If `policy.yaml` or PyYAML is missing, pre/post gateways deny.
- Emergency bypass: set `SDLC_BREAK_GLASS=1` and document on a Plane **SDLC_META** card before using `workflow start --force`, `--skip-plane`, `--skip-validate`, or `auto_merge_pr.py --skip-ci-wait`.

## Related modules

- [`../gates/README.md`](../gates/README.md) — redirect stub; `paths.yaml` shim only
- [`../gates/paths.yaml`](../gates/paths.yaml) — generated write ACL
- [`../pipeline/README.md`](../pipeline/README.md) — valid agent order
- [`../memory/README.md`](../memory/README.md) — handoff contract and `session-gate.json`
- [`../workboard/README.md`](../workboard/README.md) — Plane card must be In Progress before `workflow start`
- [`../workflows/README.md`](../workflows/README.md) — stage transitions
- [`../doctor/README.md`](../doctor/README.md) — structural validation
- [`../process/break-glass.md`](../process/break-glass.md) — CLI flag bypass (`SDLC_BREAK_GLASS=1`), not write gates
