# Validation Result IR Contract

This document defines the SDLC Studio Validation Result IR as a descriptive,
non-executable record shape for validation outcomes that future Studio work may
display, attach to Graph IR objects, or reference from derived reports.

Validation Result IR does not define a validator, command runner, gate enforcer,
compiler, CLI behavior, API behavior, database behavior, UI behavior, backend,
frontend, AI composition, workflow execution, or persistence model.

## Source Of Truth Boundaries

Validation Result IR records are derived descriptions. They are never the source
of truth for process behavior, workflow state, workboard state, pull request
state, CI state, merge state, repository state, or durable delivery evidence.

Authoritative sources remain:

- `.sdlc/` for SDLC process, lifecycle, workflow, gates, stages, scripts,
  templates, doctor checks, and handoff state.
- `.cursor/` for Cursor agents, skills, rules, commands, hooks, and local
  Cursor behavior.
- Plane for card scope, work item state, comments, and durable delivery
  evidence.
- GitHub for pull requests, reviews, checks, CI state, merge state, branch
  history, and repository history.

Validation Result IR may point to those authorities, but it must not copy their
authoritative bodies, generated outputs, command output bodies, local evidence
records, or durable work state.

## Record Shape

The schema is defined in `schemas/validation-result.schema.yaml`. A validation
result record has required top-level fields:

- `id`
- `target_ref`
- `check_type`
- `status`
- `messages`
- `source_refs`

Optional metadata includes `checked_by`, `checker_version`,
`checker_authority`, and `checked_at`. Metadata is descriptive only and must not
include invocation targets, command bodies, shell invocations, API calls,
validator internals, or freshness guarantees.

## IDs

Validation result IDs use the stable pattern `validation.<scope>.<name>`, for
example `validation.graph.relationship_targets`.

The ID names a descriptive record. It does not name an executable check, a
command, a gate, a workflow transition, or a durable evidence artifact.

## Target References

`target_ref` identifies the object or authority that the result describes. It
uses a structured `ref_type` and `ref` pair.

Supported target reference types are:

- `graph`: a derived Graph IR document or graph metadata object.
- `node`: a Graph IR node identifier.
- `edge`: a Graph IR edge identifier.
- `registry_entity`: a referential registry entity such as `sdlc.*` or
  `cursor.*`.
- `workflow`: a workflow identifier or workflow view reference.
- `stage`: a lifecycle or workflow stage reference.
- `path`: a repository path such as `.sdlc/...`, `.cursor/...`, `studio/...`,
  or `docs/...`.
- `plane`: a Plane card or work item reference.
- `github`: a GitHub pull request, review, check, branch, or repository
  reference.

A target reference points to the thing being described. It does not make Studio
authoritative for that target and does not imply that Studio can update it.

## Check Types

`check_type` is a descriptive category. It does not implement, trigger, or
enforce a check.

Supported check types are:

- `yaml_parse`
- `path_exists`
- `path_scope`
- `relationship_target`
- `doctor`
- `lint`
- `policy`
- `custom`

Future validator or compiler cards may define behavior for producing these
records, but this contract only defines the shape and semantics of the record.

## Status And Messages

`status` is an outcome label for display or traceability:

- `pass`
- `warn`
- `fail`
- `not_run`

`messages` contain concise human-readable text. Message levels are:

- `info`
- `warn`
- `error`

Messages may include optional source path context, plus line and column metadata
for human navigation. They must not copy authoritative source bodies, generated
output bodies, command output bodies, CI logs, local evidence records, or durable
delivery evidence.

## Source References

`source_refs` are required and unique. They ground the result in real sources
without copying those sources.

Supported source reference types are:

- `path`: a repository path.
- `plane`: a Plane card or work item reference.
- `github`: a GitHub pull request, review, check, branch, or repository
  reference.

Source references follow the same practical structure used by Graph IR:
`ref_type`, `ref`, and optional `summary`. The summary explains why the source
grounds the record, but it must remain concise and non-authoritative.

## Checker Metadata

`checked_by` may name a descriptive checker, tool, human review, or authority
label. `checker_version` may name a version string. `checker_authority` may
point to a source reference that explains where the checker concept comes from.

These fields are metadata only. They must not contain command strings, shell
invocations, API endpoints, workflow transition targets, agent handoff targets,
or validator implementation details.

`checked_at` is date-time metadata. It records when a result was recorded or
observed, but it does not guarantee freshness and does not imply that any live
check has just run.

## Relationship To Graph IR

Graph IR validation attachments use Validation Result IR concepts for embedded
summaries or references. A Graph IR object may carry a validation attachment for
display or traceability, and that attachment may point to a validation result
record by `validation_ref`.

Graph IR attachments remain descriptive. They must not run validation, call
doctor, call lint, call CI, call policy checks, check paths, enforce gates, move
cards, update pull requests, execute workflows, invoke commands, or store
durable evidence locally.

## Non-Goals

Validation Result IR does not:

- Replace `.sdlc/`, `.cursor/`, Plane, GitHub, or `.sdlc/registry/`.
- Define validator execution, compiler behavior, CLI behavior, workflow
  execution, command execution, gate enforcement, API behavior, database
  behavior, backend behavior, frontend behavior, UI behavior, AI composition, or
  persistence.
- Store local tickets, backlog, specs, generated outputs, durable delivery
  evidence, PR state, CI state, merge state, or workboard state.
- Require or expose command arguments, shell invocations, CI log bodies,
  validator internals, runtime state, or external API calls.
