# Hook: Pre-Task

## Purpose

Load SDLC context, identify lifecycle stage, check relevant docs and memory, and define expected output before any task begins.

## When to Execute

Before starting any non-trivial task (feature, fix, refactor, investigation).

## Procedure

### 1. Load SDLC Configuration

```
Read: .sdlc/sdlc.yaml
```

Confirm the project name, version, and referenced files are accessible.

### 2. Identify the Lifecycle Stage

Determine which stage this task belongs to:
- ticket | requirements | architecture | implementation | validation | review | deployment | observability | incident | autofix

Load the corresponding stage definition from `.sdlc/stages/definitions.yaml`.

### 3. Load Memory Context

Load the relevant memory files:
```
Read: .sdlc/memory/architecture.md
Read: .sdlc/memory/business-rules.md
Read: .sdlc/memory/operational-context.md
```

If the task involves an incident, also read:
```
Read: .sdlc/memory/incidents.md
```

### 4. Load Relevant Docs

Based on the stage, load:
- Architecture tasks → `docs/architecture/overview.md`
- Infrastructure tasks → `docs/infrastructure/overview.md`
- Deployment tasks → `docs/infrastructure/deployment.md`
- Observability tasks → `docs/operations/observability.md`

### 5. Define Expected Output

Before acting, state explicitly:
- What this task will produce
- Which files will change
- Which acceptance criteria are being satisfied
- Whether Doctor will need to run after

### 6. Check Governance Rules

Read `.sdlc/rules/governance.yaml` and confirm:
- No broad rewrites are planned
- Assumptions are documented
- Docs will be updated if required

### 7. Emit observability metric (Observer)

Open a metrics run before the task starts:

**Automático:** `.cursor/hooks.json` chama `sdlc_obs_session.py pre` em `sessionStart`.

**Manual** (tarefas com stage/agent específicos):

```bash
python3 app/infra/sdlc_obs/hooks/pre_task.py \
  --task  "<task_name with [AI][TYPE] prefix>" \
  --stage <stage_id> \
  --agent <agent_id> \
  --tags  "[AI]" "[TYPE]"
```

This records the start time in `app/infra/sdlc_obs/data/sdlc_obs.db`
and writes the run_id to `.sdlc_obs_state.json` for `post_task.py` to pick up.

If the hooks directory or DB is not initialized, run `make obs-init` first.

## Output of This Hook

A pre-task context summary:
```
Stage: <stage id>
Expected output: <description>
Files in scope: <list>
Docs to update: <list or none>
Doctor required after: yes | no
Assumptions: <list or none>
Obs run_id: <uuid written to .sdlc_obs_state.json>
```
