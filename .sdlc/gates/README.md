# Gates module

> **Data:** [`paths.yaml`](paths.yaml) · **Config:** `.sdlc/sdlc.yaml` → `core.gates.enforcement` · **Runtime:** `.sdlc/dsl/gate.py` + `.cursor/hooks/sdlc_gate_hook.py`

## Purpose

Mechanical **write permissions** by SDLC stage. The pre-write hook (`sdlc_gate_hook.py`) denies edits **only** on `protected_prefixes` when the session gate is **closed** or the stage does not allow the path. Unprotected paths (e.g. `docs/`) are always allowed. Malformed Cursor hook payloads are treated as allow when the path is unknown.

## When to read

| Situation | Action |
|-----------|--------|
| Before editing `app/` | Confirm `session-gate.json` → `gate_status: open` and stage = `implementation` |
| SDLC_META work on `.sdlc/` | Stage must be `sdlc_meta` or `planning` |
| Structural repo pivot (greenfield, rename, pyproject) | Set `core.gates.enforcement: off` (see below) |
| Hook blocked your Write | Read `paths.yaml` → `gate_paths.stages.<stage>.allowed_prefixes` |
| Starting work | `python3 .sdlc/dsl/cli.py workflow start --card RPG-N --slug … --stage implementation` |

## Disable gate checks (structural work)

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

## Protected prefixes (when enforcement is strict)

From `paths.yaml` → `gate_paths.protected_prefixes`:

- `app/backend/`, `app/frontend/`, `app/shared/`
- `pyproject.toml`

## Stage → allowed paths (summary)

| Stage | Typical allowed prefixes |
|-------|--------------------------|
| `planning` | `.sdlc/`, `.cursor/` |
| `architecture` | same as planning |
| `implementation` | `app/**`, `pyproject.toml`, `data/` |
| `sdlc_meta` | `.sdlc/`, `.cursor/`, `.github/`, `Makefile`, `AGENTS.md` |
| `validation` / `review` | read-heavy; see YAML for exceptions |

## Related modules

- [`../memory/README.md`](../memory/README.md) — `session-gate.json` fields (`card`, `branch`, `stage`)
- [`../gateways/README.md`](../gateways/README.md) — deterministic pre/post interaction harness
- [`../workboard/README.md`](../workboard/README.md) — Plane card must be In Progress before `workflow start`
- [`../workflows/README.md`](../workflows/README.md) — stage transitions
- [`../process/break-glass.md`](../process/break-glass.md) — CLI flag bypass (`SDLC_BREAK_GLASS=1`), not write gates

## Commands

```bash
python3 .sdlc/scripts/sdlc_gate.py status
python3 .sdlc/scripts/sdlc_gate.py check --path app/backend/src/foo.py
python3 .sdlc/scripts/sdlc_gate.py enforcement off
python3 .sdlc/dsl/cli.py workflow status
python3 .sdlc/dsl/cli.py workflow gates status
```

## Do not

- Leave `enforcement: off` during normal feature delivery
- Open gate on an **epic** card — only **child** cards (`RPG-N` with `[AI][BACKEND]` etc.)
