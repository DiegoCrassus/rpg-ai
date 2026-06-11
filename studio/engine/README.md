# Studio engine

Deterministic, **in-memory** Foundation engine: compile `.sdlc/` + `.cursor/` into derived IR, validate, build canvas view models, and expose CLI helpers.

## Layout

```text
engine/
├── cli.py                 # `python -m studio.cli` (via ../cli.py shim)
├── compiler_core.py       # Graph + workflow IR compilation
├── validator_core.py      # Structural validation
├── canvas_view_model.py   # Derived canvas for React Flow
├── validation_inspection.py
├── workflow_assistance.py
├── simulation_preview.py
├── publish_evidence.py
├── mvp_readiness.py
├── schemas/               # Descriptive YAML contracts
└── tests/                 # pytest suite
```

## Run

From repository root:

```bash
python -m studio.cli compile
python -m studio.cli validate
python -m studio.cli canvas
pytest studio/engine/tests/ -q
```

## Import surface

- **Public facade:** `from studio import compile_studio_sources` (re-exported from `studio.engine`)
- **Explicit:** `from studio.engine.compiler_core import compile_studio_sources`

## Boundaries

- Read-only over authoritative repo paths; no persistence under `studio/engine/generated/` or `specs/`
- Does not call Plane, GitHub, or Cursor APIs
