# Manual Test — Workflow Builder (`/builder`)

> **Authority:** [`sdlc-studio-workflow-builder-ux-plan.md`](../roadmap/sdlc-studio-workflow-builder-ux-plan.md) §6  
> **Required for:** QA PASS on any `INVES-WB*` / Workflow Builder card (WB-1 … WB-5).  
> **Automated complement:** Playwright `tests/e2e/studio/builder.spec.ts` (E2E-B1…B6) + `smoke.spec.ts` (3 routes).  
> **Evidence location:** Plane card comment only — **not** in repo files.

---

## Prerequisites

```bash
cd /path/to/sdlc-ai
make studio-dev
```

| Service | URL |
|---------|-----|
| UI | http://127.0.0.1:5174 |
| Builder | http://127.0.0.1:5174/builder |
| API health | http://127.0.0.1:8100/studio/health |

**Browser:** Chromium or Firefox, viewport **1280×720** minimum (DevTools → responsive mode).

**Notas para o operador (PT):** Confirme que o banner *propose-only* aparece no topo. Nenhum passo deste script deve escrever ficheiros no repo — apenas pré-visualização de proposta.

---

## QA rule (blocking)

`pytest`, `curl`, `npm test`, or Playwright **alone** cannot PASS a Workflow Builder card.

Every WB card QA must include:

1. This manual checklist (required steps for that card’s phase) marked PASS/FAIL.
2. Automated gates green on the same commit (`make studio-e2e` when WB-4+ is in scope).

---

## Session record (paste into Plane card comment)

| Field | Value |
|-------|-------|
| Tester | |
| Date | |
| Branch / commit | |
| Card | INVES-___ |
| `make studio-dev` | yes / no |
| Playwright (`make studio-e2e`) | pass / fail / n/a |

### Plane comment template

```markdown
## Manual QA — Workflow Builder

| Step | PASS | Notes |
|------|------|-------|
| M1 | ☐ | |
| … | | |

Tester: ___ · Date: ___ · Commit: ___
Playwright: ___ passed / failed
Verdict: qa_pass / qa_fail
```

---

## Core checklist (WB-1+) — M1–M8

| Step | Operator action | Expected result | PASS |
|------|-----------------|-----------------|------|
| **M1** | Navigate to `/builder`. Wait for `builder-shell` to load. | **10** lifecycle stage nodes on canvas **or** toolbox lists **10** stages (`builder-toolbox-stages`). Propose-only banner visible. | ☐ |
| **M2** | Set viewport to **1280×720**. Scroll toolbox if needed. | Toolbox remains scrollable (≥280px effective width). Canvas and inspector remain usable; layout not crushed. | ☐ |
| **M3** | Pan canvas (drag background). Use **Fit View** and zoom controls if present. | Graph moves; stage nodes remain clickable after pan/zoom. | ☐ |
| **M4** | Connect **Requirements** → **Architecture**: drag bottom handle (source) of Requirements to top handle (target) of Architecture **or** enable **Connect on click**, click Requirements then Architecture. | New transition edge appears. Inspector shows edge fields (`builder-inspector-edge`). | ☐ |
| **M5** | With edge selected: set **Subagent** to `architect`, **Skill** to `architecture-analysis`. Deselect edge, re-select same edge. | Values persist in inspector selects (`builder-inspector-agent`, `builder-inspector-skill`). | ☐ |
| **M6** | Select the edge from M4. Press **Delete** **or** click **Remove transition** in inspector. | Edge removed from canvas. **Create proposal** disabled when zero transition drafts remain. | ☐ |
| **M7** | Restore ≥1 edge (repeat M4 if needed). Click **Create proposal** (`builder-create-proposal`). | Proposal panel shows unified diff (non-empty). **Validate**, **Doctor**, **Gateway check** actions visible. Authority badge `proposed_non_authoritative`. | ☐ |
| **M8** | Hard refresh (**F5**) on `/builder`. | Page reloads without permanent error; canvas and toolbox recover from API. | ☐ |

---

## WB-2 addendum — drag-drop (M9–M10)

