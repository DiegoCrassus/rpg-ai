# Analysis B — Structure audit, drift & folder reduction

> **Lens:** filesystem topology, duplicate rosters, Doctor-enforced bloat, L1 doc drift.
> **Date:** 2026-06-13 · **Method:** inventory + dependency graph + delete/generate matrix

---

## 1. Inventory (`.sdlc/` modules)

| Folder | Files (approx) | Function | Verdict |
|--------|----------------|----------|---------|
| `process/` | 7 | L1 prose + **lifecycle-model.yaml** (SoT) | **Keep** — slim master-workflow later |
| `manifest/` | 3 | catalog + executions.jsonl | **Keep** — add runtime cross-ref |
| `learning/` | 8 | L3 loop | **Keep** — fold into runtime index |
| `optimization/` | 3 | procedures + proposals stub | **Keep** — delete analyzer wrapper |
| `dsl/` | 28 | gate, workflow, doctor, tests | **Keep** — core kernel |
| `scripts/` | 20+ | Plane, workflow helpers | **Trim** plane aliases in Makefile |
| `gates/` | 2 | write_policy **shim** | **Generate** — not hand-edit |
| `gateways/` | 2 | interaction harness | **Keep** — distinct from write gate |
| `stages/` | 3 | lifecycle shim + definitions | **Split** — definitions keep; lifecycle generate |
| `workflows/` | 2 | transition metadata overlay | **Keep** |
| `pipeline/` | 2 | stage→agent+skill | **Merge into catalog** (phase 2) |
| `workboard/` | 2 | Plane granularity | **Keep** |
| `rules/` | 2 | governance prose YAML | **Keep** |
| `integrations/` | 2 | vendor services | **Keep** — fix investiments refs |
| `registry/` | 4 | Studio graph index | **Update** — lifecycle-model as SoT node |
| `doctor/` | 2 | checks.yaml | **Update** — require lifecycle-model, shims generated |
| `templates/` | 6 | handoff, plane, planner | **Keep** |
| `memory/` | 10+ | runtime session state | **Keep** — ephemeral only |

**Total `.sdlc/`:** ~121 files → target **~95** after shim generation + skill cleanup.

---

## 2. gate/ vs gateways/ — deep comparison

### 2.1 Not redundant (different enforcement planes)

```text
User/agent action
    │
    ├─ Shell command ──► gateways/policy.yaml ──► pre_gateway (deny rm -rf, specs/)
    │
    ├─ Subagent spawn ──► gateways/policy.yaml ──► agent_order + handoff sections
    │
    └─ Write tool ──► lifecycle-model write_policy ──► gate.py + sdlc_gate_hook
```

| Concern | Module | Enforced by | Fail mode |
|---------|--------|-------------|-----------|
| Path ACL | write_policy (was `gates/`) | gate hook | closed gate / wrong stage |
| Command safety | `gateways/policy.yaml` | pre_gateway | deny destructive shell |
| Handoff contract | `gateways/policy.yaml` | post_gateway | reroute previous agent |
| Studio proposals | `gateways/policy.yaml` → `studio_proposals` | mutation service | dry-run only |

### 2.2 Apparent redundancy (fixable)

| Duplicate | Copies | Resolution |
|-----------|--------|------------|
| `write_policy` | lifecycle-model + gates/paths.yaml | Generate shim; gate.py already prefers model |
| Stage ids | lifecycle-model + stages/lifecycle.yaml | Generate shim |
| Transition edges | lifecycle-model + transitions.yaml graph | Model = graph; transitions.yaml = overlay only |
| Agent roster | catalog.yaml + pipeline/agents.yaml + gateways agent_order | Phase 2: catalog SoT; generate agent_order slice |
| Plane skills | board-* + plane-* (4 files) | **Delete plane-*** |

---

## 3. Drift hotspots (P0 doc)

| File | Drift | Fix |
|------|-------|-----|
| `change-lifecycle.md` | `investiments` ×3 | → `RPG` project |
| `manifest/README.md` | `INVES` prefix | → `RPG` |
| `catalog.yaml` | workspace `RPG-AI` vs sdlc.yaml `rpg` | Align to sdlc.yaml |
| `harness-v6-plan.md` | DoD unchecked | Mark PR #8 done |
| `operational-context.md` | sdlc_obs "implemented" | True after this epic |
| Studio docs | INVES-* card examples | Low priority |

---

## 4. Folders questioned by operator

| Folder | Needed? | Reason |
|--------|---------|--------|
| `gates/` | **View only** | README + generated paths.yaml |
| `gateways/` | **Yes** | Interaction harness — not replaceable by write_policy |
| `stages/` | **Partial** | definitions.yaml = rich evidence; lifecycle.yaml = generated |
| `workflows/` | **Yes** | Skill/precondition overlay for Studio IR |
| `pipeline/` | **Transitional** | Duplicate of catalog stage bindings |
| `rules/` | **Yes** | governance.yaml — prose rules index |
| `registry/` | **Yes** | Studio compiler graph — update refs |
| `optimization/` | **Yes** | observe mode procedures |
| `integrations/` | **Yes** | MCP/service map |

---

## 5. `.cursor/` reduction

| Item | Count | Action |
|------|-------|--------|
| Pipeline agents | 8 | Keep |
| Support agents | 8 | Phase 2 → invoke via skills only |
| Skills | 24+ | Delete 4 plane/github duplicates |
| Rules | 7 | Keep 060-communication |
| Flat skills (*.md) | 10+ | Consolidate or mark legacy |

---

## 6. Doctor as bloat enforcer

`checks.yaml` **requires** shim files → prevents deletion. Fix:

1. Add `process/lifecycle-model.yaml` to required files
2. Mark shims as generated (Doctor runs `sdlc_sync_model --check` not file presence alone)
3. Remove `gates/` from required **directories** after README merge into gateways

---

## 7. Delete / generate matrix

| Action | Item | Savings |
|--------|------|---------|
| **DELETE** | `.cursor/skills/plane-*`, `github-sdlc` | 4 skills |
| **DELETE** | `scripts/optimization/analyzer.py` | 1 file |
| **GENERATE** | `gates/paths.yaml`, `stages/lifecycle.yaml` | 0 manual edits |
| **SLIM** | `master-workflow.md` 338→80 lines | deferred P2 |
| **MERGE** | `pipeline/agents.yaml` → catalog | deferred P2 |
| **ADD** | `.sdlc/runtime/manifest.yaml` | +1 index, −N doc duplicates |

---

## 8. Phase plan (Analysis B)

1. **P0** — Fix L1 investiments drift; delete plane skills; implement sdlc_obs
2. **P1** — `sdlc_sync_model --write`; Doctor check update; registry SoT refs
3. **P2** — pipeline→catalog merge; support agents→skills
4. **P3** — Optional: remove `gates/` folder (README section in gateways)

---

## 9. Metrics

| Metric | Before | Target |
|--------|--------|--------|
| Lifecycle SoT files | 4 YAML | 1 canonical + 2 generated + 1 overlay |
| Obs store implementations | 0 working | 1 SQLite + 2 JSONL |
| Duplicate skills | 4 plane/github | 0 |
| L1 project name variants | 3 (`investiments`, `RPG`, `rpg`) | 1 (`RPG`) |
