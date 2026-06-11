# AI Simulation Preview Prototype

Non-executing lifecycle preview for `INVES-70` / `INVES-71` (roadmap phase 8). Walks derived workflow IR and process authority without running agents, gates, or external systems. Roadmap: `docs/roadmap/sdlc-studio-mvp-roadmap.md`.

Pipeline: compile → validate → canvas → validation_inspection → simulation_preview.

CLI:

```bash
python -m studio.cli preview-simulation [--format text|json] [--root PATH] \
  [--scenario SCENARIO] [--intent DOCS_ONLY|FEATURE] \
  [--path-label expected|blocked|unsupported] \
  [--step-kind handoff|stage|transition] [--tag TAG]
```

Output: `simulation` (`derived_non_authoritative`, `execution_mode=non_executing_preview`), `summary`, `scenarios`, `lifecycle_map`.

Each scenario includes `description`, `tags`, `outcome`, `evidence_expectations`, and `source_refs`. Steps carry `path_label` (expected|blocked|unsupported), optional `exit_criteria`, handoff routing, and lifecycle `source_refs`.

Scenario ids: `docs_only`, `feature_implementation`, `qa_failure`, `reviewer_escalation`, `devops_finish`. Tags: `docs_scope`, `failure_path`, `finish_flow`, `gate_blocked`, `happy_path`, `human_escalation`.

Non-goals: no execution, agents, MCP, persistence, or live gate status. Implementation: `studio/simulation_preview.py`.
