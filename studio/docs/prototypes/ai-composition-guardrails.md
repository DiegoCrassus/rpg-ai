# AI Composition Guardrails

This document defines guardrails for future SDLC Studio AI composition
assistance. It is a documentation-only contract for `INVES-68`; it does not
implement AI behavior, LLM calls, agent runners, command runners, workflow
runners, external API calls, persistence, generated outputs, frontend runtime,
backend runtime, or product code.

Future AI composition assistance is advisory only. It may help humans inspect
derived Studio outputs and draft reviewable suggestions, but it must remain
derived, non-authoritative, non-executable, and subordinate to `.sdlc/`,
`.cursor/`, Plane, GitHub, QA, review, and DevOps gates.

## Purpose

AI composition may eventually help humans understand SDLC Studio records without
changing source artifacts or durable work state.

Allowed purposes are:

- Explain workflow, graph, registry, validation, and report structure from
  derived Studio outputs.
- Summarize validation gaps for human inspection.
- Propose candidate annotations for derived Graph IR, Workflow IR, canvas, or
  inspection views.
- Identify missing or unclear source references.
- Draft suggested Plane-scoped follow-up text for a human or approved agent to
  review.
- Help humans inspect derived outputs while preserving source-of-truth
  boundaries.

AI composition must not approve work, execute work, persist work, or replace the
SDLC delivery process.

## Allowed Inputs

AI composition may read these inputs by reference:

- Derived Studio compiler outputs and compile report records.
- Derived Studio validator outputs, validation reports, and Validation Result IR
  records.
- Derived validation inspection records and canvas or view-model records.
- Graph IR and Workflow IR records governed by existing Studio contracts and
  schemas.
- Studio contracts such as `studio/source-boundaries.md`,
  `studio/docs/contracts/graph-ir-contract.md`, `studio/docs/contracts/validation-result-ir-contract.md`,
  `studio/compiler-validator-boundaries.md`,
  `studio/visual-orchestration-prototype.md`, and this document.
- Roadmap guidance from `docs/roadmap/sdlc-studio-mvp-roadmap.md`.
- Source references to `.sdlc/`, `.cursor/`, `.sdlc/registry/`, Plane card IDs,
  and GitHub refs.

Inputs must be source references, concise identifiers, or derived records that
already preserve source references. AI composition must not copy authoritative
rule bodies, command bodies, lifecycle text, prompts, hook logic, templates,
source file bodies, CI logs, generated output bodies, local evidence, or durable
work state into prompts, suggestions, reports, archives, or generated files.

## Required Output Boundaries

Every AI-assisted suggestion must:

- Cite the path, Plane ID, GitHub ref, derived record ID, or other source
  reference that grounds the suggestion.
- Carry a clear `derived_non_authoritative` reminder or equivalent wording.
- Distinguish observed derived data from proposed human follow-up.
- Avoid claiming live freshness for Plane, GitHub, CI, workflow status, or
  repository state unless an approved agent separately queried the authoritative
  system inside the proper gate.
- Route any proposed durable change into Plane-scoped work instead of applying
  it directly.

AI output is not a workflow definition, gate result, validation result, delivery
record, or source-of-truth update.

## Allowed AI Actions

Within the advisory boundary, future AI composition may:

- Explain how a derived workflow, graph, registry relationship, report, canvas
  record, or validation inspection record is structured.
- Summarize validation gaps already present in derived validator, inspection, or
  report outputs.
- Propose candidate annotations that remain derived until reviewed and scoped
  through the SDLC process.
- Identify missing, stale, ambiguous, or incomplete source references.
- Draft suggested Plane-scoped follow-up text for humans or approved agents to
  adapt in Plane.
- Help humans inspect derived outputs by grouping findings, naming risks, or
  pointing to relevant source references.

These actions are advisory reading and drafting actions only. They must not
create, modify, execute, validate, approve, persist, or publish source or
delivery state.

## Prohibited AI Actions

AI composition must not:

- Mutate `.sdlc/`, `.cursor/`, `.sdlc/registry/`, `studio/`, `app/`, Plane, or
  GitHub.
- Replace Plane for card scope, planning, state, comments, or durable delivery
  evidence.
- Replace GitHub for pull requests, reviews, checks, CI state, merge state,
  branch history, or repository history.
