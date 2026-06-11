# JSON Contracts — Storage Payloads

> **Status:** Accepted (refinement)  
> **Date:** 2026-06-11  
> **Related:** [database-schema.md](./database-schema.md), [storage-layout.md](./storage-layout.md)

## Principles

1. **Every Storage JSON file** uses a versioned **envelope** — no raw unwrapped payloads.
2. **Contract ID + version** are explicit (`contract`, `contract_version`) — independent of entity `version`.
3. **Validation is mandatory** on write; invalid files are rejected (HTTP 422), never persisted.
4. **JSON Schema** is the source of truth — implementation copies to `app/shared/contracts/` (future).
5. **Postgres `storage_files`** row must match envelope metadata after every successful write.

## Envelope (all JSON contracts)

```json
{
  "contract": "<contract-id>",
  "contract_version": "1.0.0",
  "meta": {
    "mesa_id": "uuid",
    "resource_id": "uuid",
    "entity_version": 1,
    "created_at": "2026-06-11T12:00:00Z",
    "updated_at": "2026-06-11T12:00:00Z"
  },
  "payload": { }
}
```

| Field | Required | Rules |
|-------|----------|-------|
| `contract` | yes | Stable string ID (see registry below) |
| `contract_version` | yes | Semver `MAJOR.MINOR.PATCH` |
| `meta.mesa_id` | yes | Must match DB `mesas.id` and path prefix |
| `meta.resource_id` | yes | Must match owning entity PK |
| `meta.entity_version` | yes | Integer ≥ 1; sync with Postgres `version` |
| `meta.created_at` | yes | ISO 8601 UTC |
| `meta.updated_at` | yes | ISO 8601 UTC, ≥ `created_at` |
| `payload` | yes | Contract-specific body |

**Reject if:** unknown `contract`, unsupported `contract_version` (major mismatch), `meta` inconsistent with DB row, schema validation fails.

## Contract registry

| Contract ID | File(s) | Schema file (impl) |
|-------------|---------|-------------------|
| `rpg.sheet-template` | `templates/{id}/schema.json` | `sheet-template.v1.schema.json` |
| `rpg.character-sheet` | `characters/{id}/data.json` | `character-sheet.v1.schema.json` |
| `rpg.document-meta` | `documents/{id}/meta.json` | `document-meta.v1.schema.json` |
| `rpg.character-meta` | `characters/{id}/meta.json` | `character-meta.v1.schema.json` |
| `rpg.campaign-manifest` | `manifest.json` | `campaign-manifest.v1.schema.json` |
| `rpg.sheet-import-proposal` | internal (API only) | `sheet-import-proposal.v1.schema.json` |
| `rpg.structured-document` | `documents/{id}/content.json` | `structured-document.v1.schema.json` |

Markdown documents (`content.md`) are **not** JSON — validated by max size + optional frontmatter parser; metadata contract is `rpg.document-meta`.

## `rpg.sheet-template` v1.0.0

**Path:** `campaigns/{mesa_id}/templates/{template_id}/schema.json`

### Payload schema

```json
{
  "name": "D&D 5e Character",
  "description": "Standard player character sheet",
  "slug": "dnd5e-character",
  "is_seed": true,
  "seed_key": "dnd5e",
  "fields": [
    {
      "key": "character_name",
      "type": "text",
      "label": "Character Name",
      "required": true,
      "order": 0,
      "constraints": { "max_length": 120 }
    },
    {
      "key": "attributes",
      "type": "group",
      "label": "Attributes",
      "order": 1,
      "children": [
        {
          "key": "str",
          "type": "number",
          "label": "Strength",
          "constraints": { "min": 1, "max": 30, "integer": true }
        }
      ]
    },
    {
      "key": "skills",
      "type": "repeater",
      "label": "Skills",
      "item_label": "Skill",
      "constraints": { "max_items": 50 },
      "children": [
        { "key": "name", "type": "text", "required": true },
        { "key": "bonus", "type": "number" }
      ]
    },
    {
      "key": "portrait",
      "type": "image",
      "label": "Portrait",
      "constraints": { "allowed_extensions": ["webp", "png", "jpg"] }
    }
  ]
}
```

### Field `type` enum (closed)

`text` | `textarea` | `number` | `checkbox` | `select` | `multiselect` | `group` | `repeater` | `image` | `file`

### Field rules

| Rule | Description |
|------|-------------|
| `key` | Unique within template; `^[a-z][a-z0-9_]{0,63}$` |
| `key` | Required on all field nodes |
| `children` | Required for `group` and `repeater`; forbidden on other types |
| `constraints.options` | Required for `select` / `multiselect` |
| Nesting | `group`/`repeater` max depth **4** |
| Total fields | Max **200** per template |

### Versioning

- Template schema change → increment `entity_version` + copy file to `versions/v{n}.json`.
- Existing sheets validated against **template version they were created with** until Master migrates (flag `schema_outdated` on `character_sheets`).

---

## `rpg.character-sheet` v1.0.0

