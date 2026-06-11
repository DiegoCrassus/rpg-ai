# MVP Test Skeleton (RPG-75)

Traceability plan for epic **RPG-53** — derived, non-executing. Source module: `studio/mvp_test_skeleton.py`. No pass/fail results are claimed here.

## Acceptance criteria (RPG-75)

1. Each MVP phase has at least one planned validation approach.
2. Skeleton references Plane child card IDs and acceptance criteria.
3. Skeleton distinguishes automated tests, manual review, CLI checks, docs review, and doctor gate.
4. No test results are claimed before execution (`execution_claimed: false`).

## Validation types

| Type | Purpose |
|------|---------|
| `automated` | Future pytest/unit coverage on scoped card |
| `manual_review` | Human reviewer sign-off on derived outputs |
| `cli` | `python -m studio.cli` deterministic checks |
| `docs_review` | English docs and source-of-truth boundaries |
| `doctor_gate` | `make sdlc-doctor` structural gate |

## Phase entries

| Phase | ID | Cards | Types |
|-------|-----|-------|-------|
| 1 Foundation | `skeleton.phase.foundation` | RPG-54, RPG-55 | docs_review, manual_review |
| 2 Registry | `skeleton.phase.registry` | RPG-56, RPG-57 | automated |
| 3 Graph IR | `skeleton.phase.graph_ir` | RPG-58, RPG-59 | automated, docs_review |
| 4 Compiler/validator | `skeleton.phase.compiler_validator` | RPG-60–62 | automated, cli |
| 5 CLI | `skeleton.phase.cli` | RPG-63, RPG-64 | cli, automated |
| 6 Visual | `skeleton.phase.visual` | RPG-65–67 | automated, manual_review |
| 7 AI | `skeleton.phase.ai` | RPG-68, RPG-69 | automated, cli, manual_review |
| 8 Simulation | `skeleton.phase.simulation` | RPG-70, RPG-71 | automated, cli |
| 9 Publish | `skeleton.phase.publish` | RPG-72, RPG-73 | cli, docs_review |
| 10 Readiness | `skeleton.phase.readiness` | RPG-74, RPG-75 | cli, automated |

## Consolidated gates

| ID | Cards | Types |
|----|-------|-------|
| `skeleton.gate.registry_schema` | RPG-56–59 | automated |
| `skeleton.gate.compiler_validator` | RPG-61, RPG-62 | automated, cli |
| `skeleton.gate.cli` | RPG-63, RPG-64 | cli |
| `skeleton.gate.preview_simulation` | RPG-70, RPG-71 | cli, automated |
| `skeleton.gate.docs_review` | RPG-55, RPG-73 | docs_review, manual_review |
| `skeleton.gate.doctor` | RPG-74 | doctor_gate |

## Pytest stubs

Skipped placeholders live in `studio/test_mvp_skeleton.py` (`test_mvp_skeleton_future_validation`). Executable meta-tests verify skeleton shape only.

## CLI

```bash
python -m studio.cli list-skeleton [--format text|json]
```
