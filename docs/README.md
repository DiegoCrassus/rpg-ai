# docs — Human-Readable Project Documentation

Documentation for the **RPG Platform** project.

## Structure

| Directory         | Purpose                                  |
|-------------------|------------------------------------------|
| `product/`        | **RPG Platform** product specs (active)  |
| `architecture/`   | RPG Platform architecture + ADRs         |
| `infrastructure/` | Deployment and environment setup         |
| `handoff/`        | State summaries and transitions          |
| `roadmap/`        | Planned work (includes legacy SDLC docs) |
| `operations/`     | Observability, incidents, maintenance    |

## Product docs

Start at [`product/README.md`](./product/README.md).

## Conventions

- Docs reflect **current state**, not aspirational state.
- Use "TBD" for undecided content — do not leave empty sections.
- ADRs go in `architecture/decisions.md`.
- SDLC process lives under `.sdlc/`, not `docs/`.
