# MVP Scope

## Goal

Validate **organization + access control** for RPG campaigns. Prove that Mesa isolation and narrative permissions work before adding gameplay tooling.

## In scope

### Authentication and users

- [ ] Supabase Auth: email + password + OAuth (Google minimum)
- [ ] Local dev via Supabase CLI
- [ ] User profile (name, avatar URL)
- [ ] Password reset flow
- [ ] Account status: active / suspended

### Mesas

- [ ] Create Mesa (name, description, RPG system label) — starts in `importing` status
- [ ] **Sheet Import Agent** — upload PDF/PNG reference sheet → propose template + optional character data
- [ ] Master review UI — approve / reject / fallback to D&D 5e seed
- [ ] Mesa status: importing → active (after import approved)
- [ ] Creator is sole Master (one Master per Mesa)
- [ ] Max 2 Mesas as Master per user; unlimited Player memberships
- [ ] Mesa settings (sheet edit flags, etc.)

### Participants and invites

- [ ] Invite Player by email — single-use token, 7-day expiry
- [ ] Accept invite → join as Player
- [ ] Master can remove Player
- [ ] Role per Mesa: Master or Player

### Documents

- [ ] CRUD documents with type and tags
- [ ] Visibility: master_only, all_players, specific_players
- [ ] Master sees all; Player sees permitted only
- [ ] Basic list + text search

### Sheet templates and character sheets

- [ ] D&D 5e seed available as import fallback (not default path)
- [ ] Master creates custom sheet templates (`schema.json` in Storage)
- [ ] Campaign folder layout per [storage-layout.md](./storage-layout.md)
- [ ] Multiple templates per Mesa (PC, NPC, etc.)
- [ ] Player creates character from template
- [ ] Player edits own sheet; Master edits any
- [ ] Sheet visibility enforcement
- [ ] Version snapshots (sheets, templates, documents)
- [ ] File upload via Supabase Storage (avatars, attachments, sheet media)

### Character stories

- [ ] Player writes stories for own character
- [ ] Visibility: private, master, mesa
- [ ] Master reads all in Mesa

### Admin (minimal)

- [ ] List users and Mesas
- [ ] Suspend user account
- [ ] Admin bypass for support

## Out of scope (explicit)

| Feature | Phase |
|---------|-------|
| Dice rolling | Never MVP |
| Combat automation | Never MVP |
| Tactical maps | Never MVP |
| Real-time chat | v2+ |
| AI assistant | v3+ |
| Template marketplace | v3+ |
| Discord integration | v2+ |
| Self-hosted auth without Supabase | Out — Supabase Auth chosen |
| Entity relationship graph | v2 |
| Timeline | v2 |
| Layered secret revelations | v2 |
| Full version diff UI | v2 |

## User journey (MVP acceptance)

### Journey 1 — Master sets up campaign

1. Register and log in.
2. Create Mesa "Curse of Strahd" with system "D&D 5e".
3. Upload official D&D 2024 character sheet PDF (or filled PNG).
4. Review agent-proposed template; approve.
5. (Optional) Agent also extracts character from filled sheet.
4. Create documents: public session summary, secret NPC note (master_only).
5. Invite Player by email.
6. Create own NPC documents tagged `npc`.

### Journey 2 — Player joins

1. Receive invite email, register (or log in), accept invite.
2. See Mesa and public documents only.
3. Create character sheet from template.
4. Write character backstory (visible to Master).
5. Confirm secret NPC document is **not** visible.

### Journey 3 — Isolation

1. Same user is Master in Mesa A, Player in Mesa B.
2. Confirm Mesa A data invisible in Mesa B context.
3. Confirm roles enforced independently.

## Non-functional MVP targets

| Concern | Target |
|---------|--------|
| Auth | JWT or session cookies; HTTPS in production |
| API | REST `/api/v1/`; OpenAPI spec |
| DB | Relational; Mesa-scoped row isolation |
| UI | Responsive web; **PT-BR only** (Q-012) |
| Deploy | Single-region; local dev documented |

## Definition of Done (refinement → ready for architecture)

- [x] All items in `open-questions.md` resolved (2026-06-11)
- [x] Domain model reviewed and frozen for MVP entities
- [x] MVP journeys defined in this document
- [ ] Plane epic created with child cards (BACKEND, FRONTEND, INFRA)
