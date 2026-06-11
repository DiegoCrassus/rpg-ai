# Studio Operating Model

This document is a derived, non-executable operating model for `INVES-73`
(roadmap phase 9). It explains how operators and reviewers use Studio CLI
outputs, previews, and evidence projections without replacing Plane, GitHub, or
formal SDLC artifacts. It references source areas by path and does not copy
authoritative rule bodies, lifecycle text, command bodies, prompts, or templates.

Related contracts: `studio/source-boundaries.md`,
`studio/compiler-validator-boundaries.md`,
`studio/ai-publish-evidence-prototype.md`, and
`docs/roadmap/sdlc-studio-mvp-roadmap.md`.

## Purpose

Operators and reviewers need a single map for:

- Which roles may use Studio outputs and what they must not treat as authority.
- How derived CLI reports, previews, and evidence projections fit the delivery
  flow.
- Where durable validation and delivery evidence is recorded (Plane and GitHub,
  never local Studio files).

## Roles And Boundaries

| Role or system | Boundary | Authority domain |
| --- | --- | --- |
| Human operator | Runs Studio CLI locally; reviews stdout; posts evidence to Plane; opens or reviews GitHub PRs | Must not treat CLI stdout as gate truth, card state, or merge approval |
| SDLC Orchestrator and subagents | Route work through `.sdlc/` pipeline data and `.cursor/` agent definitions | Authoritative for agent routing and delivery gates; Studio does not drive agents |
| Studio CLI (`python -m studio.cli`) | Derives in-memory reports from repository sources at `--root` | Non-authoritative, read-only, non-persisting; no Plane or GitHub mutation |
| `.sdlc/` | Process, lifecycle, gates, doctor, DSL, templates, handoff | Authoritative SDLC behavior and structural health gates |
| `.cursor/` | Agents, skills, rules, commands, hooks, MCP shape | Authoritative Cursor-side behavior |
| `.sdlc/registry/` | Referential index over `.sdlc/` and `.cursor/` | Points to authority; does not replace referenced artifacts |
| Plane | Cards, state, scope, acceptance criteria, comments, durable delivery evidence | Workboard and evidence authority |
| GitHub | Pull requests, reviews, checks, CI, merge state, branch history | Repository collaboration authority |
| QA and Reviewer | Verify acceptance criteria with real commands and post evidence on Plane | Studio projections support review; they do not substitute pytest, Doctor, or CI |

Studio Foundation (`studio/`, `studio/engine/schemas/`) remains separate from `app/`.
This card adds documentation only.

## Derived Vs Authoritative Sources

All Studio CLI payloads are derived review aids. Compiler and validator envelopes
use the authority label `derived_non_authoritative`. Prototype projections add
`execution_mode` values such as `non_executing_preview` or
`non_executing_projection`.

### Authoritative

| Domain | Paths or system | Holds |
| --- | --- | --- |
| SDLC process | `.sdlc/`, especially `.sdlc/process/change-lifecycle.md` and `.sdlc/sdlc.yaml` | Lifecycle, gates, workflow data, doctor checks |
| Cursor configuration | `.cursor/` | Agents, skills, rules, commands, hooks |
| Work state and evidence | Plane | Card scope, status, acceptance criteria, durable QA and delivery evidence |
| PR and CI state | GitHub | Reviews, checks, merge, history |
| Referential index | `.sdlc/registry/` | Stable IDs and paths pointing at authoritative artifacts |

### Derived

| Domain | Examples | Holds |
| --- | --- | --- |
| Studio documentation | `studio/*.md`, including this file | Human-facing maps and operating guidance |
| Descriptive schemas | `studio/engine/schemas/` | Non-executable data shapes |
| CLI outputs | Graph IR, Workflow IR, validation results, canvas, assistance, simulation, evidence field projections | Presentation and review data only |

Derived outputs must trace to `source_refs` (repository paths or external
identifiers). They must not become workflow definitions, gate enforcers, local
evidence stores, or replacements for Plane or GitHub state.

