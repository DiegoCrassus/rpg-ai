# Sheet Storage — Architecture Decision

> **Status:** Accepted (refinement, updated)  
> **Date:** 2026-06-11  
> **See also:** [storage-layout.md](./storage-layout.md)

## Questions

1. One database table per sheet type (D&D, Vampiro, custom)?  
2. Where do JSON payloads live — Postgres or Storage?

## Decisions

| Topic | Decision |
|-------|----------|
| Table per type | **No** — schema-driven templates, unlimited per Mesa |
| JSON location | **Supabase Storage** — `schema.json` + `data.json` per resource |
| DB role | Metadata + pointers only (`storage_path`, version, cached name) |
| D&D 5e | Platform **seed** copied into Mesa folder on create |

## Model

```
PostgreSQL                          Supabase Storage (campaigns bucket)
─────────────────                   ───────────────────────────────────
sheet_templates                     templates/{template_id}/schema.json
  id, mesa_id, name                 versions/v{n}.json
  storage_path, version

character_sheets                    characters/{sheet_id}/data.json
  id, mesa_id, template_id          meta.json
  owner_id, storage_path            media/portrait.webp
  character_name (cache)
```

Not one table per RPG system. Not JSONB blobs in Postgres for full sheet bodies.

## Why Storage for JSON sheets

| Benefit | Explanation |
|---------|-------------|
| Unified campaign repo | Sheets, lore, maps in one `{mesa_id}/` tree |
| Natural versioning | Copy `data.json` → `versions/v{n}.json` |
| Export | Zip one folder = full campaign backup |
| Size | Large repeaters / notes do not bloat DB |
| Master mental model | "Campaign folder" not "database rows" |

Postgres JSONB was considered; rejected for **content payloads** because campaign assets belong with files in one repository. Postgres keeps what SQL does best: relations and permissions.

## Dynamic templates

- Master creates template → API writes new `schema.json` under `templates/{id}/`.
- Master creates character → player fills `data.json` validated against schema.
- Completely different Mesas = completely different folders under `campaigns/`.

## Validation

See [json-contracts.md](./json-contracts.md) — envelope + JSON Schema on every write.  
Postgres [storage_files](./database-schema.md#table-storage_files-integrity-registry) records contract version and SHA-256.

## File fields in sheets

`image` / `file` types reference paths under the same sheet folder:

```json
{ "portrait": "characters/{sheet_id}/media/portrait.webp" }
```

## Rejected alternatives

| Option | Reason |
|--------|--------|
| Table per sheet type | No dynamic Master-created templates |
| JSONB only in Postgres | Splits campaign data away from files; harder export |
| Client writes Storage directly | Bypasses visibility rules |

## Seed

Repo file: `seeds/dnd5e/schema.json` (path TBD at implementation). Copied to Mesa on create.
