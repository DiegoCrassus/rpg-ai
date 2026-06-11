# SDLC Studio Foundation Roadmap (historical)

> **Naming:** This document describes the **Studio Foundation** delivery (engine + CLI).  
> **Do not use “MVP” for new Plane epics or titles.**  
> **Active roadmap:** [`sdlc-studio-service-roadmap.md`](sdlc-studio-service-roadmap.md) — Studio as a **service** (backend, frontend, observability, visual builders).

## Purpose

This roadmap described the path from SDLC Studio Foundation to a **minimum engine loop** (CLI and derived models). That loop is **delivered** (epic INVES-53). The **usable product** (dashboard, React Flow, builders, live observability) is planned in the Service roadmap linked above.

This file is retained as the phase-by-phase specification for what was built in `studio/`. It is a documentation-only planning artifact for future Plane-scoped work; it does not implement Studio behavior, modify source artifacts, or create local task evidence.

The current foundation is anchored in `studio/`, `studio/schemas/`, `.sdlc/registry/`, `.sdlc/`, and `.cursor/`. These areas define the modeling context and source-of-truth boundaries for future Studio work:

- `studio/` is the home for SDLC Studio Foundation documentation and descriptive schemas.
- `studio/schemas/` describes future Studio-readable contracts for graphs, workflows, registry entities, and validation results.
- `.sdlc/registry/` indexes existing `.sdlc/` and `.cursor/` artifacts by reference without copying authoritative content.
- `.sdlc/` remains the formal process, lifecycle, gate, command, template, and registry authority.
- `.cursor/` remains the Cursor-side authority for agents, rules, skills, hooks, and editor automation context.

## Research Principles

- React Flow is the preferred future candidate for an orchestration-style node and edge editor.
- TLDraw concepts may inform whiteboard-style sketching, annotation, and exploratory UX, but TLDraw should not drive the core orchestration model.
- The visual graph is never the source of truth; it is a derived view over formal artifacts.
- Compiler outputs must be derived from formal SDLC artifacts in `studio/`, `studio/schemas/`, `.sdlc/registry/`, `.sdlc/`, and `.cursor/`.
- Generated Studio artifacts must not copy authoritative rule bodies, command bodies, lifecycle rules, prompts, or templates.
- No distributed runtime, workflow runner, scheduler, backend service, or execution engine belongs in the initial MVP.
- Plane remains the workboard source of truth for cards, state, planning, and delivery evidence.

## Phase Roadmap

### 1. Foundation Baseline

Goal: establish a clear baseline of the existing Studio Foundation and its relationship to the live SDLC system.

Deliverables:

- A reviewed inventory of the current `studio/`, `studio/schemas/`, `.sdlc/registry/`, `.sdlc/`, and `.cursor/` foundation.
- A concise source-of-truth map that separates authoritative artifacts from derived Studio views.
- A baseline terminology list for entities such as workflow, stage, gate, agent, command, handoff, registry entity, and validation result.

Inputs:

- Existing `studio/` documentation.
- Schema descriptions in `studio/schemas/`.
- Registry indexes and relationships in `.sdlc/registry/`.
- Process, lifecycle, and command files under `.sdlc/`.
- Cursor agents, rules, skills, and hooks under `.cursor/`.

Outputs:

- A stable baseline for future modeling work.
- A list of foundation gaps that should become future Plane cards when ready.
- Confirmation that Studio Foundation remains separate from `app/`.

Validation/evidence:

- Review confirms the baseline references existing files instead of duplicating rule or command bodies.
- Registry references resolve to real `.sdlc/` and `.cursor/` paths.
- `make sdlc-doctor` remains the structural health gate for repository SDLC changes.

Risks:

- Baseline notes could drift from source artifacts if they copy too much detail.
- Studio terminology could conflict with existing lifecycle language.

Non-goals:

- No implementation files.
- No UI, runtime, backend, frontend, or database design.
- No changes to authoritative `.sdlc/` or `.cursor/` behavior.

Exit gate:

- The team can explain what exists today, where each source of truth lives, and which Studio views are derived.

### 2. Registry/Modeling Hardening

Goal: make the referential model strong enough to support generated views and validation without becoming a second source of truth.

Deliverables:

- Hardened conventions for registry entity IDs, paths, ownership, relationship types, and source references.
- Coverage expectations for SDLC artifacts that should be indexable by Studio.
- Modeling rules for how registry entries reference agents, skills, commands, gates, templates, and lifecycle docs.

Inputs:

- `.sdlc/registry/index.yaml`, `sdlc-artifacts.yaml`, `cursor-artifacts.yaml`, and `relationships.yaml`.
- `studio/schemas/registry-entity.schema.yaml`.
- Current `.sdlc/` and `.cursor/` artifact layout.

Outputs:

