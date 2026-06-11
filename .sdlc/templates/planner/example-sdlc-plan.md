# Example — Planner Activation via @sdlc-run

> Reference document to validate the planning flow, format, and conventions.
> Language: English. Code: English. Task names follow the `[AI][TYPE] Short title` convention.

---

## 1. User Input in Cursor Chat

```
@sdlc-run

I want to create a REST endpoint on the backend that allows creating
work items in Plane via an internal API. The Cursor agent will call
this endpoint instead of calling the Plane MCP directly — centralizing
task creation logic and enabling automatic enrichment (e.g. adding SDLC
stage labels, setting the correct project, validating stage transitions).
```

---

## 2. Pre-Task Hook — Context Loading

```
[hook: pre-task]
  Reading: .sdlc/sdlc.yaml                → project sdlc-ai, workspace investments-sdlc
  Reading: .sdlc/memory/architecture.md   → Python backend, SQLite local, Supabase prod, framework TBD
  Reading: .sdlc/memory/business-rules.md → 10-stage SDLC, mandatory validation, no fake results
  Stage identified: Requirements (new ticket intake)
  Next stage:       Architecture
  Doctor required after: yes (new structure under app/backend/)
```

---

## 3. Planner Output

---

### Task Name

```
[AI][BACKEND] Internal work item creation endpoint for Plane
```

> **Tag convention:**
> - `[AI]` — created or drafted by a Cursor agent, requires human review before merge
> - `[BACKEND]` — primary area of change; other valid types: `[FRONTEND]` `[INFRA]` `[SHARED]` `[SDLC]` `[DOCS]`

---

### Story

The platform relies on Plane as its project management layer. Right now, every time a Cursor agent needs to create a work item — for a bug, a planned task, or an SDLC gate event — it calls the Plane MCP directly. This works but creates coupling: any agent that creates tasks needs to know Plane's API shape, the correct project ID, the right labels, and the workspace slug.

As the system grows, this becomes fragile. A single misconfigured MCP call creates a task in the wrong project, with the wrong label, or with missing metadata. There's no single place to enforce enrichment rules.

This feature introduces an internal `POST /api/v1/work-items` endpoint in the backend. Agents call this endpoint with a minimal, domain-aware payload (title, description, SDLC stage, priority). The backend handles everything else: maps the SDLC stage to the correct Plane label, sets the right project, validates the input, and returns the Plane work item ID and URL. Enrichment logic lives in one place and can evolve without changing every agent that creates tasks.

---

### Scope

- `POST /api/v1/work-items` endpoint that accepts a domain-level payload
- Maps SDLC stage (`ticket`, `requirements`, `architecture`, etc.) to the corresponding Plane label
- Calls the Plane REST API with the enriched payload
- Returns `{ "id": "...", "url": "...", "identifier": "RPG-N" }` on success
- Logs all Plane API failures with full context (no silent swallowing)

---

### Non-Goals

- No listing, updating, or deleting work items in this scope
- No UI — API only
- Does not replace the Plane MCP in Cursor chat — this is for backend-side automations
- No user authentication on this endpoint yet (future feature)
- No pagination, filtering, or batch creation

---

### Assumptions

| Assumption | Confidence | Impact if wrong |
|------------|-----------|-----------------|
| FastAPI will be the backend framework | medium | blocks Architecture gate — must confirm before implementation |
| `PLANE_API_KEY` will be available as an env var on the server | high | low — already in `.env`, deployment checklist will verify |
| Target Plane project is `investiments` for now | high | low — can be made configurable later |
| No idempotency requirement for this MVP | high | low — accepted risk, documented |
| Pydantic v2 will be used for request/response models | medium | low — consistent with Python stack |

---

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Framework not confirmed (FastAPI is an assumption) | medium | high | Architecture gate is **blocking** until ADR-004 is written and accepted |
| `PLANE_API_KEY` missing in production | low | high | `make sdlc-doctor` + deployment checklist verify env vars before release |
| Plane API rate limit undocumented | low | medium | Implement retry with exponential backoff; log rate limit responses as warnings |
| Duplicate work items created without idempotency | medium | low | Accepted for MVP; registered as known gap — `# TODO(planner): add idempotency key` |
| Stack trace exposure on Plane API failure | medium | medium | Return `503` with a safe message; full error goes to server logs only |

---

### Impacted Areas

```
app/backend/
  src/
    api/
      routes/work_items.py           ← new: POST /api/v1/work-items handler
    services/
      plane_client.py                ← new: HTTP client with retry and logging
    core/
      models/work_item.py            ← new: WorkItemCreate / WorkItemCreated Pydantic models
      stage_label_map.py             ← new: SDLC stage → Plane label mapping
  tests/
    unit/
      test_plane_client.py           ← new: unit tests with mocked Plane API
    integration/
      test_work_items_endpoint.py    ← new: real Plane call, @pytest.mark.integration

docs/architecture/overview.md        ← update: add new backend service description
docs/infrastructure/local-development.md  ← update: backend setup instructions
.sdlc/memory/architecture.md         ← update: confirm framework once ADR-004 accepted
```

