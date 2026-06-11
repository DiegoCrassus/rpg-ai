# Studio Foundation Inventory

This inventory is a derived, non-executable Studio document for `INVES-54`.
It maps current SDLC Studio Foundation source areas by path and concise summary
only. It does not copy authoritative rule bodies, command bodies, lifecycle
text, prompts, hooks, templates, or large source content.

## Boundary Statement

`studio/` is separate from `app/`. No `app/` work is included in this inventory,
and Studio Foundation does not add product UI, backend, frontend, database, API,
runtime, compiler, validator, command runner, scheduler, or AI composition
behavior.

`.sdlc/` and `.cursor/` are authoritative sources for SDLC process, workflow,
gates, commands, agents, skills, hooks, rules, templates, and automation.
`studio/` inventory, maps, schemas, and future views are derived,
non-executable documentation over those existing sources.

## Source Areas

### `studio/` - Derived Studio Documentation

- `studio/README.md` describes the Studio Foundation purpose, boundaries, and
  non-goals.
- `studio/foundation-inventory.md` is this derived inventory for the current
  foundation baseline.
- `studio/engine/schemas/` contains descriptive schemas for future Studio-readable
  documents and views.

### `studio/engine/schemas/` - Descriptive Studio Schemas

- `studio/engine/schemas/README.md` indexes the schema files and states their
  non-executable role.
- `studio/engine/schemas/graph.schema.yaml` describes a future non-executable graph of
  SDLC entities and relationships.
- `studio/engine/schemas/workflow.schema.yaml` describes workflow views assembled from
  existing source references.
- `studio/engine/schemas/registry-entity.schema.yaml` describes a referential registry
  entity that points to `.sdlc/` or `.cursor/` paths.
- `studio/engine/schemas/validation-result.schema.yaml` describes Studio-readable
  validation results such as path existence, YAML parse, scope, and policy
  checks.

### `.sdlc/registry/` - Referential Registry

`.sdlc/registry/` is referential, not authoritative. It indexes existing
authoritative artifacts by stable IDs, paths, short summaries, and lightweight
relationships.

- `.sdlc/registry/README.md` explains registry purpose and maintenance.
- `.sdlc/registry/index.yaml` lists registry files and non-goals.
- `.sdlc/registry/sdlc-artifacts.yaml` indexes current `.sdlc/` artifacts.
- `.sdlc/registry/cursor-artifacts.yaml` indexes current `.cursor/` artifacts.
- `.sdlc/registry/relationships.yaml` records lightweight relationships between
  registry entities.

### `.sdlc/` - Authoritative SDLC Sources

`.sdlc/` is authoritative for the repository's SDLC operating system and
machine-readable workflow data.

- `.sdlc/README.md` is the SDLC navigation index.
- `.sdlc/sdlc.yaml` is the machine-readable SDLC entry point.
- `.sdlc/process/master-workflow.md` and
  `.sdlc/process/change-lifecycle.md` are process authorities.
- `.sdlc/stages/`, `.sdlc/workflows/`, `.sdlc/gates/`,
  `.sdlc/gateways/`, `.sdlc/workboard/`, and `.sdlc/pipeline/` define
  workflow, stage, gate, workboard, and agent-pipeline data.
- `.sdlc/rules/`, `.sdlc/integrations/`, `.sdlc/templates/`,
  `.sdlc/scripts/`, `.sdlc/dsl/`, `.sdlc/doctor/`, and `.sdlc/memory/`
  provide governance indexes, integration metadata, references, automation,
  validation, and session handoff state.

### `.cursor/` - Authoritative Cursor Sources

`.cursor/` is authoritative for Cursor-specific agent configuration, rules,
commands, skills, and hooks used by this repository.

- `.cursor/README.md` is the Cursor configuration navigation index.
- `.cursor/agents/` defines specialized SDLC agent roles.
- `.cursor/skills/` defines procedural skills for SDLC activities.
- `.cursor/rules/` defines persistent agent rules.
- `.cursor/commands/` defines Cursor command instructions.
- `.cursor/hooks/` and `.cursor/hooks.json` define hook wiring and adapters.
- `.cursor/mcp.json.example` documents expected MCP configuration shape.

## Source-of-Truth Map

| Category | Paths | Role |
| --- | --- | --- |
| Authoritative SDLC artifacts | `.sdlc/`, `.sdlc/sdlc.yaml`, `.sdlc/process/`, `.sdlc/stages/`, `.sdlc/workflows/`, `.sdlc/gates/`, `.sdlc/gateways/`, `.sdlc/workboard/`, `.sdlc/pipeline/`, `.sdlc/scripts/`, `.sdlc/dsl/`, `.sdlc/doctor/` | Define process, lifecycle, gates, workflow data, validation, and automation behavior. |
| Authoritative Cursor artifacts | `.cursor/`, `.cursor/agents/`, `.cursor/skills/`, `.cursor/rules/`, `.cursor/commands/`, `.cursor/hooks/`, `.cursor/hooks.json` | Define Cursor agent roles, rules, skills, commands, and hook behavior. |
| Referential registry files | `.sdlc/registry/index.yaml`, `.sdlc/registry/sdlc-artifacts.yaml`, `.sdlc/registry/cursor-artifacts.yaml`, `.sdlc/registry/relationships.yaml` | Point to authoritative sources with stable IDs, concise summaries, and relationships. |
| Descriptive Studio schemas | `studio/engine/schemas/graph.schema.yaml`, `studio/engine/schemas/workflow.schema.yaml`, `studio/engine/schemas/registry-entity.schema.yaml`, `studio/engine/schemas/validation-result.schema.yaml` | Describe possible Studio-readable shapes without executing workflows or commands. |
| Derived future Studio views | `studio/`, future Studio maps, future Studio inventories, future Studio view documents | Present derived documentation or views over authoritative sources; no generated outputs are created by this card. |

Plane remains the source of truth for cards, state, and delivery evidence.
GitHub remains the source of truth for PR review and merge state.

## Baseline Terminology

- **Workflow:** A governed SDLC sequence or transition model described by
  authoritative `.sdlc/` process and workflow sources.
- **Stage:** A named lifecycle point for work, backed by `.sdlc/stages/` data
  and workflow transitions.
- **Gate:** A deterministic control that constrains allowed work, writable
  paths, or stage progress.
- **Agent:** A specialized Cursor role definition under `.cursor/agents/`.
- **Command:** A reusable Cursor or SDLC operation reference, such as a
  `.cursor/commands/` instruction or `.sdlc/` CLI entry point.
- **Handoff:** The current Markdown routing context in
  `.sdlc/memory/orchestrator-handoff.md`.
- **Registry entity:** A referential ID and path entry that points to an
  authoritative `.sdlc/` or `.cursor/` artifact.
- **Validation result:** A Studio-readable description of a check outcome, such
  as YAML parse, path existence, path scope, policy, lint, or doctor status.
- **Source reference:** A real repository path used to ground derived Studio
  documentation or views.
- **Derived view:** A non-executable Studio representation assembled from source
  references; it does not replace or run authoritative behavior.

## Future Plane-Card Candidates

The following gaps are candidates for future Plane cards only. They are not
local tickets, backlog items, specs, or evidence records.

- Define a stable naming convention for future derived Studio view files.
- Decide how future Studio maps should reference Plane and GitHub state without
  storing local delivery evidence.
- Add validation coverage for relationships between registry entities and source
  paths when a dedicated validation card is active.