- A clearer registry model for compiler and graph work.
- A relationship vocabulary for parent, dependency, handoff, validation, ownership, and source-reference links.
- A checklist for adding or changing registry entries safely.

Validation/evidence:

- Registry entries are short, path-based, and do not copy authoritative text.
- Relationship records point to known entity IDs and valid source paths.
- Schema checks can identify missing required fields, duplicate IDs, and broken references.

Risks:

- Over-modeling could make registry maintenance too heavy.
- Weak relationship names could produce ambiguous graph edges later.

Non-goals:

- No local ticket, backlog, spec, or evidence system.
- No replacement for Plane as workboard source of truth.
- No executable workflow semantics in registry files.

Exit gate:

- Registry and schema rules are sufficient for a validator to detect missing entities, duplicate IDs, broken paths, and unsupported relationship types.

### 3. Graph Model/IR

Goal: define a descriptive intermediate representation for Studio graphs that can represent workflows, entities, relationships, annotations, and validation results.

Deliverables:

- A graph IR specification aligned with `studio/schemas/graph.schema.yaml`, `workflow.schema.yaml`, `registry-entity.schema.yaml`, and `validation-result.schema.yaml`.
- Node and edge categories for SDLC artifacts, agents, stages, gates, commands, handoffs, checks, and external systems.
- Annotation rules for notes, rationale, risks, open questions, and evidence hints.

Inputs:

- Studio schema documents.
- Hardened registry model.
- Current SDLC lifecycle and workflow documentation.
- Existing SDLC Workflow UI planning concepts.

Outputs:

- A non-executable graph contract for future compiler outputs.
- A workflow view model that can power CLI summaries and future visual prototypes.
- A validation result shape that can be attached to graph nodes and edges.

Validation/evidence:

- IR examples can describe real SDLC workflows without introducing runtime behavior.
- Every graph node and edge can trace back to a source artifact or declared derived relationship.
- Validation results can identify the source artifact, severity, message, and suggested next action.

Risks:

- The IR could become too UI-specific if it is shaped around a single canvas library too early.
- Derived annotations could be mistaken for authoritative process changes.

Non-goals:

- No React component model.
- No command runner, scheduler, or distributed runtime.
- No generated edits to `.sdlc/`, `.cursor/`, or registry files.

Exit gate:

- The graph IR can represent the current SDLC workflow as a derived, traceable, non-executable model.

### 4. Compiler/Validator

Goal: plan a future compiler and validator that read authoritative artifacts and emit Studio-readable graph, workflow, and validation outputs.

Deliverables:

- Compiler responsibilities for reading registry entries, schemas, lifecycle files, and Cursor artifacts.
- Validator responsibilities for schema compliance, reference integrity, relationship consistency, and source-of-truth boundaries.
- Output contracts for graph IR, workflow IR, validation results, and human-readable reports.

Inputs:

- Hardened registry/modeling rules.
- Graph IR specification.
- `studio/schemas/` contracts.
- `.sdlc/` lifecycle and command references.
- `.cursor/` agent, rule, and skill references.

Outputs:

- Derived Studio graph artifacts.
- Derived workflow artifacts.
- Validation reports that point back to source artifacts.
- Machine-readable results suitable for CLI and preview tools.

Validation/evidence:

- Compiler outputs are reproducible from source artifacts.
- Validator fails on broken references, schema drift, duplicate IDs, unsupported relationships, and copied authoritative content.
- Reports distinguish warnings from blocking failures.

Risks:

- Compiler behavior could accidentally encode policy outside `.sdlc/` and `.cursor/`.
- Validation noise could reduce trust if warnings are not actionable.

Non-goals:

- No automatic source edits.
- No runtime execution of workflows.
- No UI implementation.

Exit gate:

- A future implementation can generate and validate Studio-readable artifacts from authoritative sources without changing those sources.

### 5. CLI Command Center

Goal: define a CLI-centered MVP workflow for discovery, graph generation, validation, preview, and reporting.

Deliverables:

- Command plan for read-only discovery, compile, validate, preview, and report flows.
- Exit-code strategy for blocking failures, warnings, and successful runs.
- Output format guidance for human-readable summaries and machine-readable files.

Inputs:

- Compiler/validator contracts.
- Existing `.sdlc/dsl/cli.py` workflow conventions.
- Doctor validation expectations.
- Plane and GitHub process boundaries.

Outputs:

- A command center design that can serve humans, agents, and CI-style checks.
- Standard validation summaries for future QA and reviewer evidence.
- A path for integrating Studio checks with existing SDLC gates without replacing them.

Validation/evidence:

- CLI checks can be run locally and produce deterministic output.
- Commands do not mutate source artifacts unless a future Plane card explicitly scopes that behavior.
- CLI summaries can be attached to Plane as delivery evidence.