- Run workflow commands, shell commands, command runners, workflow runners,
  agent runners, validators, doctor checks, lint, tests, CI, MCP tools, external
  APIs, LLM APIs, backend APIs, frontend APIs, or persistence layers.
- Call agents or route work between agents.
- Create branches, commits, pull requests, local tickets, backlog files, specs,
  generated artifacts, local evidence files, prompt archives, output archives,
  or durable work records.
- Approve gates, mark Plane cards Done, complete QA, approve review, merge
  branches, finish workflows, or publish delivery evidence.
- Claim that derived Studio output is authoritative source, live Plane state,
  live GitHub state, CI evidence, QA evidence, review approval, merge state, or
  durable delivery evidence.

## Human And Agent Gates

Any durable source change suggested by AI must enter the normal SDLC path before
it exists as work:

- A Plane-scoped card defines the work, scope, and acceptance criteria.
- The workflow gate is opened with the appropriate branch and card.
- Implementer makes focused, reversible changes on the feature branch.
- QA validates against the acceptance criteria with real evidence.
- Reviewer approves or requests changes.
- DevOps handles PR, merge, and release flow after approval.
- The workflow finish path records completion through the approved process.

AI suggestions can inform these steps, but they cannot satisfy or skip them.

## Evidence Boundary

AI composition output is not:

- QA evidence.
- Review approval.
- CI evidence.
- Plane evidence.
- GitHub state.
- Workflow gate approval.
- Merge readiness.
- Durable delivery evidence.
- Durable work state.

Evidence belongs in the authoritative systems and stages defined by the SDLC
process. Studio AI assistance may point to evidence requirements or draft
follow-up text, but it must not create local evidence files or present advisory
text as completed validation.

## Freshness Boundary

AI composition may summarize the derived records it was given, but it must not
claim current Plane, GitHub, CI, workflow, branch, or repository status unless an
approved agent separately queried that authoritative system inside the proper
workflow gate.

When freshness is unknown, AI output should state that the summary is based on
derived inputs and source references only. The output should keep the
`derived_non_authoritative` reminder visible wherever a reader could mistake a
summary for live state.

## No-Persistence Boundary

AI composition must not introduce local AI memory, generated prompt archives,
generated response archives, local task records, backlog records, specs,
evidence files, generated Studio outputs, database records, caches, or other
durable state.

Future persistence, if ever needed, requires a separate Plane card, architecture
review, implementation gate, QA evidence, review approval, and DevOps flow.

## Relationship To Existing Studio Contracts

This contract builds on existing Studio boundaries without copying their
authoritative content:

- `studio/source-boundaries.md` defines Studio source-of-truth terminology and
  the derived, non-executable boundary.
- `studio/compiler-validator-boundaries.md` defines compiler, validator, and
  report boundaries for derived records.
- `studio/docs/contracts/graph-ir-contract.md` and
  `studio/docs/contracts/validation-result-ir-contract.md` define descriptive IR contracts.
- `studio/visual-orchestration-prototype.md` defines the derived visual
  inspection boundary.
- `docs/roadmap/sdlc-studio-mvp-roadmap.md` names AI composition as future
  advisory work that must preserve human review and SDLC gates.

Where this document and a source authority appear to overlap, the source
authority remains authoritative in its domain. This document only constrains
future Studio AI composition work.

## Non-Goals

This card does not:

- Implement AI runtime, LLM integration, prompt execution, agent execution,
  command execution, workflow execution, validators, doctor checks, lint, tests,
  CI execution, external API calls, MCP tool calls, persistence, services,
  schedulers, queues, databases, backend behavior, frontend behavior, UI
  behavior, or product runtime behavior.
- Add dependencies, generated outputs, generated artifacts, local tickets,
  backlog files, specs, evidence files, `studio/examples/`, `studio/generated/`,
  or `app/` changes.
- Define source editing behavior, branch creation, commits, pull requests, gate
  approval, QA approval, review approval, merge behavior, Done transitions, or
  workflow finish behavior for AI composition.
- Replace `.sdlc/`, `.cursor/`, `.sdlc/registry/`, Plane, GitHub, Studio
  contracts, QA, Reviewer, DevOps, or the existing SDLC process.

Until a separate Plane card opens a future implementation gate, AI composition
remains only a documented advisory boundary for future Studio work.