## Plane Workflow: Authoritative Delivery Vs Studio Aids

The authoritative delivery path is defined by `.sdlc/process/change-lifecycle.md`
and the SDLC Orchestrator pipeline in `AGENTS.md`. Studio does not replace any
step in that path.

### Authoritative delivery flow

1. Plane child card `INVES-N` is in progress with acceptance criteria on the
   card.
2. `workflow start --card INVES-N` opens the feature branch gate.
3. Implementer, QA, Reviewer, and DevOps agents execute scoped work with real
   tests and commands.
4. Durable evidence is recorded on the Plane card (comments or description
   blocks). Local files such as `specs/`, `studio/generated/`, or ad hoc JSON
   evidence files are prohibited.
5. GitHub holds the PR diff, review threads, and CI results. Merge to
   `develop` follows green CI and Reviewer approval.

Plane remains the workboard and evidence source of truth. GitHub remains the PR
and CI source of truth.

### Studio operating flow (derived aids only)

Studio supports the authoritative flow without executing or mutating it:

1. **Discover** — From the repository root (or `--root`), run the CLI pipeline
   over authoritative sources.
2. **Compile and validate** — Produce derived IR and structural checks for
   review (`compile`, `validate`).
3. **Inspect** — Use `canvas` and `inspect-validation` to understand graph
   shape and validation records.
4. **Advise or preview** — Optionally run `assist-workflow` or
   `preview-simulation` for advisory paths. These do not call agents, Plane,
   GitHub, shell gates, or runtime services.
5. **Draft evidence** — Run `publish-evidence --card INVES-N` to project field
   shapes aligned with `.sdlc/templates/plane/evidence-template.json`. The
   operator copies relevant fields into Plane evidence; the CLI does not post.
6. **Ship source changes** — PRs include documentation, schemas, registry, or
   CLI source edits only. CLI stdout is cited in Plane evidence, not committed
   as generated artifacts.

If Studio `validation_fail` or blocked simulation paths appear, treat them as
review signals. Resolve source issues or document accepted warnings on the
Plane card before claiming QA pass.

## CLI Index

Entry point:

```bash
python -m studio.cli <command> [options]
```

Global options vary by command. Common flags:

- `--format text|json` — stdout format (default `text`).
- `--root PATH` — repository root to inspect (default current directory).

| Command | Purpose | Typical exit code | Module / prototype doc |
| --- | --- | --- | --- |
| `compile` | Derive Graph IR, Workflow IR, and compile report | `0` | `studio/compiler_core.py` |
| `validate` | Run structural Studio validation checks | `1` if any `fail` | `studio/validator_core.py`, `studio/compiler-validator-boundaries.md` |
| `canvas` | Build derived canvas view model with validation legend | `1` if canvas validation `fail` | `studio/canvas_view_model.py`, `studio/visual-orchestration-prototype.md` |
| `inspect-validation` | Filter and group validation records (`--status`, `--check-type`, `--target-type`, `--group-by`) | `1` if any `fail` | `studio/validation_inspection.py` |
| `assist-workflow` | Advisory workflow suggestions (`--kind`) | `1` if `validation_fail` | `studio/workflow_assistance.py`, `studio/ai-workflow-assistance-prototype.md` |
| `preview-simulation` | Non-executing lifecycle scenario preview (`--scenario`, `--intent`, `--path-label`, `--step-kind`, `--tag`) | `1` if `validation_fail` or blocked paths | `studio/simulation_preview.py`, `studio/ai-simulation-preview-prototype.md` |
| `publish-evidence` | Project Plane evidence template fields (`--card`, `--title`, `--branch`) | `1` if `validation_fail` | `studio/publish_evidence.py`, `studio/ai-publish-evidence-prototype.md` |

Recommended pipeline order for a full review pass:

```text
compile → validate → canvas → inspect-validation → publish-evidence
```