Risks:

- CLI scope could expand into workflow execution.
- Command output could become hard to review if graph data is too verbose.

Non-goals:

- No production service.
- No distributed job runner.
- No replacement for existing SDLC workflow commands.

Exit gate:

- The MVP has a clear command-line loop: discover sources, compile derived artifacts, validate them, preview workflow behavior, and report results.

### 6. Visual Orchestration Prototype

Goal: prototype a derived visual orchestration view that helps humans understand SDLC workflows without making the canvas authoritative.

Deliverables:

- A future React Flow prototype plan for node/edge workflow visualization.
- Visual mapping rules from graph IR nodes and edges to canvas elements.
- UX notes for selecting nodes, inspecting source references, showing validation state, and following handoff paths.

Inputs:

- Graph IR and workflow IR.
- Compiler outputs.
- Validation results.
- Research principles for React Flow and TLDraw concepts.

Outputs:

- A derived visual graph prototype concept.
- Interaction requirements for inspection, filtering, validation overlays, and source links.
- A clear boundary that editing the visual graph does not change authoritative source artifacts in the MVP.

Validation/evidence:

- Prototype views can be regenerated from compiler outputs.
- Every displayed node and edge links back to a source artifact or derived relationship.
- Validation warnings and failures are visible without becoming local evidence records.

Risks:

- Users may assume canvas edits are source-of-truth changes.
- UI concerns could leak back into the IR if not carefully separated.

Non-goals:

- No durable frontend architecture decision in this roadmap.
- No `app/` changes.
- No canvas-driven workflow execution.

Exit gate:

- A human can navigate the derived graph, inspect sources, and understand validation state while the formal artifacts remain authoritative.

### 7. AI Composition Prototype

Goal: plan AI-assisted workflow drafting, explanation, and gap detection over formal artifacts while preserving human and SDLC gate review.

Deliverables:

- AI use cases for explaining workflows, suggesting missing registry links, drafting candidate graph annotations, and identifying validation gaps.
- Guardrails for human review, Plane-scoped work creation, and source-of-truth boundaries.
- Prompt and output expectations that reference artifacts without copying protected authoritative bodies.

Inputs:

- Compiler outputs.
- Validation reports.
- Registry and graph IR.
- Existing agent, skill, and rule references in `.cursor/`.
- SDLC lifecycle requirements in `.sdlc/`.

Outputs:

- Candidate suggestions for future Plane-scoped changes.
- Human-readable explanations of workflow structure and risks.
- Draft annotations that remain derived until reviewed and scoped through SDLC.

Validation/evidence:

- AI suggestions are traceable to source artifacts and validation findings.
- Suggested source changes are not applied automatically.
- Any durable change is routed through Plane, branch, review, QA, and DevOps gates.

Risks:

- AI output could hallucinate process rules or invent artifacts.
- Draft suggestions could be mistaken for approved work.

Non-goals:

- No autonomous source mutation.
- No bypass of Architect, QA, Reviewer, or DevOps gates.
- No local backlog or evidence files.

Exit gate:

- AI can assist discovery and composition while all authoritative changes remain gated through the existing SDLC process.

### 8. Simulation/Runtime Preview

Goal: provide non-executing previews of SDLC state transitions, gate outcomes, handoffs, and failure paths.

Deliverables:

- Simulation model for walking through stages, gates, next-agent routing, validation states, and blocker paths.
- Preview output for common scenarios such as docs-only change, feature implementation, QA failure, reviewer escalation, and DevOps finish.
- Clear labels that previews are explanatory and not a workflow runner.

Inputs:

- Workflow IR.
- Compiler outputs.
- Existing lifecycle and gate definitions.
- Handoff conventions in `.sdlc/memory/`.

Outputs:

- Read-only transition previews.
- Scenario reports that explain expected evidence and next actions.
- Failure-path documentation for common blocked states.

Validation/evidence:

- Preview scenarios match existing `.sdlc/` lifecycle documentation.
- Simulated transitions do not call Plane, GitHub, shell commands, agents, or runtime services.
- Results distinguish expected path, blocked path, and unsupported path.

Risks:

- Preview terminology could imply executable runtime behavior.
- Users could trust a preview more than live gate status.

Non-goals:

- No distributed runtime.
- No scheduler, queue, workflow engine, backend service, or command execution.
- No replacement for `workflow status`, Plane state, or GitHub checks.

Exit gate:

- Users can preview how a change should move through the SDLC without executing or modifying anything.

### 9. Publish/Operate Workflows

Goal: define how Studio outputs, validation reports, visual previews, and operating evidence are published and used in the existing delivery process.

Deliverables:

- Operating model for where generated Studio outputs are reviewed, attached, or published.
- Plane evidence expectations for future Studio work.
- GitHub PR review expectations for changes to schemas, registry, CLI behavior, or generated docs.

