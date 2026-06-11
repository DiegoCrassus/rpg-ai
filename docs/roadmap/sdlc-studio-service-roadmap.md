# SDLC Studio Service — Roadmap & Architecture

> **Status:** Active planning (post-foundation).  
> **Supersedes naming:** This roadmap continues the work started in [`sdlc-studio-mvp-roadmap.md`](sdlc-studio-mvp-roadmap.md) but **must not be called “MVP”** in titles or Plane epics. Use **Studio Foundation** (delivered) and **Studio Service** (next).  
> **Related:** [`sdlc-enforcement-roadmap.md`](sdlc-enforcement-roadmap.md) (hooks/gateways), [`studio/studio-operating-model.md`](../../studio/studio-operating-model.md) (current CLI boundaries).

---

## 1. Naming & positioning

| Term | Meaning |
|------|---------|
| **Studio Foundation** | Delivered engine in `studio/` + CLI (`INVES-53`, phases 1–10). Deterministic, in-memory, non-UI. |
| **Studio Service** | Next product: **backend + frontend** that exposes Foundation capabilities and SDLC authoring/observability over the **whole repo** (`.sdlc/`, `.cursor/`, registry, hooks, gateways, Plane, GitHub). |
| **Not “MVP”** | Foundation was a minimum *engine* loop for agents. Service is the *usable product* (dashboard, canvas, builders, live runs). |

**North star:** A local (later deployable) **SDLC control plane** — visual, simple, n8n-like for workflows — that **integrates** what already exists and **creates** new agents, rules, commands, and workflow definitions **through gated change**, with **live observability** during runs.

**Chat:** Primary agent chat stays **Cursor**. Studio does not replace it; it may deep-link (“open in Cursor”) and show run context beside IDE work.

---

## 2. What exists today (reuse, do not rewrite)

### 2.1 Studio Foundation (`studio/`)

| Capability | Module / CLI | Service role |
|------------|--------------|--------------|
| Compile Graph/Workflow IR | `compiler_core`, `compile` | API: `POST /studio/compile` |
| Structural validation | `validator_core`, `validate` | API: `POST /studio/validate` |
| Canvas view-model | `canvas_view_model`, `canvas` | API: `GET /studio/canvas` → React Flow |
| Validation inspection | `validation_inspection`, `inspect-validation` | Validation Center UI |
| Workflow assistance (advisory) | `workflow_assistance`, `assist-workflow` | Assistance panel |
| Simulation preview | `simulation_preview`, `preview-simulation` | Simulation UI |
| Evidence projection | `publish_evidence`, `publish-evidence` | Evidence draft → Plane |
| Readiness loop | `mvp_readiness`, `check-readiness` | Dashboard health widget |
| Test traceability skeleton | `mvp_test_skeleton`, `list-skeleton` | QA planning view |

Contracts and boundaries: `studio/schemas/`, `studio/*-contract.md`, `studio/studio-operating-model.md`.

### 2.2 SDLC authority (operate on, not replace)

| Area | Path | Studio Service interaction |
|------|------|----------------------------|
| Process & lifecycle | `.sdlc/process/`, `.sdlc/stages/`, `.sdlc/workflows/` | Read + **propose** edits (patch preview) |
| Gates & session | `.sdlc/gates/`, `.sdlc/memory/session-gate.json` | Read live gate; show in dashboard |
| Gateways | `.sdlc/gateways/policy.yaml`, `.cursor/hooks/sdlc_*_gateway.py` | Stream deny/allow events to Observability |
| Agents & pipeline | `.cursor/agents/`, `.sdlc/pipeline/` | Subagent builder + roster |
| Rules, skills, commands | `.cursor/rules/`, `.cursor/skills/`, `.cursor/commands/` | Browse + template-based create |
| Registry | `.sdlc/registry/` | Registry explorer graph |
| Doctor / DSL | `.sdlc/dsl/`, `make sdlc-doctor` | Trigger from UI; show results |
| Workboard | Plane (MCP) | Cards, states, evidence (read; post via approved flows) |
| Delivery | GitHub | PR/CI status panels |
| Hooks config | `.cursor/hooks.json` | Observability wiring |

### 2.3 Observability (already started)

`app/infra/sdlc_obs/` — SQLite metrics, `pre_task` / `post_task`, HTTP dashboard on port 7700.

**Service integration:** Studio Observability screen **embeds or supersedes** the sdlc_obs dashboard and **correlates** gateway events + handoff + Plane card + branch.

### 2.4 Enforcement alignment

