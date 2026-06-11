# Graph IR Contract

This document defines the SDLC Studio Graph IR as a descriptive,
non-executable intermediate representation for future Studio graph views.
Graph IR describes how Studio may refer to existing SDLC and Cursor sources as
nodes, directed edges, annotations, source references, and validation
attachments. It does not define runtime behavior, generated outputs, UI
components, compiler behavior, validator behavior, or workflow execution.

## Source Of Truth Boundaries

Graph IR is derived and referential. It is never the source of truth for process
behavior, workflow state, workboard state, pull request state, CI state, merge
state, or delivery evidence.

Authoritative sources remain:

- `.sdlc/` for SDLC process, lifecycle, workflow, gates, stages, scripts,
  templates, doctor checks, and handoff state.
- `.cursor/` for Cursor agents, skills, rules, commands, hooks, and local
  Cursor behavior.
- Plane for card scope, work item state, comments, and durable delivery
  evidence.
- GitHub for pull requests, reviews, checks, CI state, merge state, branch
  history, and repository history.

`.sdlc/registry/` is a referential index over `.sdlc/` and `.cursor/`
artifacts. Graph IR may point to registry entities and relationships, but it
does not make the registry authoritative for the behavior of referenced
artifacts.

## Relationship To Existing Schemas

Graph IR is the graph-level contract for `schemas/graph.schema.yaml`.
Supporting schemas remain focused on their own descriptive shapes:

- `schemas/workflow.schema.yaml` describes workflow views assembled from
  existing stages, agents, gates, and transitions.
- `schemas/registry-entity.schema.yaml` describes individual referential
  registry entities.
- `schemas/registry-relationship.schema.yaml` describes directed registry
  relationships.
- `validation-result-ir-contract.md` and
  `schemas/validation-result.schema.yaml` describe Studio-readable Validation
  Result IR records.

Graph IR may reference those concepts, but it does not implement validation,
compile workflows, execute commands, or persist generated graph outputs.

## Graph Model

A Graph IR document contains graph metadata, nodes, and edges.

Graph metadata identifies the graph view with a stable ID, name, description,
version, source references, optional annotations, optional validation
attachments, and explicit non-goals. Metadata explains the derived view; it does
not define operational state.

## Node Model

A node represents a descriptive graph object such as a workflow, stage, agent,
skill, command, gate, policy, template, hook, rule, module, registry entity,
validation concept, or artifact.

Each node has:

- A stable `id`.
- A `type` and `category` for classification.
- A human-readable `label`.
- Optional `registry_ref`, `entity_ref`, or `workflow_ref` pointers.
- Required `source_refs` that ground the node in real repository paths or
  external authorities.
- Optional `annotations`.
- Optional `validation_attachments`.

Node references are pointers only. Nodes must not copy authoritative rule
bodies, lifecycle text, prompts, command bodies, hook logic, templates,
evidence, generated outputs, or source file bodies.

## Edge Model

An edge represents a directed descriptive relationship between two nodes. The
direction is explicit as `from -> relation -> to`; inverse or bidirectional
meaning requires another edge.

Each edge has:

- A stable `id`.
- `from` and `to` node references.
- A `relation` type.
- Required `source_refs` that ground the relationship.
- Optional `label` or `summary`.
- Optional `annotations`.
- Optional `validation_attachments`.

Edges are non-executable. An edge may describe that one artifact governs,
validates, references, uses, contains, documents, indexes, hands off to, or
transitions to another artifact, but the edge does not run a command, move a
workflow, call an agent, enforce a gate, or invoke a validator.

## Annotations

Annotations are advisory and non-authoritative. They may help future Studio
views explain graph context, but they cannot override `.sdlc/`, `.cursor/`,
Plane, GitHub, or registry source references.

Allowed annotation kinds include:

- `note`
- `rationale`
- `risk`
- `open_question`
- `evidence_hint`
- `handoff_context`

Annotations must stay concise and referential. They must not store delivery
evidence, copied source bodies, generated output bodies, or durable work state.

## Source References

`source_refs` ground the derived graph in real sources. A source reference is
either:

- A repository path such as `.sdlc/...`, `.cursor/...`, `studio/...`, or
  `docs/...`.
- An external authority reference such as a Plane card ID or GitHub pull
  request/check reference.

Source references point to authority; they do not copy authority. Graph IR must
not copy rule bodies, lifecycle text, prompts, command bodies, hook logic,
templates, evidence, generated outputs, or source file bodies into source
references.

## Validation Attachments

Validation attachments describe Validation Result IR concepts for display or
traceability. Their semantics come from `validation-result-ir-contract.md` and
their schema vocabulary aligns with `schemas/validation-result.schema.yaml`,
including target reference, check type, status, messages, source references,
checker metadata, and timestamps.

Validation attachments do not run checks. They do not call doctor, lint, CI,
policy checks, path checks, custom validators, workflow gates, shell commands,
or external APIs. They are descriptive attachments only and must not copy or
store durable delivery evidence locally.

## Non-Executable Semantics

Graph IR is not coupled to UI libraries, canvas coordinates, React components,
React Flow, TLDraw, runtime state, command invocation, workflow execution,
compiler internals, validator logic, backend services, frontend code, APIs,
databases, AI composition, LLM orchestration, generated outputs, or local
delivery evidence.

Future UI, compiler, and validator cards may consume Graph IR as an input
contract, but those implementations must define their own behavior and preserve
the authority boundaries in this document.

## Non-Goals

Graph IR does not:

- Replace `.sdlc/`, `.cursor/`, Plane, GitHub, or `.sdlc/registry/`.
- Define workflow execution, command execution, gate enforcement, agent
  orchestration, compiler behavior, validator behavior, CLI behavior, UI
  behavior, backend behavior, frontend behavior, API behavior, database
  behavior, or AI composition.
- Store local tickets, backlog, specs, generated outputs, durable delivery
  evidence, PR state, CI state, merge state, or workboard state.
- Require or expose canvas coordinates, UI component props, React component
  names, React Flow node data, TLDraw shapes, runtime state, command arguments,
  shell invocations, or validator internals.