Inputs:

- CLI command center design.
- Compiler/validator outputs.
- Preview and visual prototype outputs.
- Existing Plane and GitHub delivery flow.

Outputs:

- A publish model for generated reports and docs.
- Reviewer and QA evidence expectations.
- Roll-forward and rollback considerations for future Studio metadata changes.

Validation/evidence:

- Plane remains the record for work item state and delivery evidence.
- PRs show source changes separately from generated outputs.
- Doctor and Studio validations are both considered before merge when relevant.

Risks:

- Generated outputs could clutter reviews if not scoped.
- Evidence could drift into local files instead of Plane.

Non-goals:

- No production launch.
- No public hosted Studio service.
- No new workboard or evidence repository.

Exit gate:

- Future Studio work has a clear operating path for validation, review, evidence, and publication without replacing Plane or GitHub.

### 10. MVP Readiness

Goal: define the minimum usable SDLC Studio loop and the readiness gates required before calling it an MVP.

Deliverables:

- MVP checklist covering registry coverage, schema stability, compiler/validator behavior, CLI workflows, derived graph preview, AI assistance guardrails, and simulation preview.
- Acceptance criteria for the first usable end-to-end Studio loop.
- Known limitations and post-MVP backlog candidates to be created in Plane only when approved.

Inputs:

- All prior phase outputs.
- QA, review, and Doctor evidence.
- User feedback from CLI, visual, AI, and preview prototypes.

Outputs:

- A usable loop: discover authoritative artifacts, compile derived Studio outputs, validate them, preview workflows, inspect graph views, and publish evidence through Plane/GitHub.
- MVP readiness report for reviewers.
- Post-MVP candidate list for Plane-scoped planning.

Validation/evidence:

- Registry and schema checks pass.
- Compiler and validator checks pass with documented warnings only.
- CLI checks produce deterministic output and meaningful exit codes.
- Preview and simulation checks match lifecycle expectations.
- Docs review confirms source-of-truth boundaries and exclusions.
- `make sdlc-doctor` passes.

Risks:

- MVP criteria could expand into production launch expectations.
- Prototype UI or AI workflows could be treated as durable architecture too early.

Non-goals:

- No production launch scope.
- No distributed runtime.
- No source-of-truth replacement for `.sdlc/`, `.cursor/`, `studio/`, `studio/schemas/`, `.sdlc/registry/`, Plane, or GitHub.

Exit gate:

- The MVP is ready when a user can complete the Studio loop with traceable derived artifacts, passing validations, reviewed documentation, and Plane-backed evidence.

## Consolidated Validation Gates

Registry/schema checks:

- Validate registry entity IDs, source paths, relationship references, duplicate IDs, and unsupported relationship types.
- Validate Studio outputs against `studio/schemas/` contracts.
- Confirm generated artifacts reference authoritative files without copying rule bodies, command bodies, prompts, templates, or lifecycle text.

Compiler/validator checks:

- Confirm compiler outputs are reproducible from `studio/`, `studio/schemas/`, `.sdlc/registry/`, `.sdlc/`, and `.cursor/`.
- Confirm validator results identify severity, source path, message, and suggested next action.
- Fail on broken references, schema drift, copied authoritative content, and invalid source-of-truth assumptions.

CLI checks:

- Verify command outputs are deterministic and reviewable.
- Verify exit codes distinguish pass, warning, and failure states.
- Verify CLI commands do not mutate source artifacts unless separately scoped by a future Plane card.

Preview/simulation checks:

- Verify previews are non-executing and do not call Plane, GitHub, shell commands, agents, or services.
- Verify simulated transitions match `.sdlc/` lifecycle and gate behavior.
- Verify previews clearly distinguish expected paths, blocked paths, and unsupported paths.

Docs review:

- Confirm documentation is written in English for repository artifacts.
- Confirm source-of-truth boundaries are explicit.
- Confirm Plane remains the workboard source of truth.
- Confirm visual graph, AI suggestions, and simulation previews are derived aids only.

Doctor gate:

- Run `make sdlc-doctor` after structural SDLC changes and before declaring MVP readiness.
- Treat a non-zero Doctor exit code as blocking.
- Review warnings and either fix them or record why they are accepted in the appropriate Plane evidence.

## Explicit Exclusions

- No `app/` changes.
- No implementation files in this roadmap work.
- No edits to `studio/`, `studio/schemas/`, `.sdlc/registry/`, `.sdlc/` process files, `.cursor/`, or plan files.
- No `studio/examples/`.
- No `specs/`.
- No local tickets, backlog, or evidence files.
- No production launch scope.
- No distributed runtime, workflow runner, scheduler, backend service, or execution engine in the initial MVP.
