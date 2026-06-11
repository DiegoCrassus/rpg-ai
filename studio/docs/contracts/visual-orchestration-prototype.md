# Visual Orchestration Prototype

This document defines the SDLC Studio visual orchestration prototype as a
derived, non-authoritative architecture view. It describes how a future visual
surface may present Studio compiler and validator outputs without implementing a
runtime UI, changing source artifacts, storing generated outputs, or becoming a
source of workflow truth.

The prototype belongs to `studio/`. Studio is unrelated to product runtime code
and this card does not introduce implementation targets under `app/`.

## Purpose

The visual orchestration prototype helps humans understand SDLC workflows,
artifact relationships, validation findings, and handoff paths through a derived
graph view. It is a planning and architecture boundary for future build work,
not a product UI build.

The prototype may explain:

- How workflow, graph, registry, report, and validation concepts could appear in
  a future canvas or visual inspector.
- How visual records trace back to existing source references.
- How validation status may be shown without becoming local evidence.
- How future implementation work can preserve Studio source-of-truth boundaries.

The prototype must not define executable behavior. It does not run commands,
call agents, update cards, update pull requests, enforce gates, persist graph
artifacts, or mutate source files.

## Inputs

The visual prototype is derived from existing Studio contracts and future
compiler or validator outputs. Expected inputs are references to:

- Graph IR governed by `studio/docs/contracts/graph-ir-contract.md`.
- Workflow IR shaped by `studio/engine/schemas/workflow.schema.yaml`.
- Validation Result IR governed by `studio/docs/contracts/validation-result-ir-contract.md`.
- Compiler and validator report envelopes described by
  `studio/compiler-validator-boundaries.md`.
- Source boundary terminology from `studio/source-boundaries.md`.
- Descriptive schema documents under `studio/engine/schemas/`.
- Roadmap guidance from `docs/roadmap/sdlc-studio-mvp-roadmap.md`.
- Source references to `.sdlc/`, `.cursor/`, `.sdlc/registry/`, Plane, and
  GitHub as authorities in their existing domains.

Inputs are read by reference. The visual prototype must not copy authoritative
rule bodies, lifecycle bodies, command bodies, prompts, hook logic, templates,
generated output bodies, CI logs, local evidence records, or durable work state.

## Source-Of-Truth Boundaries

The visual prototype is never authoritative for workflow state, card state, PR
state, CI state, merge state, validation evidence, or source artifact behavior.

Authoritative sources remain:

- `.sdlc/` for SDLC process, lifecycle, workflows, gates, stages, scripts,
  templates, doctor checks, and handoff state.
- `.cursor/` for Cursor agents, skills, rules, commands, hooks, MCP
  configuration shape, and Cursor-local behavior.
- Plane for card scope, work item state, comments, planning, and durable
  delivery evidence.
- GitHub for pull requests, reviews, checks, CI state, merge state, branch
  history, and repository history.
- `.sdlc/registry/` as a referential index over `.sdlc/` and `.cursor/`
  artifacts, not as the behavioral authority for referenced artifacts.

`studio/` documents and `studio/engine/schemas/` remain descriptive and
non-executable. A visual graph may point to authority, but it cannot replace or
override authority.

## Derived Graph Source

The visual graph source is an in-memory view assembled from compiler, validator,
and report envelopes. The envelope authority label is
`derived_non_authoritative`.

The derived source may combine:

- Graph metadata, nodes, edges, annotations, source references, and validation
  attachments from Graph IR.
- Workflow stage, gate, transition, agent, and handoff records from Workflow IR.
- Validation Result IR records for path scope, schema, relationship, policy,
  lint, doctor, or custom findings.
- Compile report sections for coverage, unresolved references, skipped source
  areas, non-goals, and suggested next actions.
- Validate report sections for findings, severity, target references, source
  references, and status summaries.

For this card, generated graph artifacts and report outputs are non-persisted.
They may be discussed as stdout, transient memory, or future preview inputs, but
no generated artifacts are committed or treated as delivery evidence.

## View Model Responsibilities

A future view model may translate derived Studio records into display records
that are convenient for a renderer while preserving the IR contracts.

Allowed responsibilities include:

- Map Graph IR nodes and edges into display records with stable IDs, labels,
  categories, source references, annotations, and validation attachments.
- Group workflow records by stage, gate, transition, handoff path, agent role,
  source area, or validation status.
- Expose source links back to repository paths, Plane IDs, or GitHub references
  without copying source bodies or evidence bodies.
- Surface validation overlays such as pass, warn, fail, and not_run states from
  Validation Result IR.