[`sdlc-enforcement-roadmap.md`](sdlc-enforcement-roadmap.md) hardens fail-closed hooks and CI truth. Studio Service **surfaces** enforcement (blocked writes, gateway messages) and must **not** bypass it. Authoring flows go through the same gates as Orchestrator-led changes.

---

## 3. Target architecture

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  Studio Web UI (app/studio-frontend/)                                     │
│  • Dashboard  • Workflow canvas (React Flow)  • Builders  • Observability │
│  • Registry   • Validation  • Evidence  • Settings                        │
│  Chat: remains in Cursor IDE (link-out only)                              │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ REST + WebSocket (SSE)
┌───────────────────────────────▼──────────────────────────────────────────┐
│  Studio API (app/studio-backend/)                                         │
│  • Wraps `studio/` Python package (no duplicate compiler logic)         │
│  • Repo scanner: .sdlc/, .cursor/, registry                               │
│  • Mutation service: patch proposals → user confirm → git/Plane workflow  │
│  • Event bus: gateway hooks, sdlc_obs, session-gate, orchestrator-handoff │
│  • Integrations: Plane MCP proxy, GitHub API (read-only first)            │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
  studio/ (engine)        .sdlc/ + .cursor/      app/infra/sdlc_obs/
  authoritative IR      authoritative config   run metrics DB
