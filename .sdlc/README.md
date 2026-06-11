# .sdlc — SDLC Operating System (v5.2)

> **You are here:** the machine-readable root of the SDLC. Start at [`sdlc.yaml`](sdlc.yaml), then open the module README for your task.

## Who should read this

| Role | Start here | Then open |
|------|------------|-----------|
| **Orchestrator** (chat agent) | [`AGENTS.md`](../AGENTS.md) | [`memory/orchestrator-handoff.md`](memory/orchestrator-handoff.md), [`pipeline/`](pipeline/README.md) |
| **Intent Analyst** | [`memory/discovery-context.json`](memory/discovery-context.json) | [`workboard/`](workboard/README.md) |
| **Planner / Architect** | [`workboard/granularity.yaml`](workboard/granularity.yaml) | [`stages/definitions.yaml`](stages/definitions.yaml) |
| **Implementer** | [`gates/paths.yaml`](gates/paths.yaml) | [`memory/session-gate.json`](memory/session-gate.json) — gate must be **open** |
| **QA / Doctor** | [`doctor/checks.yaml`](doctor/checks.yaml) | run `make sdlc-doctor` |
| **Any agent** | This file | module README below |

## Loading order (mandatory)

1. [`AGENTS.md`](../AGENTS.md) — L0 decision tree (alwaysApply rules)
2. [`process/master-workflow.md`](process/master-workflow.md) + [`process/change-lifecycle.md`](process/change-lifecycle.md) — process authority
3. **[`sdlc.yaml`](sdlc.yaml)** — `core` (vendors, env, paths) + `contract.modules` (module map)
4. **Module README** for the area you will touch (table below)
5. **Module data YAML** referenced by that README

## Module map

Each folder is a **vendor-free module**. README = human/agent index; YAML = machine data.

| Module | README (read first) | Data file(s) | Answers the question |
|--------|---------------------|--------------|----------------------|
| **Manifest** | [`manifest/README.md`](manifest/README.md) | [`manifest/catalog.yaml`](manifest/catalog.yaml) | Which agents, skills, MCPs exist? |
| **Stages** | [`stages/README.md`](stages/README.md) | [`stages/lifecycle.yaml`](stages/lifecycle.yaml), [`stages/definitions.yaml`](stages/definitions.yaml) | What are the 10 lifecycle stages and their evidence? |
| **Gates** | [`gates/README.md`](gates/README.md) | [`gates/paths.yaml`](gates/paths.yaml) | Which paths are writable per stage? Is `app/` blocked? |
| **Gateways** | [`gateways/README.md`](gateways/README.md) | [`gateways/policy.yaml`](gateways/policy.yaml) | Should this interaction advance, block, or return to a previous step? |
| **Workboard** | [`workboard/README.md`](workboard/README.md) | [`workboard/granularity.yaml`](workboard/granularity.yaml) | Epic vs child cards? Min layers for FEATURE? |
| **Pipeline** | [`pipeline/README.md`](pipeline/README.md) | [`pipeline/agents.yaml`](pipeline/agents.yaml) | Which agent runs at which stage? |
| **Workflows** | [`workflows/README.md`](workflows/README.md) | [`workflows/transitions.yaml`](workflows/transitions.yaml) | Valid stage transitions and preconditions |
| **Rules** | [`rules/README.md`](rules/README.md) | [`rules/governance.yaml`](rules/governance.yaml) | Governance data + link to `.cursor/rules/` |
| **Integrations** | [`integrations/README.md`](integrations/README.md) | [`integrations/services.yaml`](integrations/services.yaml) | Plane, GitHub, LLM env vars and roles |
| **Doctor** | [`doctor/README.md`](doctor/README.md) | [`doctor/checks.yaml`](doctor/checks.yaml) | Structure validation checks |
| **Memory** | [`memory/README.md`](memory/README.md) | `memory/*` (runtime) | Session state, handoff, ADR summary |
| **Scripts** | [`scripts/README.md`](scripts/README.md) | `scripts/*` | Deterministic SDLC automation |
| **Templates** | [`templates/README.md`](templates/README.md) | [`templates/plane/`](templates/plane/README.md), [`templates/planner/`](templates/planner/README.md) | Plane evidence examples and planner output templates |
| **Process** | [`process/README.md`](process/README.md) | [`process/master-workflow.md`](process/master-workflow.md), [`process/change-lifecycle.md`](process/change-lifecycle.md) | Minimal workflow and change authority |

## Viability Matrix

Use this table before deleting, moving, or merging anything under `.sdlc/`.

