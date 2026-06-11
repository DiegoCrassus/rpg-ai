# Hook: Post-Task

## Purpose

Summarize what changed, update docs if needed, run Doctor if structure changed, and record unresolved risks.

## When to Execute

After completing any non-trivial task.

## Procedure

### 1. Summarize Changes

List:
- Files created, modified, or deleted
- Reason for each change
- What acceptance criteria were satisfied

### 2. Update Docs If Needed

Check rules from `.cursor/rules/030-docs-and-handoff.mdc`:
- Did architecture change? → Update `docs/architecture/overview.md`
- Did infrastructure change? → Update `docs/infrastructure/` as needed
- Did a public interface change? → Update relevant API docs
- Is this a major stage transition? → Update `docs/handoff/current-state.md`

### 3. Run Doctor If Structure Changed

If any of the following changed:
- Top-level directory structure
- `.sdlc/*.yaml` files
- `.cursor/` configuration files
- `Makefile` structure

Then run:
```bash
make sdlc-doctor
```

Record the result (exit code and summary line).

### 4. Record Unresolved Risks

If any of the following are true:
- A known risk was not mitigated
- An assumption was not verified
- A test was deferred

Document them explicitly. Do not silently omit risks.

### 5. State Next Step

What should happen next?
- Which stage follows?
- Which agent should act?
- Is human review required?

### 6. Emit observability metric (Observer)

Close the metrics run with actual outcomes:

**Automático:** `.cursor/hooks.json` chama `sdlc_obs_session.py post` em `stop`.

**Manual:**

```bash
python3 app/infra/sdlc_obs/hooks/post_task.py \
  --status    <completed|failed|escalated|abandoned> \
  --tokens-in <N> --tokens-out <N> \
  --cost      <USD>  \
  --tools-total <N> --tools-ok <N> --tools-fail <N> \
  --tests-pass  <N> --tests-fail <N> \
  --doctor    <0|1|not_run>
  # add --hallucination if fabricated result was detected
  # add --regression   if Doctor/tests failed after claimed success
```

**Hallucination flag rules** — add `--hallucination` if:
- Agent said "Doctor passed" but actual exit code was `1`
- Agent said "tests pass" but actual `tests_failed > 0`
- Agent cited a file or result that does not exist

**Regression flag rules** — add `--regression` if:
- Doctor exit code is `1` after a change marked as complete
- Tests fail after a change marked as complete

## Output of This Hook

A post-task summary:
```
Files changed: <list>
Docs updated: <list or none>
Doctor result: PASS (N passed, N warnings) | FAIL (N failed) | not run
Unresolved risks: <list or none>
Next step: <description>
Obs: run closed → <status> | cost $X.XXXX | tools N/N | doctor <0|1>
```