Add `assist-workflow` or `preview-simulation` when advisory or scenario context
is needed. All commands write to stdout only and must not persist outputs under
`studio/generated/`, `studio/examples/`, or `specs/`.

## Generated Reports, Previews, And Reviews

| Output kind | How it is produced | How operators use it | Where truth lives |
| --- | --- | --- | --- |
| Compile and validate reports | `compile`, `validate` | Confirm registry and schema references before PR | Authoritative sources under `.sdlc/` and `.cursor/` |
| Canvas and validation inspection | `canvas`, `inspect-validation` | Review graph and check grouping in PR preparation | Validation rules in `studio/docs/contracts/validation-result-ir-contract.md` |
| Workflow assistance | `assist-workflow` | Advisory suggestions with `source_refs`; not agent instructions | `.cursor/agents/` and `.sdlc/process/` |
| Simulation preview | `preview-simulation` | Expected, blocked, and unsupported path labels for training and review | `.sdlc/process/change-lifecycle.md` and live Plane gate state |
| Evidence projection | `publish-evidence` | Draft Plane evidence fields for manual posting | Plane card and `.sdlc/templates/plane/evidence-template.json` |

GitHub PR review expectations for Studio work:

- Separate source edits (docs, schemas, registry, Python CLI modules) from any
  pasted CLI output in the PR description or Plane evidence.
- Reviewers confirm derived outputs are labeled and authorities are unchanged.
- Rollback is a revert PR on the same paths; roll-forward uses a follow-up Plane
  child card (`studio/ai-publish-evidence-prototype.md`).

## Doctor And Studio Validation Evidence

Record validation evidence on the Plane card, not in local files.

| Check | Command | Evidence on Plane |
| --- | --- | --- |
| SDLC structural health | `make sdlc-doctor` | Exit code, FAIL or WARN summary, and fix or accepted-warn rationale |
| Studio structural validation | `python -m studio.cli validate` | Exit code and pass, warn, fail counts from stdout |
| Studio unit tests | `pytest studio/ -q` | Pytest summary and relevant failure excerpts |
| Gate or product tests | Scoped pytest or CI when SDLC or product paths change | Linked CI checks on GitHub plus summary on Plane |
| Evidence field draft | `python -m studio.cli publish-evidence --card INVES-N` | Projected fields copied into the evidence template block |

### Warnings: accept or escalate

- **Studio `warn`:** Fix the underlying source when practical. If accepted,
  document the warning, affected paths, and rationale in Plane evidence.
- **Doctor `WARN`:** Same pattern per `.cursor/rules/040-doctor-gates.mdc` —
  fix or record why the warning is accepted on the Plane card.
- **Studio or Doctor `fail` / non-zero Doctor exit:** Blocking for merge until
  resolved or explicitly escalated to `human_required` through the normal agent
  pipeline.
- **QA failure path:** Documented in simulation scenario `qa_failure`; follow
  AutoFixer cycles and re-post QA evidence on Plane.

## Explicit Exclusions

This operating model does not:

- Replace `docs/roadmap/sdlc-studio-mvp-roadmap.md` or `.sdlc/process/` authority.
- Define an MVP launch checklist beyond pointing to roadmap phase 10.
- Create local tickets, backlog files, `specs/`, or committed evidence JSON.
- Mutate Plane, GitHub, agents, gates, or product code under `app/`.
- Persist CLI output in the repository.

## Related Documents

- `studio/README.md` — Studio Foundation index.
- `studio/source-boundaries.md` — Source boundary map and terminology.
- `studio/foundation-inventory.md` — Foundation inventory baseline.
- `studio/compiler-validator-boundaries.md` — Compiler and validator phase contract.
- `studio/ai-composition-guardrails.md` — Advisory AI composition limits.
- `studio/ai-*-prototype.md` — Per-command prototype notes.
- `.sdlc/templates/plane/evidence-template.json` — Plane evidence field shape.
- `.sdlc/process/change-lifecycle.md` — Authoritative change lifecycle.
