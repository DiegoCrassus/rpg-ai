# Product Modules

Logical modules for MVP and their boundaries. Each maps to future backend routers and frontend areas.

## Module map

```
┌─────────────────────────────────────────────────────────┐
│                    RPG Platform                          │
├─────────────┬─────────────┬──────────────┬──────────────┤
│   Users     │   Mesas     │ Permissions  │    Admin     │
├─────────────┴──────┬──────┴──────────────┴──────────────┤
│     Sheet Import Agent │ Documents │ Fichas (Sheets)    │
├──────────────────────┴─────────────────────────────────┤
│         História/Lore (via Documents + Stories)          │
└─────────────────────────────────────────────────────────┘
```

## Users

**Responsibility:** Authentication, profile, account lifecycle.

| Feature | MVP |
|---------|-----|
| Supabase Auth (email + OAuth) | ✓ |
| Profile (name, avatar via Storage) | ✓ |
| Password recovery | ✓ (Supabase) |
| Admin user management | ✓ (basic) |

**API prefix proposal:** `/api/v1/auth`, `/api/v1/users`

## Sheet Import Agent

**Responsibility:** Mesa bootstrap — PDF/PNG → `rpg.sheet-template` + optional `rpg.character-sheet`.

| Feature | MVP |
|---------|-----|
| Upload PDF/PNG on Mesa create | ✓ |
| Vision LLM layout + value extraction | ✓ |
| D&D 5e 2024 / 2014 classification | ✓ |
| Master review + approve before persist | ✓ |
| D&D 5e platform seed fallback | ✓ |
| Import additional sheets post-create | Post-MVP |

**API prefix:** `/api/v1/mesas/{id}/import`  
**Doc:** [sheet-import-agent.md](./sheet-import-agent.md)

## Mesas

**Responsibility:** Campaign lifecycle, participants, invites.

| Feature | MVP |
|---------|-----|
| Create Mesa → import flow → active | ✓ |
| Create / edit / archive Mesa | ✓ |
| Participant list and roles | ✓ |
| Invite by email + link | ✓ |
| Mesa settings JSON | ✓ |
| Transfer primary Master | Post-MVP |

**API prefix:** `/api/v1/mesas`

## Permissions

**Responsibility:** Authorization middleware — not a user-facing module.

| Concern | MVP |
|---------|-----|
| Mesa membership guard | ✓ |
| Role check (Master/Player) | ✓ |
| Document visibility resolver | ✓ |
| Sheet visibility resolver | ✓ |
| Admin global bypass | ✓ |

Implemented as backend policy layer + shared permission helpers, not a separate UI.

## Fichas (Sheets)

**Responsibility:** Template designer + character sheet CRUD.

| Feature | MVP |
|---------|-----|
| D&D 5e seed template | ✓ |
| Custom template CRUD (`schema.json` in Storage) | ✓ |
| Multiple templates per Mesa | ✓ |
| Character sheet CRUD (`data.json` in Storage) | ✓ |
| Version snapshots | ✓ |
| Sheet file/image fields (Storage) | ✓ |
| Template library / reuse | Post-MVP |

**API prefix:** `/api/v1/mesas/{id}/sheet-templates`, `/api/v1/mesas/{id}/characters`

## Documents

**Responsibility:** Campaign wiki — lore, NPCs, rules, session notes.

| Feature | MVP |
|---------|-----|
| Document CRUD | ✓ |
| Type taxonomy + tags | ✓ |
| Visibility controls | ✓ |
| Search / filter | ✓ (basic text) |
| File/image upload (Supabase Storage) | ✓ |
| Full-text advanced search | Post-MVP |
| Entity relationships (graph) | Post-MVP |

**API prefix:** `/api/v1/mesas/{id}/documents`

## História e Lore

**Responsibility:** Narrative organization.

| MVP approach | Notes |
|--------------|-------|
| Documents typed as `lore`, `npc`, `location`, etc. | Wiki-like browsing |
| CharacterStory entity | Player diaries separate from Mesa docs |
| Timeline module | Post-MVP |
| Layered secrets / revelations | Post-MVP |

No separate backend module in MVP — composition of Documents + CharacterStory.

## Sessões (Sessions)

**Responsibility:** Session logging, summaries, links to entities.

| MVP | Post-MVP |
|-----|----------|
| Document type `session` | Dedicated session entity |
| Manual summary text | Structured session with linked NPCs, locations, rewards |

## Admin

**Responsibility:** Platform operator panel.

| Feature | MVP |
|---------|-----|
| User list + suspend | ✓ |
| Mesa list (read-only overview) | ✓ |
| Audit log viewer | Basic |
| Global settings | Minimal |

**API prefix:** `/api/v1/admin`

## Module dependency order (implementation)

1. Users (auth)
2. Mesas + Sheet Import Agent
3. Participants + Invites
4. Permissions layer
5. Documents
6. Sheet templates + Character sheets
7. Character stories
8. Admin panel
