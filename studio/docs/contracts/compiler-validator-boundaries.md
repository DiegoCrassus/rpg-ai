# Compiler And Validator Boundary Contract

This document defines the SDLC Studio compiler and validator phase boundaries as
descriptive, non-executable architecture contracts. It explains what future
compiler and validator work may read, derive, and report without implementing
compiler execution, validator execution, command running, workflow execution, UI
behavior, backend behavior, frontend behavior, persistence, schedulers, APIs, or
AI composition.

The terms "compiler" and "validator" in this document name future Studio phases.
They do not define executable behavior in this card. Any future implementation
must be scoped by separate Plane cards, workflow gates, implementation plans, QA
evidence, review, and DevOps flow.

## Source Of Truth Boundaries

The compiler and validator phases must preserve the repository's existing
authorities:

- `.sdlc/` remains authoritative for SDLC process, lifecycle, workflows, gates,
  stages, scripts, templates, doctor checks, and handoff state.
- `.cursor/` remains authoritative for agents, skills, rules, commands, hooks,
  MCP configuration shape, and Cursor-local behavior.
- Plane remains authoritative for card scope, work item state, planning,
  comments, and durable delivery evidence.
- GitHub remains authoritative for pull requests, reviews, checks, CI state,
  merge state, branch history, and repository history.
- `.sdlc/registry/` remains a referential index over `.sdlc/` and `.cursor/`;
  it is not authoritative for the behavior of referenced artifacts.
- `studio/` documents and `studio/engine/schemas/` describe derived or referential
  Studio contracts only.

Graph IR, Workflow IR, Validation Result IR, and Studio reports are derived or
referential artifacts. They are non-executable and must not become workflow
definitions, command invocations, gate enforcers, product runtime contracts,
local evidence stores, or replacements for the authorities above.

## Compiler Boundary

The future compiler is a derivation boundary. It may assemble Studio-readable IR
and report records from authoritative and referential inputs, but it does not
change those inputs and does not run the workflow it describes.

### Compiler Inputs

Compiler inputs are references to existing sources:

- Studio contracts such as `studio/source-boundaries.md`,
  `studio/docs/contracts/graph-ir-contract.md`, `studio/docs/contracts/validation-result-ir-contract.md`, this
  contract, and `studio/README.md`.
- Studio schema documents under `studio/engine/schemas/`, including Graph IR, Workflow
  IR, registry entity, registry relationship, and Validation Result IR schemas.
- Referential registry files such as `.sdlc/registry/index.yaml`,
  `.sdlc/registry/sdlc-artifacts.yaml`,
  `.sdlc/registry/cursor-artifacts.yaml`, and
  `.sdlc/registry/relationships.yaml`.
- Authoritative SDLC sources such as `.sdlc/sdlc.yaml`,
  `.sdlc/stages/lifecycle.yaml`, `.sdlc/workflows/transitions.yaml`,
  `.sdlc/gates/paths.yaml`, and relevant `.sdlc/process/` documents.
- Authoritative Cursor sources such as `.cursor/agents/`, `.cursor/skills/`,
  `.cursor/rules/`, `.cursor/hooks*`, `.cursor/commands/` when present, and
  `.cursor/mcp.json` when in scope.
- Plane and GitHub identifiers as external authority references only.

Compiler inputs must be read by reference. The compiler boundary must not copy
rule bodies, lifecycle text, prompts, command bodies, hook logic, templates,
source file bodies, generated output bodies, CI logs, local evidence, or durable
work state into derived records.

### Compiler Derived Outputs

Compiler outputs are derived or referential records for future Studio consumers:

- Graph IR shaped by `studio/engine/schemas/graph.schema.yaml` and governed by
  `studio/docs/contracts/graph-ir-contract.md`.
- Workflow IR shaped by `studio/engine/schemas/workflow.schema.yaml`.
- Registry summaries or relationship references that point back to
  `.sdlc/registry/` entries without making the registry authoritative.
- Compile report records that summarize source coverage, unresolved references,
  excluded source areas, non-goals, and suggested next actions.

These outputs may be displayed, reviewed, or passed to future Studio phases.
They do not execute workflows, enforce gates, call agents, invoke commands,
update Plane, update GitHub, persist operational state, or prove delivery
evidence.

### Compiler Non-Outputs

The compiler boundary must not emit:

- Authoritative `.sdlc/`, `.cursor/`, Plane, GitHub, or `.sdlc/registry/` state.
- Source edits, runtime configuration, command arguments, shell invocations,
  agent prompts, copied rule bodies, lifecycle bodies, templates, hook logic, CI
  logs, local evidence, tickets, backlog, specs, or generated source files.
- UI-specific props, canvas coordinates, React Flow nodes, TLDraw shapes,
  backend APIs, frontend APIs, service contracts, persistence models, scheduler
  definitions, or database models.
