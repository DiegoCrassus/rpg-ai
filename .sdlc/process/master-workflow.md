# Master Workflow — SDLC AI-Native (L1 Index)

> **Status:** APPROVED — slim index (Harness v7 P2)  
> **Authority:** complements [`change-lifecycle.md`](change-lifecycle.md); prevails over ad hoc chat instructions

---

## Documentation layers

| Layer | File | Audience | Content |
|-------|------|----------|---------|
| L0 — Entry | `AGENTS.md` (root) | Agent (alwaysApply) | One-page decision tree + entry commands |
| L1 — Index | `.sdlc/README.md` + `.sdlc/manifest/catalog.yaml` | Agent + human | Modular SDLC map, agents, skills, MCP catalog |
| L1 — Process | `.sdlc/process/master-workflow.md` | Agent + human | This document — pipeline index |
| L2 — Machine | `.sdlc/sdlc.yaml` + module YAMLs under `.sdlc/<module>/` | Scripts/hooks/CLI | States, gates, paths, transitions |
| L2 — Canonical model | `.sdlc/process/lifecycle-model.yaml` | Gate, validate, Doctor | Single stage graph + write_policy + operational_map |

Operational steps map to lifecycle stages in [`lifecycle-model.yaml`](lifecycle-model.yaml) → `operational_map`. Legacy `gates/paths.yaml` and `workflows/transitions.yaml` are generated shims during migration.

---

## Agreed principles

1. **Always automatic** — any message goes through Orchestrator first.
2. **Autonomy ≠ bypass** — full pipeline within scope; zero gate skips.
3. **Zero human clicks** — autonomous merge (green CI + Reviewer APPROVE).
4. **Human escalation** — AutoFixer max 2 cycles → stop and ask human.
5. **Dual state** — Plane = source of truth; `session-gate.json` = hook cache.
6. **Plan artifacts** — Plane HTML only; local `specs/` forbidden.
7. **Self-management** — structural gap → auto-create `SDLC_META` card.

---

## Step 0 — Entry (every session)

```
User message → Orchestrator → Task(Intent Analyst) [unless gate open + continuation]
→ handoff (.sdlc/memory/orchestrator-handoff.md) + session-gate.json (+ Plane if product)
```

| User input | Behavior |
|------------|----------|
| "no interruptions", "urgent" | Full pipeline; autonomous decisions; no human questions |
| Out-of-scope | Record in handoff; do not expand scope |
| Unrecoverable blocker | AutoFixer → report → stop and ask human |

Full decision tree: [`AGENTS.md`](../../AGENTS.md).

---

## Pipeline overview

Orchestrator coordinates via `Task()` — never edits `app/`, never commits, never runs lint/test.  
Skill: [`.cursor/skills/subagent-delegation/SKILL.md`](../../.cursor/skills/subagent-delegation/SKILL.md)

```
Task(Intent Analyst) → Task(Planner) → workflow discover → Task(Architect)
→ FOR EACH child card: workflow start → Task(Implementer) → Task(QA)
  → Task(AutoFixer)×2 if fail → Task(Reviewer) → Task(DevOps) → workflow finish
→ epic Done when all children Done
```

| Concern | Authority |
|---------|-----------|
| Gitflow, branch, PR, merge | [`change-lifecycle.md`](change-lifecycle.md) |
| Stage graph, transitions, write policy | [`lifecycle-model.yaml`](lifecycle-model.yaml) |
| Agent procedures per stage | [`.cursor/agents/*.md`](../../.cursor/agents/) |
| Stage → agent → skill bindings | [`catalog.yaml`](../manifest/catalog.yaml) → `stage_bindings` |
| Epics vs child cards | [`granularity.yaml`](../workboard/granularity.yaml) |

**Operational map (canonical):** `operational_map` in [`lifecycle-model.yaml`](lifecycle-model.yaml).

---

## Mechanical gate

| File | Function |
|------|----------|
| `lifecycle-model.yaml` → `write_policy` | Canonical write ACL |
| `.sdlc/gates/paths.yaml` | Generated shim (gate hook) |
| `.sdlc/memory/session-gate.json` | Session cache |
| `.cursor/hooks/sdlc_gate_hook.py` | Pre-write enforcement |

Open gate: `python .sdlc/dsl/cli.py workflow start --card RPG-N` (child card only, never epic).

---

## CLI (meta-tool)

```bash
python .sdlc/dsl/cli.py workflow classify | plan | discover | start | status | finish
make sdlc-doctor   # after structural changes
```

Full command list: [`AGENTS.md`](../../AGENTS.md) · [`change-lifecycle.md`](change-lifecycle.md).

---

## Communication

Inter-agent: **caveman mode** — see [`communication-policy.md`](communication-policy.md).  
User chat: Portuguese prose per workspace rules.

---

## References

- **Gitflow / Plane / merge authority:** [`change-lifecycle.md`](change-lifecycle.md)
- **Lifecycle SoT:** [`lifecycle-model.yaml`](lifecycle-model.yaml)
- **Communication law:** [`communication-policy.md`](communication-policy.md)
- **Harness migration plan:** [`harness-v7-change-plan.md`](harness-v7-change-plan.md)
- **Module map:** [`.sdlc/README.md`](../README.md)
