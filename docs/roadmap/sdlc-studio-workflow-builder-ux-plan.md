# Workflow Builder UX — Delivery Plan (with real QA)

> **Status:** Active — manual + E2E gates required for Workflow Builder cards.  
> **Epic:** INVES-100 (Studio Workflow Builder)  
> **Audience:** Planner, Implementer, QA, Reviewer  
> **Language:** English plan; manual script includes Portuguese operator notes.

---

## 1. Phases (summary)

| Phase | Plane | Focus |
|-------|-------|-------|
| WB-1 | INVES-101 | Layout, toolbox, stable connections |
| WB-2 | INVES-102 | Drag-drop stages onto canvas |
| WB-3 / WB-3b | INVES-103 / 104 | Multi-type nodes, inspectors |
| WB-4 | INVES-105 | Playwright `builder.spec.ts` + CI |
| WB-5 | INVES-106 | Manual checklist + operator docs (this plan §6) |

---

## 5. Playwright — automated regression

File: `tests/e2e/studio/builder.spec.ts`

| Test ID | Assertion |
|---------|-----------|
| E2E-B1 | `goto /builder` → heading visible |
| E2E-B2 | Canvas has ≥10 `stage-node` **or** toolbox lists 10 stages |
| E2E-B3 | Drag handle A→B → edge count +1 |
| E2E-B4 | Inspector agent `<select>` after edge select |
| E2E-B5 | Create proposal disabled at 0 drafts; enabled with ≥1 edge |
| E2E-B6 | Proposal panel unified diff non-empty after create |

Plus `smoke.spec.ts` (3 routes). **CI job name:** `Studio E2E (smoke + builder)` — 9 tests via `make studio-e2e`.

---

## 6. Manual test script (mandatory before QA PASS)

**Operator doc (canonical):** [`docs/operations/studio-workflow-builder-manual-test.md`](../operations/studio-workflow-builder-manual-test.md)

Human with `make studio-dev` and browser at http://127.0.0.1:5174/builder.

Record date, branch, PASS/FAIL per step in **Plane card comment** (not repo).

### Core steps M1–M8

| Step | Action | Expected |
|------|--------|----------|
| M1 | Open `/builder` | 10 stages on canvas or toolbox |
| M2 | Viewport 1280×720 | Toolbox scrollable; canvas usable |
| M3 | Pan/zoom | Nodes stay interactive |
| M4 | Connect Requirements → Architecture | New edge; inspector active |
| M5 | Agent architect, skill architecture-analysis | Values persist on re-select |
| M6 | Delete selected edge | Edge removed; export disabled if 0 edges |
| M7 | Create proposal (≥1 edge) | Diff preview; validate/doctor/gateway |
| M8 | Hard refresh | Page recovers |

### WB-2 addendum M9–M10

| Step | Action | Expected |
|------|--------|----------|
| M9 | Drag stage from toolbox to canvas | Node at drop position |
| M10 | Connect new node to another stage | Edge + inspector |

### WB-3b addendum M-WB3b-1…5

| Step | Action | Expected |
|------|--------|----------|
| M-WB3b-1 | Edge with assigned subagent | Agent badge on edge |
| M-WB3b-2 | Toggle annotations; try to connect them | Annotations non-connectable |
| M-WB3b-3 | Select stage / edge / agent / gate | Type-specific inspector |
| M-WB3b-4 | `GET /studio/metadata/pipeline` | `gates[]` from paths.yaml |
| M-WB3b-5 | Create proposal with annotations visible | Export strips annotations |

**QA rule:** `pytest` + `curl` alone **cannot** PASS a WB card. Manual steps above must be ticked for the card’s phase.

---

## 7. Definition of Done (per WB card)

1. Acceptance criteria met in code.
2. `npm run test` + `npm run build` green (frontend).
3. `pytest app/studio-backend/tests/` green if API touched.
4. Playwright green locally when WB-4+ in scope.
5. Human manual script §6 posted on Plane.
6. Reviewer confirms UX ids for that phase.
7. DevOps merge only after CI `studio-e2e` green.

---

## References

- [`docs/studio-service-operator-guide.md`](../studio-service-operator-guide.md)
- [`docs/architecture/studio-service-platform.md`](../architecture/studio-service-platform.md) § S4
- [`.sdlc/workflows/transitions.yaml`](../../.sdlc/workflows/transitions.yaml)