```

### 3.1 Layer responsibilities

| Layer | Owns | Must not |
|-------|------|----------|
| **Studio Engine** (`studio/`) | Derive IR, validate, projections | Persist UI state as authority; call agents |
| **Studio API** | HTTP/WS, auth (local), orchestration of engine + file reads | Copy rule bodies into DB as SoT |
| **Studio UI** | Layout, React Flow, forms, live timelines | Execute shell/git merge without gates |
| **Cursor** | Agent chat, Task(), MCP in IDE | — |
| **Plane / GitHub** | Workboard, evidence, PR/CI | — |

### 3.2 Mutation model (authoring)

All visual edits follow **propose → review → apply**:

1. User edits block diagram or form in UI.
2. API generates a **patch preview** (YAML/Markdown diff) against `.sdlc/` or `.cursor/`.
3. UI shows Doctor/validate impact + gateway policy check (dry-run).
4. Apply only when: open Plane child card, `workflow start`, branch, commit (same as today).
5. Studio never silently writes authoritative files.

### 3.3 Data classes

| Class | Examples | UI treatment |
|-------|----------|--------------|
| **Authoritative** | `change-lifecycle.md`, `agents/*.md`, `rules/*.mdc` | Edit via patch only; badge “source of truth” |
| **Derived** | Canvas JSON, simulation, assistance | Badge `derived_non_authoritative`; regenerate button |
| **Operational** | `session-gate.json`, handoff, obs events | Live; read-mostly |
| **External** | Plane card, GitHub PR | Linked panels |

---

## 4. Information architecture — screens

### 4.1 Global shell

- **Top bar:** repo name, active Plane card (if gate open), branch, Doctor status chip, link “Open in Cursor”.
- **Hamburger sidebar (primary nav):**
  - Home (Dashboard)
  - Workflows
  - Workflow Builder
  - Agents & Subagents
  - Rules & Skills
  - Commands
  - Registry
  - Validation
  - Simulation
  - Assistance
  - Observability
  - Evidence & Delivery
  - Settings
- **Main canvas:** route content.
- **Optional right drawer:** context for selected node (source refs, validation records, `source_path` links).

### 4.2 Screen catalog

#### A. Dashboard (home)

**Purpose:** Single glance at SDLC health and activity.

| Zone | Content | Data source |
|------|---------|-------------|
| Summary cards | Workflows count, stages, open validations, `mvp_ready` | `check-readiness`, compile/validate |
| Workflow strip | Mini React Flow or stage pills for default pipeline | `canvas` (collapsed) |
| Active work | Gate open: card, branch, stage, `Next agent` from handoff | `session-gate.json`, handoff |
| Enforcement | Recent gateway deny/allow (last 24h) | gateway hook stream + `sdlc_obs` |
| Plane snapshot | Epic/child counts by state (Studio epic, enforcement epic) | Plane MCP |
| GitHub snapshot | Open PRs, last CI on `develop` | GitHub API |
| Recent runs | Timeline from Observability | `sdlc_obs` + hook events |

**Non-goals on this screen:** Start agents, merge PRs, or replace Cursor chat.

#### B. Workflows (read-first canvas)

- Full **React Flow** graph from `canvas` API (nodes/edges/overlays).
- Filters: section, validation status, entity type.
- Click node → source refs (`.sdlc/…`, `.cursor/…`) in drawer; open file path (local).
- Toggle: validation overlay legend (pass/warn/fail).
- **Default mode: read-only.** “Propose change” opens Builder with selection context.

#### C. Workflow Builder (n8n-like)

- **Palette blocks:** Stage, Gate, Transition, Handoff, Agent assignment, Validation checkpoint.
- **Canvas:** drag-connect blocks; map to Workflow IR / `transitions.yaml` structure.
- **Properties panel:** id, `agent_ref`, conditions, `next_agent`, lifecycle_source.
- **Actions:** Validate (engine), Preview simulation (selected scenario), Export patch.
- **Guardrails:** banner — visual graph is not authoritative until patch merged.

Inspired by n8n: triggers = lifecycle entry; nodes = stages; edges = transitions; sticky notes = advisory only.

#### D. Agents & Subagents

- Tree/list from `.cursor/agents/` + `.sdlc/pipeline/` roster.
- Card per agent: role, tools, forbidden actions, handoff expectations.
- **Create flow:** template wizard → preview `.cursor/agents/<name>.md` → patch proposal.
- Link agents to workflow stages (derived map from IR).

#### E. Rules, Skills, Commands

- Tabbed browser: Rules | Skills | Commands.
- Search by name/path; show scope (globs), related modules.
- **Create:** pick template (rule/skill/command) → fill metadata → patch preview.
- Run scoped Doctor checks after proposal.

#### F. Registry Explorer

- Graph of registry entities (`index.yaml`, relationships).
- Highlight broken refs (validator output).
- Drill-down to authoritative file without copying content.

#### G. Validation Center

- Table from `inspect-validation` (groupable).
- Run `validate` / `make sdlc-doctor` from UI (API subprocess).
- Link failures to nodes on Workflow canvas.

#### H. Simulation

- Scenario picker (`docs_only`, `qa_failure`, …).
- Step timeline with `expected` / `blocked` / `unsupported` chips.
- Side-by-side: lifecycle_source links.

#### I. Assistance (advisory)

- Suggestions from `assist-workflow` with `source_refs`.
- Explicit “advisory only — not agent instructions”.
- No auto-apply to repo.

#### J. Observability (live run)

**Purpose:** Follow an execution end-to-end.

| Stream | Source |
|--------|--------|
| Run span | `sdlc_obs` pre_task/post_task |
| Gateway | `subagentStart`, `subagentStop`, shell deny from `.cursor/hooks` |
| Gate | write gate allow/deny |
| Handoff | `orchestrator-handoff.md` updates |
| Plane/GitHub | card state, PR checks (polling) |

**UI:** Gantt-style or vertical timeline; filter by card/run_id/agent.

**Cursor chat:** not embedded; show “Continue in Cursor” with session id / card ref.

#### K. Evidence & Delivery

- Form populated from `publish-evidence` projection.
- Copy-to-clipboard for Plane comment; link to evidence template doc.
- PR panel: status, checks, link to finish-change skill path.

#### L. Settings

- Repository root (`--root`).
- Plane workspace/project (from env).
- sdlc_obs DB path; gateway log level.
- Feature flags (read-only mode, break-glass warning).

---

## 5. Technology choices (recommended)

| Concern | Choice | Rationale |
|---------|--------|-----------|
| API | FastAPI (Python) | Reuse `studio/` package; same runtime as Doctor/DSL |
| Realtime | SSE or WebSocket | Gateway/obs event stream |
| UI | React + Vite in `app/studio-frontend/` | Align with `app/frontend/` patterns; isolate from MarketPulse |
| Canvas | React Flow | Already named in Foundation research |
| Styling | Tailwind (match existing frontend) | Consistency |
| obs storage | Extend `sdlc_obs` SQLite schema | Avoid second metrics DB |
| Deployment (later) | Docker compose: API + UI + optional obs | Local-first |

**Explicit:** No TLDraw for core orchestration (annotations optional later).

---

## 6. Phased delivery (Plane-ready)

Each phase should become an **epic child** under a new Plane epic  
`[AI][EPIC] Build SDLC Studio Service` (not “MVP”).

### Phase S0 — Foundation complete ✅

**Delivered:** `studio/` engine, CLI, contracts, INVES-54–75.  
**Exit:** `check-readiness` pass on `develop`.

### Phase S1 — Service shell & read-only dashboard

| Deliverable | Notes |
|-------------|-------|
| `app/studio-backend/` scaffold | Health, `GET /studio/readiness`, wrap compile/validate/canvas |
| `app/studio-frontend/` scaffold | Shell: top bar + hamburger + routing |
| Dashboard (read-only) | Summary widgets, no mutation |
| Dev script | `make studio-dev` → API + UI |

**Exit:** User opens browser, sees live readiness + canvas summary for repo.

### Phase S2 — Workflow canvas (React Flow)

| Deliverable | Notes |
|-------------|-------|
| Full graph viewer | Nodes/edges/overlays from API |
| Node inspector drawer | source_refs, validation |
| Filters & search | |

**Exit:** Human navigates SDLC graph without CLI.

### Phase S3 — Observability integration

| Deliverable | Notes |
|-------------|-------|
| Unify `sdlc_obs` + gateway events | Single timeline API |
| Observability screen | Live + historical runs |
| Correlation | run_id ↔ card ↔ branch ↔ handoff |

**Exit:** User traces one INVES-N delivery through hooks and gateways in UI.

### Phase S4 — Builders (propose-only)

| Deliverable | Notes |
|-------------|-------|
| Workflow Builder | Patch to `.sdlc/workflows/` / transitions |
| Agent builder | `.cursor/agents/` templates |
| Rules/Skills/Commands wizards | Patch preview |
| Validate + Doctor on proposal | |

**Exit:** User creates draft agent + workflow patch; applies via normal git/Plane flow.

### Phase S5 — Registry & validation UX

| Deliverable | Notes |
|-------------|-------|
| Registry explorer | |
| Validation Center | |
| Simulation + Assistance panels | |

**Exit:** Full Foundation CLI surface available in UI.

### Phase S6 — Delivery integrations

| Deliverable | Notes |
|-------------|-------|
| Plane panel (read + evidence post helper) | Respect 403 lessons; MCP proxy |
| GitHub PR/CI panel | |
| Evidence screen | |

**Exit:** Operator completes review loop without switching tools except Cursor chat.

### Phase S7 — Hardening & service posture

| Deliverable | Notes |
|-------------|-------|
| Auth (local token) | |
| Enforcement roadmap alignment | fail-closed visible in UI |
| E2E tests | Playwright + API tests |
| Runbook | `docs/` operator guide |

**Exit:** Team treats Studio Service as default SDLC console alongside Cursor.

---

## 7. Consolidated validation gates (Service)

| Gate | Command / check |
|------|-----------------|
| Engine regression | `pytest studio/ -q` |
| API contract | OpenAPI + integration tests |
| UI smoke | Critical routes render |
| Doctor | `make sdlc-doctor` after `.sdlc`/`.cursor` mutations |
| Enforcement | Gateway tests green; Studio mutations respect write gate |
| No authority leak | Derived views labeled; Plane/GitHub remain SoT for work/evidence |

---

## 8. Risks & non-goals

### Risks

| Risk | Mitigation |
|------|------------|
| UI mistaken for source of truth | Persistent banners; read-only default; patch-only writes |
| Duplicating Cursor agent runtime | Chat stays in Cursor; Studio triggers Plane/git only |
| Split brain vs `sdlc_obs` | Merge into one observability API |
| `app/` collision with MarketPulse | Separate `app/studio-*` packages |
| Scope explosion | Phase boundaries; one Plane child per phase capability |

### Non-goals (Service v1)

- Distributed multi-tenant SaaS
- Replacing Plane or GitHub
- Autonomous agent execution inside Studio UI
- Running `pytest`/`merge` without SDLC gates
- Local `specs/` or evidence JSON in repo

---

## 9. Mapping from old “MVP” phases

| Old MVP phase (doc) | Service phase |
|---------------------|---------------|
| 1–5 Foundation/engine | **S0** ✅ |
| 6 Visual orchestration | **S2** canvas + **S4** builder |
| 7 AI composition | **S5** Assistance panel (advisory) |
| 8 Simulation | **S5** Simulation UI |
| 9 Publish/operate | **S6** Evidence & Delivery |
| 10 MVP readiness | **S1** dashboard + ongoing gates |

---

## 10. Next planning actions

1. Create Plane epic **`[AI][EPIC] Build SDLC Studio Service`** with children aligned to S1–S7 (no “MVP” in titles).
2. Architect card for **S1**: API boundaries, `app/studio-*` layout, event schema for observability.
3. Keep [`sdlc-studio-mvp-roadmap.md`](sdlc-studio-mvp-roadmap.md) as historical Foundation reference; link here for all new work.
4. Cross-link [`sdlc-enforcement-roadmap.md`](sdlc-enforcement-roadmap.md) — Studio Observability screen is the operator face of enforcement.

---

*English repository artifact. Plane cards and user chat may use Portuguese.*
