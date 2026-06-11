# Command: SDLC Run

## Purpose

Run the normal SDLC orchestration loop for the user's current request. This command does not implement inline; it points the Orchestrator back to the authoritative pipeline.

## Procedure

1. Read `AGENTS.md`.
2. Read `.sdlc/process/master-workflow.md` and `.sdlc/process/change-lifecycle.md`.
3. Check `python3 .sdlc/dsl/cli.py workflow status`.
4. If a gate is open, continue from `.sdlc/memory/orchestrator-handoff.md`.
5. If there is no open gate, start with `Task(Intent Analyst)`.
6. Delegate each stage using `.cursor/skills/subagent-delegation/SKILL.md`.
7. Use Plane for cards/evidence and `workflow start|finish` for gate state.

## Do Not

- Implement product code directly.
- Create local tickets or specs.
- Skip Planner, Architect, QA, Reviewer, or DevOps for product work.
