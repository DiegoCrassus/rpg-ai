# SDLC Workflow UI Planning

## Purpose

This document captures initial planning notes for a future auxiliary SDLC workflow management UI. The idea is a human-facing interface for understanding, planning, and tracking SDLC workflows as connected blocks, similar in spirit to visual workflow tools such as n8n, while staying aligned with the repository's Plane-backed SDLC process.

This is planning-only documentation. It does not define or implement a frontend, backend, API, workflow engine, command runner, database, or execution architecture.

## Relationship To Studio Foundation

`studio/` is the future SDLC Studio Foundation area for descriptive schemas and referential indexes over real `.sdlc/` and `.cursor/` artifacts. Future UI planning can use Studio Foundation as its modeling base, but this document remains a planning note and does not choose or implement UI architecture.

The existing `app/` directory is unrelated to SDLC Studio Foundation. No assumptions in this planning document should be read as product code direction for `app/`.

## Scope

The future UI concept may help agents and humans visualize how SDLC work moves through stages, gates, commands, handoffs, reviews, and operating practices. It should support planning and communication around workflow design without replacing Plane, GitHub, existing CLI commands, or the current SDLC source-of-truth files.

Initial scope for this document:

- Describe the conceptual block model for SDLC workflows.
- Capture annotation needs for blocks, connections, and workflow decisions.
- Outline catalog ideas for commands, workflows, reusable block types, and cultural practices.
- Provide a lightweight planning and tracking reference for future Plane-scoped work.

## Core Concepts / Block Model

- **Workflow**: A named SDLC process or sub-process, such as planning, implementation, QA, review, release, incident response, or workflow discovery.
- **Block**: A visual unit representing a stage, gate, command, agent responsibility, decision point, artifact, or operating practice.
- **Connection**: A directed relationship between blocks that shows expected flow, dependency, handoff, or feedback loop.
- **Stage / gate**: A lifecycle checkpoint that defines required evidence, allowed transitions, and blocking conditions.
- **Command**: A documented CLI or automation entry point that supports a workflow step, such as validation, discovery, doctor checks, or state transitions.
- **Practice**: A repeatable team norm or culture pattern, such as no local ticket files, evidence on Plane, review before merge, or small reversible changes.
- **Handoff**: Context passed between humans, agents, or workflow stages, including current card, branch, stage, validation results, blockers, and next agent.

The block model is descriptive. Blocks and connections are planning objects, not executable definitions.

## Annotation Model

Annotations should help explain why a workflow exists, how it should be used, and what still needs design work. Useful annotation types include:

- **Notes**: Clarifying context for a block, connection, command, or practice.
- **Rationale**: Why a workflow step, gate, or convention exists.
- **Open questions**: Unresolved design or ownership issues.
- **Risks**: Known failure modes, ambiguity, or process gaps.
- **TODOs**: Future Plane-scoped work that still needs triage and planning.
- **Evidence hints**: Pointers to the kind of validation or review evidence expected at a gate.
- **Handoff context**: Information needed by the next human or agent to continue the workflow safely.

Annotations should support future workflow design without becoming a local ticket, backlog, or evidence system.

## Workflow And Command Catalog

A future catalog could organize planning material around:

- **Workflow families**: Feature delivery, docs-only changes, SDLC meta changes, bug fixes, hotfixes, QA, review, DevOps, observability, and rollback.
- **Reusable block types**: Plane card, branch, gate, command, agent task, validation result, review decision, PR, merge, and post-merge update.
- **Command references**: Existing SDLC commands such as workflow discovery, workflow status, workflow start, workflow finish, validation, and doctor checks.
- **Operating practices**: Plane as source of truth, feature branches per child card, no local specs or ticket files, real validation evidence, reviewer approval before merge, and green CI before integration.
- **Culture patterns**: Small reviewable changes, explicit non-goals, handoffs with blockers, and process changes through SDLC-scoped cards.

The catalog should describe candidate concepts and relationships. It should not define executable command behavior or replace existing command documentation.

## Planning / Tracking Usage

This document can help future work by giving teams a shared vocabulary for discussing a workflow UI before implementation choices are made. It can be used to:

- Identify which workflow blocks and annotations need to be represented.
- Track open questions that should become future Plane work when they are ready.
- Compare workflow design ideas against the current SDLC lifecycle and governance rules.
- Evaluate future Studio Foundation graph and registry models without turning them into runtime behavior.
- Plan diagrams, user journeys, and catalog structure for future architecture review.
- Clarify how a UI could support workflow understanding without becoming the source of truth.

Plane remains the workboard source of truth for tasks, state, and delivery evidence.

## Non-Goals

- No frontend implementation or framework selection.
- No backend, API, database, persistence, or sync design.
- No workflow engine, runner, scheduler, or command execution model.
- No changes to existing SDLC gates, CLI commands, Plane usage, or GitHub flow.
- No local tickets, backlog files, specs, or evidence records.
- No product code changes under `app/`.
- No durable architecture decision for the future UI.

## Open Questions

- Which SDLC workflows should be modeled first?
- What is the minimum useful set of block and connection types?
- How should annotations distinguish notes, rationale, risks, TODOs, and handoff context?
- Which existing commands and practices belong in an initial catalog view?
- How should a future UI reference Plane cards without replacing Plane as the source of truth?
- What future architecture review is needed before selecting a framework, API, database, or workflow engine?
- How should workflow design changes be reviewed and versioned if this concept moves beyond planning?

## Initial Next Steps

1. Use this README as the initial planning reference for future Plane-scoped work.
2. Validate terminology against the current SDLC lifecycle, gates, commands, and handoff conventions.
3. Identify the first workflow family that would benefit from a visual block model.
4. Draft future acceptance criteria for a planning artifact, prototype, or architecture review without choosing implementation technology.
5. Keep any future tracking in Plane and any future implementation behind a separately approved SDLC card.
