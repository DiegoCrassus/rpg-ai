# Architecture Overview

## Current Status

**Phase:** **RPG Platform** — architecture defined; implementation pending (Plane epic TBD).

The SDLC operating system remains production-ready. **Investment Radar** docs are legacy; active product is **RPG Platform** (campaign management).

| Product | Status | Architecture |
|---------|--------|--------------|
| **RPG Platform** | Active — MVP planning | [rpg-platform-overview.md](./rpg-platform-overview.md) |
| Investment Radar | Legacy / superseded | [investment-radar-api.md](./investment-radar-api.md) |
| Studio Service | SDLC control plane | [studio-service-platform.md](./studio-service-platform.md) |

## System Boundaries

```
rpg-ai/
├── app/
│   ├── frontend/     ← React + Vite + TypeScript (RPG Platform UI)
│   ├── backend/      ← FastAPI + Supabase + Deep Agents
│   ├── shared/       ← JSON Schema contracts, D&D 5e seeds
│   └── infra/        ← Supabase, sdlc_obs
├── docs/
│   ├── product/      ← RPG Platform product specs
│   └── architecture/ ← This directory
├── .sdlc/
└── .cursor/
```

## RPG Platform — Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                   Browser — React SPA :5173                   │
│                   PT-BR · Supabase Auth client                │
└────────────────────────────┬─────────────────────────────────┘
                             │ JWT + REST /api/v1/*
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Backend :8000                      │
│  ┌────────────┐ ┌────────────┐ ┌──────────────────────────┐  │
│  │ Mesas      │ │ Documents  │ │ Sheet Import Deep Agent  │  │
│  │ Invites    │ │ Characters │ │ (deepagents + gpt-4.1-mini)│  │
│  └─────┬──────┘ └─────┬──────┘ └────────────┬─────────────┘  │
│        └──────────────┼─────────────────────┘                │
│                       ▼                                      │
│              Permission + contract validation                │
└────────────────────────────┬─────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Supabase Auth   │ │ PostgreSQL      │ │ Storage         │
│ Google OAuth    │ │ metadata + ACL  │ │ campaigns/      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

Full detail: [rpg-platform-overview.md](./rpg-platform-overview.md).

## App Boundaries Convention

- **frontend** — UI only; dynamic sheet forms from template schema
- **backend** — Business rules, JWT validation, Storage orchestration, agent jobs
- **shared** — JSON Schema contracts, seed templates
- **infra** — Supabase CLI config, SDLC observability

## Key Technology Decisions (RPG Platform)

| Area | Decision | ADR |
|------|----------|-----|
| Backend | FastAPI + Pydantic v2 | ADR-004 |
| Frontend | React + Vite + TypeScript | ADR-005 |
| Auth + DB | Supabase Auth + PostgreSQL | ADR-011 |
| Content | Supabase Storage (JSON + Markdown) | ADR-012 |
| Sheet import | LangChain Deep Agents | ADR-013 |
| Contracts | JSON Schema envelopes | ADR-014 |
| API | REST `/api/v1/`, OpenAPI | ADR-008, ADR-011 |

## Design Principles

1. **Mesa isolation** — Every query and Storage path scoped by `mesa_id`.
2. **Contracts first** — Storage JSON validated before persist.
3. **API-mediated Storage** — No direct client writes to `campaigns` bucket.
4. **Human-in-the-loop import** — Agent proposes; Master approves.
5. **SDLC-driven** — Plane cards before `app/` implementation.

## Related Documents

- [RPG Platform architecture](./rpg-platform-overview.md)
- [Architecture decisions](./decisions.md)
- [Product documentation](../product/README.md)