**Path:** `campaigns/{mesa_id}/characters/{sheet_id}/data.json`

### Payload schema

```json
{
  "template_id": "uuid",
  "template_entity_version": 2,
  "values": {
    "character_name": "Aragorn",
    "attributes": { "str": 18, "dex": 14 },
    "skills": [{ "name": "Athletics", "bonus": 5 }],
    "portrait": "characters/{sheet_id}/media/portrait.webp"
  }
}
```

### Rules

| Rule | Description |
|------|-------------|
| `template_id` | Must match DB `character_sheets.template_id` |
| `template_entity_version` | Template version used for validation |
| `values` | Keys must exist in template; unknown keys **rejected** |
| Required fields | Every field marked `required: true` in template must be present |
| Types | Validated per template field `type` |
| `image` / `file` | String path; must start with `characters/{sheet_id}/media/` or `assets/` |
| Max payload size | **512 KB** JSON serialized |

### `character-meta.json` (`rpg.character-meta` v1.0.0)

Mirror for Storage-only reads and export:

```json
{
  "payload": {
    "character_name": "Aragorn",
    "owner_id": "uuid",
    "template_id": "uuid",
    "status": "active",
    "visibility": "owner_only"
  }
}
```

Must stay in sync with Postgres `character_sheets` on every write.

---

## `rpg.document-meta` v1.0.0

**Path:** `campaigns/{mesa_id}/documents/{document_id}/meta.json`

```json
{
  "payload": {
    "title": "Barovia — Village of Barovia",
    "type": "location",
    "tags": ["barovia", "village"],
    "visibility": "all_players",
    "visibility_targets": [],
    "character_sheet_id": null,
    "content_format": "markdown",
    "created_by": "uuid"
  }
}
```

### `type` enum (closed)

`rule` | `campaign_story` | `lore` | `npc` | `location` | `item` | `monster` | `organization` | `session` | `summary` | `freeform` | `character_story` | `attachment` | `external_link`

### `visibility` enum (closed)

`master_only` | `all_players` | `specific_players` | `specific_character` | `owner_private`

| `visibility` | `visibility_targets` |
|--------------|----------------------|
| `specific_players` | Non-empty array of `user_id` |
| `specific_character` | Exactly one `character_sheet_id` |
| Others | Must be `[]` |

Character stories: `type: "character_story"`, `character_sheet_id` required.

### `content_format` enum

`markdown` | `structured_json`

- `markdown` → body in `content.md`
- `structured_json` → body in `content.json` using `rpg.structured-document`

---

## `rpg.structured-document` v1.0.0

For NPCs/items with fixed internal shape (optional alternative to Markdown):

```json
{
  "payload": {
    "title": "Strahd von Zarovich",
    "sections": [
      { "key": "description", "content": "..." },
      { "key": "motivation", "content": "..." },
      { "key": "stats_ref", "character_sheet_id": "uuid-or-null" }
    ]
  }
}
```

---

## `rpg.campaign-manifest` v1.0.0

**Path:** `campaigns/{mesa_id}/manifest.json`  
Regenerated by API after structural changes (not hand-edited).

```json
{
  "payload": {
    "mesa_id": "uuid",
    "mesa_name": "Curse of Strahd",
    "rpg_system": "D&D 5e",
    "entity_version": 5,
    "counts": {
      "templates": 2,
      "characters": 5,
      "documents": 42,
      "assets": 3
    },
    "updated_at": "2026-06-11T12:00:00Z"
  }
}
```

---

## Validation pipeline (write)

```
1. Authenticate JWT
2. Authorize Mesa + resource action (Postgres)
3. Load contract JSON Schema by (contract, contract_version)
4. Parse envelope — reject if wrapper invalid
5. Cross-check meta.mesa_id, meta.resource_id vs DB
6. Validate payload against schema
7. For character-sheet: load template schema; validate values (step 6b)
8. Write Storage file
9. Upsert storage_files row (checksum, contract, version)
10. Update entity table + version table in single transaction
11. Regenerate manifest.json (async or same request)
```

## Contract evolution

| Change | Action |
|--------|--------|
| PATCH (optional fields, looser constraints) | Bump `contract_version` minor |
| Breaking payload shape | Bump `contract_version` major; support N and N-1 major in API during migration window |
| New field type | Minor bump + update enum in schema |

API rejects writes with deprecated major version after sunset date (documented per contract).

## Implementation artifacts (future)

```
app/shared/contracts/
├── sheet-template.v1.schema.json
├── character-sheet.v1.schema.json
├── document-meta.v1.schema.json
├── character-meta.v1.schema.json
├── campaign-manifest.v1.schema.json
├── structured-document.v1.schema.json
└── README.md
```

CI: validate seed files (`seeds/dnd5e/schema.json`) against schemas on every PR.

## Sheet Import Agent output

The Deep Agent produces `rpg.sheet-import-proposal` (internal). After Master approval, the API converts to `rpg.sheet-template` and optional `rpg.character-sheet` envelopes. See [sheet-import-agent.md](./sheet-import-agent.md).
