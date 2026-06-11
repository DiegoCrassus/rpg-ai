# Campaign Repository Layout — Supabase Storage

> **Status:** Accepted (refinement)  
> **Date:** 2026-06-11  
> **Related:** [sheet-storage.md](./sheet-storage.md), [infrastructure.md](./infrastructure.md)

## Principle

Each **Mesa** is a self-contained campaign repository. All **content payloads** (JSON sheets, documents, media) live in **Supabase Storage**. **PostgreSQL** holds metadata, permissions, indexes, and pointers to storage paths.

```
PostgreSQL  →  who, what, where, visibility, version number
Storage     →  actual JSON / markdown / binary files
```

## Buckets

| Bucket | Scope | Contents |
|--------|-------|----------|
| `profiles` | Global | User avatars |
| `campaigns` | Per Mesa | All campaign content (JSON, text, media) |

Single `campaigns` bucket keeps one Mesa = one folder tree. Easier backup, export, and mental model.

## Campaign folder tree

```
campaigns/
└── {mesa_id}/
    ├── import/
    │   └── source.{pdf|png}          # Mesa bootstrap upload (Sheet Import Agent)
    ├── manifest.json                 # optional index (types, counts, updated_at)
    │
    ├── templates/
    │   └── {template_id}/
    │       ├── schema.json           # field definitions (current)
    │       └── versions/
    │           └── v{version}.json
    │
    ├── characters/
    │   └── {sheet_id}/
    │       ├── data.json             # sheet values (current)
    │       ├── meta.json             # character_name, template_id, owner_id mirror
    │       ├── versions/
    │       │   └── v{version}.json
    │       └── media/                # portrait, item images
    │           └── {field_key}.{ext}
    │
    ├── documents/
    │   └── {document_id}/
    │       ├── content.md            # or content.json for structured docs
    │       ├── meta.json             # title, type, tags, visibility mirror
    │       ├── versions/
    │       │   └── v{version}.md
    │       └── attachments/
    │           └── {filename}
    │
    └── assets/                       # loose uploads (maps, handouts)
        └── {asset_id}.{ext}
```

## File formats

| Resource | Primary file | Format |
|----------|--------------|--------|
| Sheet template | `schema.json` | JSON — field schema |
| Character sheet | `data.json` | JSON — values keyed by schema |
| Document (lore, NPC) | `content.md` | Markdown (default) or `content.json` |
| Character story | `documents/{id}/content.md` | Same as documents |
| Binary | `attachments/`, `media/`, `assets/` | png, webp, pdf, etc. |

All JSON files use the **envelope** from [json-contracts.md](./json-contracts.md). Examples below show `payload` only.

### Example `schema.json` payload (D&D 5e seed)

```json
{
  "name": "D&D 5e Character",
  "slug": "dnd5e-character",
  "is_seed": true,
  "fields": [
    { "key": "character_name", "type": "text", "label": "Name", "required": true },
    { "key": "str", "type": "number", "label": "Strength", "constraints": { "min": 1, "max": 30 } }
  ]
}
```

### Example `data.json` payload

```json
{
  "template_id": "uuid",
  "template_entity_version": 1,
  "values": {
    "character_name": "Aragorn",
    "str": 18,
    "portrait": "characters/{sheet_id}/media/portrait.webp"
  }
}
```

Media paths inside JSON are **relative to the Mesa folder** in `campaigns`.

## PostgreSQL mirror (metadata)

DB rows point to storage; they do not duplicate full JSON in MVP.

| Table | Storage pointer | Cached fields (for list/search) |
|-------|-----------------|----------------------------------|
| `sheet_templates` | `storage_path` → `templates/{id}/schema.json` | name, version, status |
| `character_sheets` | `storage_path` → `characters/{id}/data.json` | character_name, owner_id, template_id |
| `documents` | `storage_path` → `documents/{id}/content.md` | title, type, tags |
| `*_versions` | `storage_path` → `…/versions/v{n}.*` | version, created_at, created_by |

**Optional:** small JSONB cache on `character_sheets` for indexed fields (e.g. `character_name`) — add only if search requires it.

## Read / write flow

### Save character sheet

1. API validates JWT + Mesa permission.
2. Load `templates/{template_id}/schema.json` from Storage.
3. Validate payload against schema.
4. Write `characters/{sheet_id}/data.json` to Storage.
5. Copy previous file to `versions/v{n}.json` if version bump.
6. Update Postgres row (version, `updated_at`, cached `character_name`).

### Load document (with visibility)

1. API checks visibility in Postgres.
2. If allowed, fetch `documents/{id}/content.md` via signed URL or service role.
3. Return content + metadata.

All Storage access goes through **FastAPI** in MVP — no direct client write to `campaigns` bucket (prevents permission bypass).

## Versioning

| Trigger | Storage action |
|---------|----------------|
| Sheet save | Copy `data.json` → `versions/v{n}.json` before overwrite |
| Template edit | Copy `schema.json` → `versions/v{n}.json` |
| Document edit | Copy `content.*` → `versions/v{n}.*` |

Postgres `*_versions` table records `version`, `storage_path`, `created_by`, `created_at`.

## Access control

| Layer | Responsibility |
|-------|----------------|
| Postgres | Membership, role, document visibility, sheet ownership |
| FastAPI | Authorize before any Storage read/write |
| Storage RLS | Optional defense-in-depth; service role for API writes |

Players never receive Storage credentials for paths they cannot access via API.

## D&D 5e seed

On Mesa create (optional):

1. Copy repo seed `seeds/dnd5e/schema.json` → `campaigns/{mesa_id}/templates/{new_id}/schema.json`
2. Insert `sheet_templates` row with `is_seed: true`

## Export / backup (future)

Entire Mesa = zip of `campaigns/{mesa_id}/` folder. Postgres metadata exported separately or embedded in `manifest.json`.

## What stays out of Storage

| Data | Where |
|------|-------|
| Users, auth | Supabase Auth + `users` table |
| Invites, tokens | Postgres only (security) |
| Permissions | Postgres only |
| Audit log | Postgres |

## Consequences

- Campaign feels like a **folder of files** — aligns with RPG table mental model.
- JSON sheets sit beside lore markdown and map PNGs in one tree.
- Postgres stays lean; no large JSONB blobs in DB.
- Every read/write = Storage API call — acceptable for MVP scale; add CDN/cache later.
