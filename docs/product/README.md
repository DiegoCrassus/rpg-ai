# RPG Platform — Product Documentation

> **Phase:** Architecture complete — ready for Plane epic  
> **Status:** Refinement closed · Architecture in `docs/architecture/`  
> **Last updated:** 2026-06-11

## Purpose

Product definition for the **RPG Campaign Management Platform**. Each file refines the brief into decision-ready specifications.

## Document map

| # | Document | Contents |
|---|----------|----------|
| 1 | [product-vision.md](./product-vision.md) | Vision, differentiation, non-goals |
| 2 | [user-roles-and-permissions.md](./user-roles-and-permissions.md) | Admin, Master, Player |
| 3 | [domain-model.md](./domain-model.md) | Entities, states, relationships |
| 4 | [business-rules.md](./business-rules.md) | Numbered business rules |
| 5 | [modules.md](./modules.md) | Product modules |
| 6 | [mvp-scope.md](./mvp-scope.md) | MVP scope and journeys |
| 7 | [future-evolution.md](./future-evolution.md) | Post-MVP roadmap |
| 8 | [open-questions.md](./open-questions.md) | Remaining decisions |
| 9 | [sheet-storage.md](./sheet-storage.md) | Dynamic sheets — schema model |
| 10 | [storage-layout.md](./storage-layout.md) | Supabase Storage campaign tree |
| 11 | [infrastructure.md](./infrastructure.md) | Supabase stack, data split |
| 12 | [json-contracts.md](./json-contracts.md) | Versioned JSON envelopes + schemas |
| 13 | [database-schema.md](./database-schema.md) | PostgreSQL tables, indexes, constraints |
| 14 | [sheet-import-agent.md](./sheet-import-agent.md) | AI import PDF/PNG → sheet contract (Mesa bootstrap) |
| 15 | [dnd5e-sheet-reference.md](./dnd5e-sheet-reference.md) | D&D 5e 2024 field glossary for agent |

## Glossary

| PT | EN |
|----|-----|
| Mesa | Campaign sandbox |
| Master | Game Master (one per Mesa) |
| Player | Invited participant |
| Ficha | Character sheet (`data.json` in Storage) |
| Modelo de ficha | Sheet template (`schema.json` in Storage) |
| Documento | Campaign document (`content.md` in Storage) |

## Next

Plane epic (BACKEND · FRONTEND · INFRA) → `workflow start` per child card.

Architecture: [rpg-platform-overview.md](../architecture/rpg-platform-overview.md) · ADRs 011–015.
