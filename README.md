# RPG AI

AI-native SDLC operating system and **RPG Platform** (campaign management MVP).

## Repository layout

| Path | Purpose |
|------|---------|
| `app/` | Product code — backend API, shared contracts, Supabase infra |
| `docs/product/` | RPG Platform product specs (frozen for MVP) |
| `.sdlc/` | SDLC machine index, workflow CLI, Doctor |
| `.cursor/` | Cursor agents, hooks, skills |
| `studio/` | SDLC Studio Service (control plane UI + API) |

## Quick start

```bash
cp .env.example .env   # fill Supabase, Plane, GitHub tokens
pip install -e ".[dev]"
make sdlc-doctor
pytest app/backend/tests app/shared/tests -q
```

Local Supabase: `make supabase-start` (requires Docker + Supabase CLI).

## SDLC entry

See [`AGENTS.md`](AGENTS.md) and [`.sdlc/process/change-lifecycle.md`](.sdlc/process/change-lifecycle.md).
