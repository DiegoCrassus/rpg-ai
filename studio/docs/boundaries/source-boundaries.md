# Studio Source Boundaries

This document is a derived, non-executable Studio boundary map for `INVES-55`.
It extends `studio/foundation-inventory.md` with stable source-boundary
terminology for future Studio modeling cards. It references source areas by path
or external system name and does not copy authoritative rule bodies, command
bodies, lifecycle text, prompts, hooks, templates, or large source content.

## Source-of-Truth Statement

`.sdlc/` and `.cursor/` are the authoritative repository sources for SDLC
process, workflow, gates, agents, skills, rules, commands, hooks, templates,
automation, and Cursor-specific behavior. `.sdlc/registry/` is a referential
index over those sources; it is not the authority for the behavior it points to.

`studio/` documents and `studio/engine/schemas/` are derived, descriptive, and
non-executable. They can model, summarize, or visualize existing sources, but
they do not define workflows, execute commands, validate gates, drive agents, or
store delivery evidence.

Any Studio visual graph, AI suggestions, and simulations are derived aids,
projections, or previews only. They cannot override `.sdlc/`, `.cursor/`,
Plane, or GitHub source-of-truth artifacts or states.

Plane remains authoritative for work item state, card scope, and durable
delivery evidence. GitHub remains authoritative for pull request state, review,
CI, merge state, and repository history.

## Boundary Map

| Source area | Boundary role | Authority and allowed use | Execution or evidence boundary |
| --- | --- | --- | --- |
| `studio/` | Derived documentation area | May contain human-facing maps, inventories, and explanatory documents over existing SDLC sources. | Must remain non-executable; must not store durable work state, local tickets, backlog, specs, or delivery evidence. |
| `studio/engine/schemas/` | Descriptive schema area | May describe future Studio-readable data shapes for graphs, workflow views, registry entities, and validation results. | Must not become a compiler, validator, runtime contract, command runner, or source of operational truth. |
| `.sdlc/registry/` | Referential index | May point to `.sdlc/` and `.cursor/` artifacts with stable IDs, concise summaries, and relationships. | Does not replace the referenced artifacts and must not be treated as the behavioral authority. |
| `.sdlc/` | Authoritative SDLC source | Defines repository SDLC process, lifecycle, workflows, gates, stage data, scripts, doctor checks, templates, and handoff state. | Execution behavior and gate validation originate here; Studio may reference but not redefine it. |
| `.cursor/` | Authoritative Cursor source | Defines Cursor agents, skills, rules, commands, hooks, and MCP configuration shape for this repository. | Agent behavior and Cursor-specific instructions originate here; Studio may reference but not duplicate them. |
| Plane | External work-state authority | Stores cards, state, scope, acceptance criteria, comments, and durable delivery evidence. | Studio must route durable work state and evidence to Plane instead of local files. |
| GitHub | External PR-state authority | Stores pull requests, reviews, checks, merge state, branch history, and repository collaboration state. | Studio must route PR and CI state to GitHub instead of local derived records. |
| `studio/backend/` | Studio Service API | HTTP control plane wrapping the Foundation engine; reads `.sdlc/` / `.cursor/`; propose-only mutations. | Must not write authoritative repo files or replace Cursor runtime. |
| `studio/frontend/` | Studio Service UI | React SPA for canvas, builders, observability, evidence helpers. | Must not execute shell/git/merge or embed Cursor chat. |
| `app/` | MarketPulse product area | Contains Investment Radar backend/frontend when product work is in scope. | Out of scope for Studio Foundation docs; Studio must not import `marketpulse`. |

## Terminology

- **Authoritative source:** The artifact or external system that defines current
  operational behavior or durable state. For this repository, `.sdlc/`,
  `.cursor/`, Plane, and GitHub hold authority in their respective domains.
- **Referential index:** A lightweight catalog that points to authoritative
  sources by ID, path, summary, and relationship without replacing them.
- **Derived document:** A human-facing Studio document assembled from source
  references for explanation, mapping, or planning.
- **Descriptive schema:** A non-executable schema that describes a possible
  Studio-readable shape without validating, compiling, or running workflows.
- **Source reference:** A real repository path or named external authority used
  to ground a derived Studio model.
- **Boundary map:** A derived document that names source areas, their authority,
  and the limits on how Studio may model or use them.
- **Generated view:** A future Studio-readable representation derived from source
  references. A generated view is presentation data, not a workflow definition or
  evidence store.
- **Validation result:** A recorded outcome of a check, such as path existence,
  YAML parse, policy, lint, doctor, or CI status. Durable delivery evidence must
  live in Plane or GitHub as appropriate.
- **Execution boundary:** The line between describing a workflow and running or
  enforcing it. Studio docs and schemas stay on the descriptive side.
- **Evidence boundary:** The line between explaining expected evidence and
  storing durable evidence. Plane and GitHub store durable evidence; Studio docs
  do not.

## Modeling Rules

Future Studio models must:

- Trace every modeled entity, relationship, view, or validation result to a
  source reference such as a repository path, Plane card, or GitHub pull request.
- Reference authoritative rule bodies, command bodies, lifecycle text, prompts,
  hooks, templates, and source files by path or external identifier instead of
  copying their bodies.
- Remain descriptive and non-executable; Studio models must not become workflow
  definitions, gate implementations, command runners, validators, compilers,
  agent orchestration, or runtime configuration.
- Route durable work state, delivery evidence, review state, CI state, and merge
  state through Plane and GitHub instead of local Studio files.

## Non-Goals

This card does not:

- Change `.sdlc/`, `.cursor/`, `.sdlc/registry/`, `studio/engine/schemas/`, `app/`, or
  `docs/roadmap/`.
- Add runtime, UI, React Flow, TLDraw, compiler, validator, CLI, command runner,
  AI composition, LLM integration, backend, frontend, database, API, scheduler,
  storage, persistence, or distributed execution behavior.
- Create `studio/examples/`, `specs/`, local tickets, local backlog files, or
  local evidence records.
- Redefine Plane as anything other than the work-state and evidence authority.
- Redefine GitHub as anything other than the PR, CI, merge, and repository
  history authority.
