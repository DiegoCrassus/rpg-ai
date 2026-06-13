# Orchestrator Handoff

## Routing

| Field | Value |
|-------|-------|
| **Next agent** | qa |
| **Stage complete** | no |
| **Previous agent** | implementer |

## Session

| Field | Value |
|-------|-------|
| **Card** | RPG-24 |
| **Epic** | RPG-22 |
| **Branch** | feature/RPG-24-support-agents-skills |
| **Stage** | sdlc_meta |
| **Intent** | SDLC_META |

## Delta

- catalog.yaml: agents.support invocation skill-only + doctor skill/command refs
- policy.yaml: support_agents + support_spawn bypass_handoff_route
- sdlc_pre_gateway.py: support agents skip handoff route match
- roster_sync.py: warn support overlap in pipeline_agents
- AGENTS.md + subagent-delegation: pipeline vs support table
- manifest README: support invocation mapping table
- harness-v7-change-plan.md: P3 complete
- test_support_agents.py added

## Blockers

none

## Next

spawn QA. run pytest .sdlc/dsl/test_support_agents.py + make sdlc-doctor.
