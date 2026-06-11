# MVP Readiness Loop Prototype

Deterministic readiness loop for `INVES-74` (roadmap phase 10). Evaluates Studio modules, CLI commands, and documentation against the MVP checklist without running Doctor, pytest, CI, Plane, or GitHub. Roadmap: `docs/roadmap/sdlc-studio-mvp-roadmap.md`.

Pipeline: compile → validate → canvas → validation_inspection → workflow_assistance → simulation_preview → publish_evidence → readiness checks.

CLI:

```bash
python -m studio.cli check-readiness [--format text|json] [--root PATH]
```

Output: `readiness` (`derived_non_authoritative`, `execution_mode=non_executing_readiness_loop`), `summary` (`mvp_ready`, pass/warn/fail counts), `checks` (compiler, validator, canvas, inspection, assistance, simulation, publish-evidence, operating model, CLI surface), and `cli_commands`.

Non-goals: no Doctor/pytest/CI execution, no Plane/GitHub mutation, no persistence, no authoritative MVP declaration. Implementation: `studio/mvp_readiness.py`.
