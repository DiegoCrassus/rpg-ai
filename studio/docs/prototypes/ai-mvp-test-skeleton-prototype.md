# MVP Test Skeleton Prototype

Traceability plan for `INVES-75` (roadmap phase 10). Maps epic `INVES-53` MVP phases and consolidated validation gates to planned validation approaches without running pytest, Doctor, CI, Plane, or GitHub. Roadmap: `docs/roadmap/sdlc-studio-mvp-roadmap.md`.

CLI:

```bash
python -m studio.cli list-skeleton [--format text|json]
```

Output: `skeleton` (`derived_non_authoritative`, `execution_mode=non_executing_traceability_plan`), `summary` (`entry_count`, `phase_count`, `validation_types`, `cards_referenced`, `execution_claimed=false`), and `entries` (phase, Plane card IDs, area, validation types, acceptance-criteria ref, `status=planned`).

Validation types: `automated`, `manual_review`, `cli`, `docs_review`, `doctor_gate`.

Non-goals: no pytest/doctor/CI execution, no pass/fail claims, no Plane/GitHub mutation, no persistence. Implementation: `studio/mvp_test_skeleton.py`. Memory mirror: `.sdlc/memory/test-skeleton.md`.