Required for cards that ship toolbox drag-drop (INVES-102 / WB-2+).

| Step | Operator action | Expected result | PASS |
|------|-----------------|-----------------|------|
| **M9** | From toolbox, drag **Implementation** (or any stage not yet on canvas) onto empty canvas area (`builder-canvas-drop-target`). | New stage node appears near drop coordinates. | ☐ |
| **M10** | Connect the new node to **Validation** (handles or connect-on-click). | Edge created; inspector opens for the new transition. | ☐ |

---

## WB-3b addendum — multi-type nodes (M-WB3b-1…5)

Required for INVES-104 / WB-3b and later builder cards that include annotation nodes.

| Step | Operator action | Expected result | PASS |
|------|-----------------|-----------------|------|
| **M-WB3b-1** | Ensure at least one transition has a subagent assigned (M5). Observe the edge on canvas. | Edge displays agent badge (`data-testid="agent-badge"`) matching selected subagent. | ☐ |
| **M-WB3b-2** | Enable **Show agent & gate annotations** (`builder-show-annotations`). Attempt to connect two annotation nodes or drag from an annotation handle. | Annotation nodes visible (`agent-annotation-node`, `gate-annotation-node`); **no** connection handles; no new edges from annotations. | ☐ |
| **M-WB3b-3** | Click (a) a **stage** node, (b) a **transition** edge, (c) an **agent** annotation, (d) a **gate** annotation. | Inspector routes per type: `builder-inspector-stage`, `builder-inspector-edge`, `builder-inspector-agent-annotation`, `builder-inspector-gate-annotation`. Gate/agent panels are read-only. | ☐ |
| **M-WB3b-4** | `curl -s http://127.0.0.1:8100/studio/metadata/pipeline \| jq '.gates \| length'` (or browser Network tab). | Response includes non-empty `gates[]` sourced from `.sdlc/gates/paths.yaml` (ids + paths). | ☐ |
| **M-WB3b-5** | With annotations visible, create proposal (M7). Read unified diff preview. | Diff targets transition/workflow paths only; **no** `display.annotation.*` or annotation node ids in export body. | ☐ |

---

## Which steps apply per card

| Card / phase | Required manual steps |
|--------------|----------------------|
| WB-1 (layout, connections) | M1–M8 |
| WB-2 (drag-drop) | M1–M10 |
| WB-3b (multi-type nodes) | M1–M8 + M-WB3b-1…5 |
| WB-4 (Playwright) | Automated E2E-B1…B6; manual optional unless regressions suspected |
| WB-5 (this doc) | Reviewer confirms doc matches live UI |

---

## Playwright cross-reference (automated)

Run: `make studio-e2e` (9 tests total).

| ID | Spec | Covers (partial) |
|----|------|------------------|
| E2E-B1 | `builder.spec.ts` | M1 heading / page shell |
| E2E-B2 | `builder.spec.ts` | M1 stage count |
| E2E-B3 | `builder.spec.ts` | M4 connection |
| E2E-B4 | `builder.spec.ts` | M4–M5 inspector agent select |
| E2E-B5 | `builder.spec.ts` | M6 proposal button state |
| E2E-B6 | `builder.spec.ts` | M7 unified diff |
| Smoke ×3 | `smoke.spec.ts` | Dashboard, workflows, observability routes |

Playwright does **not** replace M-WB3b-1…5 or M9–M10 — run those manually when the card scope includes them.

---

## Failure reporting

For any FAIL, record in Plane:

- Step ID (M#, M-WB3b-#)
- Observed vs expected (one sentence)
- Browser + viewport
- Console errors (if any)
- Optional screenshot or screen recording (attach to Plane — **do not** commit to git)

---

## Sign-off

- [ ] All **required** steps for this card’s phase are PASS
- [ ] `make studio-e2e` green on same commit (when WB-4+ in scope)
- [ ] `make sdlc-doctor` exit 0 (when SDLC paths touched)

**QA:** Do not mark the Plane card PASS without a completed PASS/FAIL table in the card comment.
