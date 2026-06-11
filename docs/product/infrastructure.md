# Infrastructure — MVP

> **Status:** Accepted (refinement)  
> **Date:** 2026-06-11  
> **Related:** [storage-layout.md](./storage-layout.md)

## Stack

| Layer | Choice |
|-------|--------|
| Auth | Supabase Auth (email + OAuth) |
| Database | Supabase PostgreSQL — metadata, permissions, indexes |
| Content store | Supabase Storage — JSON sheets, documents, media |
| API | FastAPI — JWT validation, authorization, Storage orchestration |
| Sheet Import Agent | LangChain **Deep Agents** (`deepagents`) + `AGENT_MODEL` |
| Frontend | React + Vite |
| Local dev | `supabase start` (Docker) |

## Data split

```
┌─────────────────────────────────────────────────────────┐
│                    Supabase                              │
├──────────────────────┬──────────────────────────────────┤
│ PostgreSQL           │ Storage                           │
│ · users (mirror)     │ · profiles/{user_id}/avatar.*    │
│ · mesas              │ · campaigns/{mesa_id}/           │
│ · participants       │     templates/…/schema.json      │
│ · invites            │     characters/…/data.json       │
│ · sheet_templates *  │     documents/…/content.md       │
│ · character_sheets * │     assets/, attachments/, media/ │
│ · documents *        │                                   │
│ · versions *         │                                   │
│ · permissions        │                                   │
└──────────────────────┴──────────────────────────────────┘
         * rows hold storage_path + cache fields only
```

## Storage buckets

| Bucket | Path pattern | Access |
|--------|--------------|--------|
| `profiles` | `{user_id}/avatar.{ext}` | API-mediated |
| `campaigns` | `{mesa_id}/…` | API-mediated; see [storage-layout.md](./storage-layout.md) |

No separate `sheet-media` or `mesa-assets` buckets — all under `campaigns/{mesa_id}/`.

## Auth flow

```
Browser → Supabase Auth
        → JWT
        → FastAPI (validate JWKS, load user)
        → Permission check (Postgres)
        → Read/write Storage via service role
```

Clients do **not** write to `campaigns` bucket directly in MVP.

## Local development

```bash
supabase start
# Postgres + Auth + Storage + Studio (localhost)
```

Env vars: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `DATABASE_URL`, `SUPABASE_JWT_SECRET`.

## Application-only logic (not Supabase built-ins)

- Invite tokens (7-day, single-use)
- Document / sheet visibility
- 2-Mesa Master cap
- Version copy orchestration in Storage

## Agent configuration

| Variable | Purpose |
|----------|---------|
| `AGENT_MODEL` | `openai:gpt-4.1-mini` — Sheet Import Agent + SDLC agents |
| `OPENAI_API_KEY` | OpenAI API access |

See [sheet-import-agent.md](./sheet-import-agent.md).

## Resolved defaults (Q-019–Q-021)

| Topic | MVP decision |
|-------|----------------|
| OAuth providers | **Google** required; GitHub optional (Q-010) |
| Authorization | **FastAPI only**; Supabase RLS deferred to v1.1 (Q-019) |
| Signed URL TTL | **1 hour** for media/attachments (Q-020) |
| LangSmith | Optional; **off** by default (Q-021) |