- Support inspection, filtering, search, and handoff-path reading over derived
  records.
- Carry non-goal reminders so the visual surface clearly communicates that it is
  derived and non-authoritative.
- Preserve enough source reference context for future QA and reviewers to verify
  that displayed records trace back to real authorities.

The view model must not:

- Mutate `.sdlc/`, `.cursor/`, `.sdlc/registry/`, Plane, GitHub, Studio
  contracts, schemas, or product source files.
- Store local tickets, backlog, durable evidence, generated graph outputs,
  validation evidence, PR state, CI state, merge state, or workboard state.
- Run shell commands, doctor, lint, CI, validators, compilers, workflow gates, or
  command runners.
- Call agents, Plane, GitHub, external APIs, backend APIs, frontend APIs, or
  persistence layers.
- Become workflow state, card state, PR state, CI state, merge state, validation
  evidence, or source artifact behavior.

## Rendering Boundaries

The renderer is a future consumer of the view model. This document does not
choose or implement a rendering runtime.

React Flow is only a future candidate named by
`docs/roadmap/sdlc-studio-mvp-roadmap.md`. TLDraw concepts may inform future
whiteboard-style annotation research. This card does not add a React Flow
dependency, TLDraw implementation, npm package, component model, canvas
coordinates, React props, UI runtime, backend or frontend API, database,
persistence, external API, or product runtime code.

Renderer boundaries:

- Renderers consume derived display records and source links.
- Renderers do not define Graph IR, Workflow IR, Validation Result IR, compiler
  behavior, validator behavior, gate behavior, or source artifact behavior.
- Renderer interactions such as selection, filtering, expansion, highlighting,
  and inspection are presentation concerns only.
- Any future edit affordance must be explicitly scoped by a later Plane card and
  must preserve the rule that source changes flow through the SDLC process,
  Plane, GitHub, QA, review, and DevOps gates.

## Validation Display Expectations

Validation display is descriptive. It helps people see the status of derived
records, but it is not a validator and it is not durable delivery evidence.

Expected display behavior:

- Show validation status using Validation Result IR status labels: pass, warn,
  fail, and not_run.
- Link each validation item to its target reference and source references.
- Distinguish compiler coverage gaps, validator findings, skipped checks,
  warnings, and blocking failures.
- Preserve message levels such as info, warn, and error without copying command
  output bodies, CI logs, or evidence bodies.
- Make freshness and authority clear when a displayed result comes from a
  derived report rather than a live source authority.
- Explain that Plane remains the durable evidence authority and GitHub remains
  the PR, review, checks, CI, and merge authority.

Validation display must not imply that a visual status has enforced a gate,
approved a workflow transition, passed CI, merged a branch, completed QA,
updated Plane, or changed GitHub.

## Non-Goals

This card does not:

- Build a runtime UI, product UI, backend, frontend, API, service, database,
  scheduler, persistence layer, command runner, workflow runner, validator,
  compiler, AI composition system, or external integration.
- Add React Flow, TLDraw, npm packages, runtime dependencies, component models,
  canvas coordinates, React props, generated artifacts, or persisted reports.
- Define Plane or GitHub replacement behavior.
- Store local tickets, backlog, specs, delivery evidence, validation evidence,
  generated graph outputs, PR state, CI state, merge state, or workboard state.
- Change `.sdlc/`, `.cursor/`, `.sdlc/registry/`, `studio/engine/schemas/`,
  `docs/roadmap/`, or any product runtime source.
- Treat Studio as related to `app/` or add `app/` implementation targets.

## Handoff To Future Build Work

Future build work may implement a derived visual canvas only after a separate
Plane card opens the appropriate workflow gate. That future card should consume
this architecture alongside `studio/docs/contracts/graph-ir-contract.md`,
`studio/compiler-validator-boundaries.md`, `studio/source-boundaries.md`,
`studio/docs/contracts/validation-result-ir-contract.md`, `studio/engine/schemas/`, and
`docs/roadmap/sdlc-studio-mvp-roadmap.md`.

Future implementation scope should define:

- The exact source of compiled Graph IR, Workflow IR, Validation Result IR, and
  report records.
- Whether outputs are transient, attached to Plane/GitHub as evidence, or
  published through another explicitly approved path.
- Renderer technology and interaction behavior, if any.
- Validation and QA evidence expected for the build card.
- Review checks that prevent derived visual state from becoming source of truth.

Until that separate card exists, the visual orchestration prototype remains a
documentation-only architecture contract under `studio/`.
