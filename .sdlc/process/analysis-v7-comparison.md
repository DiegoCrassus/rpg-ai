# Analysis A × B — Reconciliation matrix

> Compare: [`analysis-v7-a-manifest-studio.md`](analysis-v7-a-manifest-studio.md) vs [`analysis-v7-b-structure-drift.md`](analysis-v7-b-structure-drift.md)

---

## 1. Agreement (both analyses)

| Topic | Consensus |
|-------|-----------|
| **lifecycle-model.yaml** | Single canonical graph + write_policy |
| **sdlc_obs missing** | P0 — Studio observability broken |
| **Shims** | Must not be hand-edited; generate or delete after consumer migration |
| **gate vs gateways** | **Not** the same — keep both modules, different enforcement |
| **plane-* skills** | Delete duplicates (board-* canonical) |
| **investiments drift** | Fix in change-lifecycle.md |
| **transitions.yaml** | Keep as metadata overlay (skills, preconditions) |
| **Studio compiler** | Must stop treating shims as SoT |

---

## 2. Divergence

| Topic | Analysis A | Analysis B | **Decision** |
|-------|------------|------------|--------------|
| Shim fate | Generate until Studio migrated | Generate + Doctor enforcement | **Generate via `sdlc_sync_model --write`** |
| `gates/` folder | Generate paths only | Eventually merge README into gateways | **Keep folder P1; merge README P3** |
| `pipeline/agents.yaml` | Keep short term | Merge into catalog P2 | **Keep P1; merge P2 epic** |
| Obs location | Manifest declares paths | Restore app/infra package | **Both:** manifest index + sdlc_obs impl |
| Support agents | Not discussed | Demote to skills P2 | **Defer P2** |
| master-workflow slim | P3 | P2 deferred | **P2** |

---

## 3. Conflict resolution rules

1. **Manifest wins** for runtime path declarations (`runtime/manifest.yaml`).
2. **lifecycle-model wins** for graph + write_policy.
3. **gateways/policy.yaml wins** for interaction harness (never merge into write_policy).
4. **Studio reads manifest index first**, then resolves files — never hardcode shim paths in new code.
5. **Generated shims** satisfy Doctor + legacy compiler until Phase 2 removes them from `REQUIRED_SOURCE_PATHS`.

---

## 4. Unified priority stack

| P | Work | Source |
|---|------|--------|
| **P0** | runtime/manifest.yaml + sdlc_obs + Studio compiler→model | A + B |
| **P0** | Fix investiments + delete plane skills | B |
| **P1** | sdlc_sync_model --write + pipeline_metadata + registry | A + B |
| **P1** | catalog reading_order + gateways README clarity | A |
| **P2** | pipeline→catalog; orchestrator hints; learning loop warm | A |
| **P3** | gates README merge; master-workflow slim | B |

---

## 5. Score

| Criterion | A emphasis | B emphasis | Combined |
|-----------|------------|------------|----------|
| Studio alignment | ★★★★★ | ★★★ | ★★★★★ |
| Folder reduction | ★★★ | ★★★★★ | ★★★★ |
| Drift elimination | ★★★★ | ★★★★★ | ★★★★★ |
| Risk control | ★★★★ | ★★★★ | ★★★★ |

**Verdict:** execute **P0+P1** from combined stack in one SDLC_META pass; defer P2/P3 to follow-up cards.