- Executable compiler internals, validator internals, workflow runners, command
  runners, AI orchestration, or deployment behavior.

## Validator Boundary

The future validator is a checking boundary. It may describe findings over
authoritative sources and compiler-derived records, but it does not make Studio
the authority for the sources it checks.

### Validator Inputs

Validator inputs are references to:

- The same authoritative and referential sources available to the compiler.
- Derived Graph IR and Workflow IR records produced by future compiler work.
- Referential registry entity and registry relationship records.
- Compiler report records that summarize coverage, unresolved references, and
  intentionally excluded areas.
- Validation Result IR semantics from `studio/docs/contracts/validation-result-ir-contract.md`
  and schema shape from `studio/engine/schemas/validation-result.schema.yaml`.

Validator inputs remain non-authoritative unless they already come from an
authoritative source such as `.sdlc/`, `.cursor/`, Plane, or GitHub. Derived
inputs cannot override their source references.

### Validator Outputs

Validator outputs are descriptive result and report records:

- Validation Result IR records shaped by
  `studio/engine/schemas/validation-result.schema.yaml`.
- Human-readable report records that reference source paths, derived object IDs,
  Plane cards, and GitHub refs concisely.
- Status outcomes `pass`, `warn`, `fail`, and `not_run`.
- Message levels `info`, `warn`, and `error`.

Validator outputs do not enforce gates, move workflow stages, update Plane,
update GitHub, rerun CI, invoke doctor, invoke lint, call shell commands, call
external APIs, or store durable evidence locally.

## Failure Semantics

Validation statuses are descriptive and non-executable:

- `fail` is reserved for blocking defects in the derived or referential model,
  such as YAML parse errors, schema drift, missing required fields, duplicate
  IDs, broken source paths, broken registry or graph relationship targets,
  unsupported relationship types, copied authoritative content, forbidden output
  paths, or claims that derived artifacts are authoritative.
- `warn` covers non-blocking but actionable gaps such as incomplete optional
  coverage, unclear summaries, missing optional annotations, accepted
  integration-environment warnings, or source areas intentionally deferred to a
  later card.
- `not_run` describes checks intentionally skipped because their source, derived
  artifact, environment, or future implementation gate is absent.
- `pass` describes a completed check result only. It must not imply live
  freshness, durable delivery evidence, CI success, merge readiness, or gate
  approval unless a separate future executable card defines and verifies that
  behavior.

## Report Contracts

Compiler and validator reports are derived artifacts. They may help future
Studio readers understand coverage and findings, but they are not Plane
evidence, GitHub state, workflow gates, source-of-truth records, generated
outputs, or execution logs.

Compiler and validator reports use one shared envelope shape:

- `id`: stable report identifier such as `report.studio.compile` or
  `report.studio.validate`.
- `kind`: `compile` or `validate`.
- `status`: one of `pass`, `warn`, `fail`, or `not_run`.
- `authority`: exactly `derived_non_authoritative`.
- `summary`: deterministic description and counts used by both JSON and text
  rendering.
- `sections`: deterministic report sections for coverage, findings, boundaries,
  skipped work, or other concise derived summaries.
- `source_refs`: concise repository path or external authority pointers only.
- `non_goals`: inherited report boundaries that prevent source-of-truth drift.

Reports must:

- Distinguish compiler coverage, validator findings, source authority
  boundaries, skipped checks, non-goals, and suggested next actions.
- Reference sources by repository path or external identifier without copying
  authoritative source bodies, generated output bodies, command output bodies,
  CI logs, local evidence, or durable delivery evidence.
- Mark Graph IR, Workflow IR, Validation Result IR, and report records as
  derived or referential and non-executable.
- Route any future durable evidence to Plane or GitHub through the appropriate
  QA, review, and DevOps flow instead of storing it in local Studio files.

## Future Implementation Gate

This contract does not authorize execution. Future compiler or validator
implementation requires separate Plane cards, open workflow gates,
implementation scope, local verification, QA evidence, reviewer approval, and
DevOps flow. Those future cards must define their own executable behavior and
must preserve the source-of-truth boundaries in this document.

## Explicit Non-Goals

This contract does not:

- Implement compiler execution, validator execution, workflow execution, command
  execution, gate enforcement, CI execution, lint execution, doctor execution, or
  runtime behavior.
- Define UI behavior, React Flow behavior, TLDraw behavior, backend behavior,
  frontend behavior, API behavior, service behavior, scheduler behavior,
  persistence, databases, AI composition, LLM orchestration, or deployment
  behavior.
- Create `app/` changes, `studio/examples/`, `specs/`, local tickets, local
  backlog, local task evidence, generated outputs, durable evidence files, or
  product runtime artifacts.
- Replace `.sdlc/`, `.cursor/`, Plane, GitHub, or `.sdlc/registry/` as source
  authorities.
- Make Graph IR, Workflow IR, Validation Result IR, or reports executable.