---

### Acceptance Criteria

1. `POST /api/v1/work-items` with a valid payload returns `201` with `{ "id", "url", "identifier" }`
2. The created work item is visible in Plane under project `investiments` with the correct SDLC stage label
3. Invalid payload (empty title, unknown stage) returns `422` with a field-level error message — no generic error
4. Missing `PLANE_API_KEY` returns `503 Service Unavailable` with `"Plane integration not configured"` — no stack trace in response body
5. A Plane API failure (timeout, 5xx) returns `502 Bad Gateway` with a safe message and logs the full error server-side
6. At least one unit test per behavior (happy path, validation error, missing config, Plane failure)
7. At least one integration test marked `@pytest.mark.integration` that creates a real work item and verifies the response shape

---

### Definition of Done (DoD)

- [ ] ADR-004 written and accepted (framework confirmed)
- [ ] Endpoint implemented and all unit tests pass locally (`python -m pytest app/backend/tests/unit/ -v`)
- [ ] Integration test passes against real Plane (`@pytest.mark.integration`)
- [ ] `make sdlc-doctor` exits `0` after structural changes
- [ ] `docs/architecture/overview.md` updated with new backend service
- [ ] `docs/infrastructure/local-development.md` updated with backend setup
- [ ] `.sdlc/memory/architecture.md` updated with confirmed framework
- [ ] No secrets in code or diff
- [ ] PR reviewed and approved (human or Reviewer agent)
- [ ] Handoff summary written in `docs/handoff/current-state.md`

---

### Task Breakdown

```
[ ] RPG-N · [AI][SDLC]    Confirm backend framework — write ADR-004
[ ] RPG-N · [AI][BACKEND] Create app/backend/ structure and update pyproject.toml
[ ] RPG-N · [AI][BACKEND] Implement PlaneClient (HTTP wrapper with retry + logging)
[ ] RPG-N · [AI][BACKEND] Implement WorkItemCreate / WorkItemCreated Pydantic models
[ ] RPG-N · [AI][BACKEND] Implement POST /api/v1/work-items handler
[ ] RPG-N · [AI][BACKEND] Write unit tests (mocked PlaneClient)
[ ] RPG-N · [AI][BACKEND] Write integration test (@pytest.mark.integration)
[ ] RPG-N · [AI][DOCS]    Update architecture/overview.md and local-development.md
[ ] RPG-N · [AI][SDLC]    Run make sdlc-doctor — confirm exit 0
```

---

### Next Step

**Architect** must:

1. Confirm FastAPI vs alternatives → write `ADR-004` in `docs/architecture/decisions.md`
2. Define module structure under `app/backend/src/`
3. Define full request/response contract (field names, types, validation rules)
4. List new dependencies for `pyproject.toml` — expected: `fastapi`, `httpx`, `pydantic>=2`

> Rule: no code before the Architecture gate passes. The ADR is the gate.

---

## 4. Post-Task Hook — Planner Summary

```
[hook: post-task]
  Files changed: .sdlc/templates/planner/example-sdlc-plan.md (this document)
  Docs to update after implementation:
    - docs/architecture/overview.md
    - docs/infrastructure/local-development.md
    - .sdlc/memory/architecture.md
  Doctor required after: yes (new app/backend/ structure)
  Open risks:
    - Framework unconfirmed → Architecture gate is blocking
    - Idempotency deferred → accepted, documented in code as TODO
  Next agent: Architect
```

---

## 5. Format Reference

| Element | Why it matters |
|---------|----------------|
| `[AI]` tag | Signals agent-created content — human must review before merge |
| `[BACKEND/FRONTEND/INFRA/...]` tag | Makes scope visible at a glance in Plane and PR titles |
| Story section | Provides the "why" — without it, agents (and humans) optimize for the wrong thing |
| Non-goals | Close scope explicitly; prevent the Implementer from building beyond the plan |
| Assumptions with confidence | `medium` = Architecture gate is blocking; `high` = can proceed |
| Measurable acceptance criteria | Each criterion has an HTTP code or verifiable behavior — never "it should work" |
| Definition of Done | Checklist the Reviewer uses; PR cannot merge until all items are checked |
| Risks with real mitigations | Not just listed — each has an action or an accepted reason |
| Blocking Architecture gate | No code until the Architect confirms the framework (ADR) |
| Task breakdown with tags | Each sub-task in Plane follows the same `[AI][TYPE]` convention |