| Folder | Class | Primary consumers | Recommendation |
|--------|-------|-------------------|----------------|
| `doctor/` | `runtime-critical`, `machine-data` | `dsl/doctor.py`, CI, `make sdlc-doctor` | **keep** — validates structure |
| `dsl/` | `runtime-critical` | Makefile, workflow CLI, hooks, Doctor | **keep** — Python runtime |
| `gates/` | `runtime-critical`, `machine-data` | `dsl/gate.py`, `sdlc_gate_hook.py` | **keep** — write enforcement |
| `gateways/` | `runtime-critical`, `machine-data` | Cursor pre/post hooks, Orchestrator | **keep** — deterministic step harness |
| `integrations/` | `machine-data` | `loader.py`, Doctor env warnings, DevOps docs | **keep** — vendor roles and env mapping |
| `manifest/` | `machine-data`, `agent-procedure` | agents, skills, `loader.load_skills()` | **keep** — catalog/phonebook |
| `memory/` | `runtime-state`, `agent-context` | Orchestrator, hooks, `workflow.py`, agents | **keep** — see memory policy |
| `pipeline/` | `machine-data` | `loader.py`, `validator.py` | **keep** — stage-to-agent binding |
| `process/` | `agent-procedure`, `human-reference` | Agents, humans, rules, skills | **keep** — process authority |
| `rules/` | `machine-data`, `agent-procedure` | `loader.py`, Doctor, `.cursor/rules/` | **keep** — governance index |
| `scripts/` | `runtime-critical` | Makefile, workflow CLI, Plane/GitHub automation | **keep** — deterministic execution |
| `stages/` | `machine-data` | `loader.py`, `validator.py`, commands | **keep** — lifecycle contracts |
| `templates/` | `human-reference`, `agent-procedure` | Plane evidence flow, review/validation stages | **keep** — examples/templates, not source of truth |
| `workboard/` | `runtime-critical`, `machine-data` | `plane_granularity.py`, `plane_card.py` | **keep** — Plane granularity |
| `workflows/` | `machine-data` | `loader.py`, `validator.py`, docs | **keep** — declarative transition graph |

## Toolchain (Python DSL)

| Tool | Path | CLI |
|------|------|-----|
| Loader | `.sdlc/dsl/loader.py` | resolves v5 modular YAML |
| Gate | `.sdlc/dsl/gate.py` | `python3 .sdlc/scripts/sdlc_gate.py status` |
| Workflow | `.sdlc/dsl/workflow.py` | `python3 .sdlc/dsl/cli.py workflow …` |
| Doctor | `.sdlc/dsl/doctor.py` | `make sdlc-doctor` |
| Workboard | `.sdlc/dsl/plane_granularity.py` | used by `plane_card.py validate-all` |

## Commands

```bash
make sdlc-doctor       # structure checks + health Canvas + doctor-health.json
make sdlc-validate     # YAML consistency
make sdlc-stages       # list lifecycle stages
make sdlc-compact-memory  # rolling-summary protocol
python3 .sdlc/dsl/cli.py workflow status   # gate + handoff preview
```

## Runtime artifacts (not module data)

| Artifact | Location | Purpose |
|----------|----------|---------|
| Session gate | `.sdlc/memory/session-gate.json` | Mechanical write lock (gitignored) |
| Handoff | `.sdlc/memory/orchestrator-handoff.md` | **Markdown** routing between agents |
| Doctor health | `.sdlc/memory/doctor-health.json` | Last doctor run summary |
| Health Canvas | `~/.cursor/.../sdlc-doctor-health.canvas.tsx` | Visual doctor report |

## Canonical structure checks

The v5.2 layout is **modular only**. The Doctor fails if legacy flat YAML files
come back at `.sdlc/` root (`manifest.yaml`, `pipeline.yaml`, `stages.yaml`,
`gate-paths.yaml`, etc.).

The old migration helper at `.sdlc/scripts/migrate_v5_modular.py` is retired and
exits with an error. It must not be used to regenerate README files or rewrite
module data. Update the target module directly and run `make sdlc-doctor`.

## Canvases (IDE)

- **Doctor health** — regenerated every `make sdlc-doctor`
- **FEATURE flow** — reference simulation canvas (optional)

## Do not

- Edit flat legacy paths (`manifest.yaml`, `pipeline.yaml` at root) — v5 uses **module folders**
- Write `app/` without open gate on a child Plane card
- Put handoff content inside YAML fences — use **Markdown sections** (see [`memory/README.md`](memory/README.md))
