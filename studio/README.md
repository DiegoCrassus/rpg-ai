# SDLC Studio

Self-contained framework that complements the SDLC operating system. **Not** MarketPulse (`app/`).

```text
studio/
├── docs/       boundaries, contracts, prototypes (human docs)
├── engine/     Foundation: compile, validate, canvas, CLI
├── backend/    Studio Service API (:8100)
└── frontend/   Studio Service UI (:5174)
```

## Quick start

```bash
cd studio/frontend && npm install   # once
make studio-dev                     # from repo root
```

## Navigation

| Path | Purpose |
|------|---------|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Layout, dependency rules, commands |
| [`docs/README.md`](docs/README.md) | Boundary docs and IR contracts |
| [`engine/README.md`](engine/README.md) | Compiler, validator, CLI |
| [`backend/README.md`](backend/README.md) | FastAPI control plane |
| [`frontend/README.md`](frontend/README.md) | React SPA |

## CLI (Foundation)

```bash
python -m studio.cli compile
python -m studio.cli validate
python -m studio.cli check-readiness
```

## Tests

```bash
make -C studio test
# or
pytest studio/engine/tests/ -q
```

## Authority

`.sdlc/` and `.cursor/` are source of truth. Studio derives and proposes; apply happens via Plane → branch → PR.
