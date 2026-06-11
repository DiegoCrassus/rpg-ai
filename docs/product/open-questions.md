# Open Questions — Refinement Backlog

**Last updated:** 2026-06-11  
**Status:** **All resolved** — refinement gate closed.

---

## Product & branding

| ID | Decision | Date |
|----|----------|------|
| Q-001 | Product name: **RPG Platform** (working title). Repo `rpg-ai`; commercial/domain branding TBD pre-launch. | 2026-06-11 |

## Roles & access

| ID | Decision | Date |
|----|----------|------|
| Q-002 | **One Master per Mesa** — creator is sole Master; no co-Master in MVP. | 2026-06-11 |
| Q-003 | Subsumed by Q-002 — no Master transfer in MVP. | 2026-06-11 |
| Q-008 | **Players cannot create Mesa documents** in MVP. Only `character_story` (own character) and private notes. | 2026-06-11 |
| Q-011 | Any user may create a Mesa; **max 2 as Master**; unlimited Player memberships in others' Mesas. | 2026-06-11 |
| Q-015 | **Invite email must match** authenticated user's account email on accept. | 2026-06-11 |

## Invites

| ID | Decision | Date |
|----|----------|------|
| Q-004 | **Single-use token**; expires **7 days** after creation. | 2026-06-11 |

## Sheets & storage

| ID | Decision | Date |
|----|----------|------|
| Q-005 | **Computed sheet fields — post-MVP.** MVP field types are static only. | 2026-06-11 |
| Q-006 | Multiple templates per Mesa; JSON in **Supabase Storage**; D&D 5e seed as fallback. See [sheet-storage.md](./sheet-storage.md), [storage-layout.md](./storage-layout.md). | 2026-06-11 |
| Q-009 | **Version history in MVP** — Storage snapshots + `*_versions` tables. | 2026-06-11 |
| Q-013 | **File upload in MVP** via Supabase Storage. | 2026-06-11 |
| Q-018 | Import additional player sheets **post-MVP**; MVP = Mesa bootstrap import only. | 2026-06-11 |

## Auth & infra

| ID | Decision | Date |
|----|----------|------|
| Q-010 | **Supabase Auth** — email/password + OAuth. **Google required** in MVP; GitHub optional. Local dev: Supabase CLI. | 2026-06-11 |
| Q-019 | Authorization **API-only in MVP**; Supabase RLS on Storage as defense-in-depth in v1.1. | 2026-06-11 |
| Q-020 | Signed URL TTL for media downloads: **1 hour**. | 2026-06-11 |
| Q-021 | LangSmith tracing for import jobs: **optional**, off by default. | 2026-06-11 |

## UX & content

| ID | Decision | Date |
|----|----------|------|
| Q-012 | **PT-BR only** in MVP UI. i18n structure deferred to v1.1. | 2026-06-11 |
| Q-014 | Character stories and documents: **Markdown** (`content.md`). Structured JSON optional via `content_format: structured_json`. | 2026-06-11 |
| Q-016 | Document delete: **soft-delete** (`deleted_at`); hard purge by Admin only. | 2026-06-11 |

## AI / Sheet Import

| ID | Decision | Date |
|----|----------|------|
| Q-017 | **`openai:gpt-4.1-mini`** via `AGENT_MODEL` + **LangChain Deep Agents** (`deepagents`). | 2026-06-11 |

---

## Refinement gate

| Check | Status |
|-------|--------|
| All Q-items resolved | ✓ 2026-06-11 |
| Domain model frozen for MVP | ✓ |
| JSON contracts defined | ✓ |
| Database schema defined | ✓ |
| Mesa bootstrap (import agent) defined | ✓ |

**Next:** Plane epic + child cards (Planner). Architecture: [rpg-platform-overview.md](../architecture/rpg-platform-overview.md).
