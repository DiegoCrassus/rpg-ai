# Studio Architecture

SDLC Studio is a **self-contained framework** under `studio/`. It complements the SDLC operating system (`.sdlc/`, `.cursor/`) and is separate from MarketPulse product code (`app/`).

## Package layout

```text
studio/
├── README.md              # Navigation index
├── ARCHITECTURE.md        # This file — layout and dependency rules
├── Makefile               # Local test/dev shortcuts
├── cli.py                 # CLI shim (`python -m studio.cli`)
│
├── docs/                  # Human documentation (non-executable)
│   ├── boundaries/        # Inventories, operating model, source boundaries
│   ├── contracts/         # IR contracts, compiler/validator boundaries
│   └── prototypes/        # AI assistance prototype specs
│
├── engine/                # Foundation Python engine
│   ├── cli.py             # Compile, validate, canvas, readiness CLIs
│   ├── compiler_core.py
│   ├── validator_core.py
│   ├── schemas/           # Descriptive YAML contracts
│   └── tests/
│
├── backend/               # Studio Service API (FastAPI, studio_service)
└── frontend/              # Studio Service UI (React + Vite)
```

## Dependency rules

| Layer | May import | Must not |
|-------|------------|----------|
| `engine/` | stdlib, PyYAML, repo files at `--root` | `studio_service`, React, `marketpulse` |
| `backend/` | `studio.engine.*`, `app/infra/sdlc_obs` | `marketpulse`, silent repo writes |
| `frontend/` | `/studio/*` HTTP API | Foundation Python, Cursor runtime |
| `docs/` | — | Executable code |

**Authority:** `.sdlc/` and `.cursor/` remain source of truth. Studio derives, previews, and proposes — it does not replace Plane, GitHub, or Cursor.

## Shared infrastructure

- **Observability DB:** `app/infra/sdlc_obs/` (used by backend + gateway hooks; not Studio-owned)
- **Registry index:** `.sdlc/registry/` references `studio/engine/schemas/`

## Commands

```bash
make -C studio test          # engine + backend unit tests
python -m studio.cli compile # Foundation CLI (from repo root)
make studio-dev              # API + UI (root Makefile)
```
