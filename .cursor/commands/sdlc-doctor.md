# Command: SDLC Doctor

## Purpose

Run the SDLC Doctor to validate repository structure, YAML consistency, docs, Cursor configuration, and app boundaries.

## When to Use

- After any structural change (new directories, YAML files, Cursor config changes)
- Before a major stage transition
- When unsure if the repository is in a valid state
- As a first step when starting work on an existing codebase

## Procedure

1. Run the Doctor:
   ```bash
   make sdlc-doctor
   ```
   Or directly:
   ```bash
   python .sdlc/dsl/cli.py doctor
   ```

2. Read the output carefully:
   - `[PASS]` — check passed, no action needed
   - `[WARN]` — non-critical gap, review and decide if it needs addressing
   - `[FAIL]` — required check failed, must be fixed before proceeding

3. For each `[FAIL]`:
   - Identify what is missing or invalid.
   - Create the missing file/directory, or fix the invalid content.
   - Do not suppress failures by editing Doctor rules.

4. Re-run after fixes:
   ```bash
   make sdlc-doctor
   ```

5. Confirm exit code `0` before proceeding.

## Checks Performed

- Required directories exist (`.cursor/`, `.sdlc/`, `docs/`, `app/`)
- Required SDLC YAML files exist and parse correctly
- Cursor configuration files exist (rules, commands, skills, subagents, hooks)
- Docs exist and are non-empty
- Makefile targets exist
- Integration env vars configured (warnings only)

## Output Format

```
[PASS] Required directory exists: .cursor
[PASS] Required file exists: .sdlc/sdlc.yaml
[FAIL] Missing file: docs/handoff/current-state.md
[WARN] Integration not configured: github (GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC not set)

Doctor summary: 42 passed, 3 warnings, 1 failed
```

## On Success

Report: "Doctor passed. Repository structure is valid."

## On Failure

Report: "Doctor failed. N required checks did not pass."
List the failures and proposed fixes.
Do not proceed to other tasks until Doctor exits 0.
