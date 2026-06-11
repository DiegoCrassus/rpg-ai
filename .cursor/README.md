# .cursor — Cursor Agent Configuration

This directory contains all Cursor-specific configuration for the `sdlc-ai` project.

## Structure

| Directory     | Purpose                                                         |
|---------------|-----------------------------------------------------------------|
| `rules/`      | Persistent rules applied to every agent interaction             |
| `commands/`   | Reusable command instructions for SDLC operations               |
| `skills/`     | Specialized skill procedures for each SDLC activity             |
| `agents/`     | Specialized agent roles with defined responsibilities           |
| `hooks/`      | Executable pre/post gateways, write gates, and observability adapters |
| `hooks.json`  | Cursor hook wiring for gate, gateway, and observability events |

## Rules

| File                         | Applied When                             |
|------------------------------|------------------------------------------|
| `orchestrator.mdc`           | Always                                   |
| `sdlc-core.mdc`              | Always                                   |
| `020-code-quality.mdc`       | During implementation and review         |
| `030-docs-and-handoff.mdc`   | When docs or interfaces change           |
| `040-doctor-gates.mdc`       | After structural changes                 |

## Commands

Use these commands by referencing them in Cursor:

| Command            | Purpose                                        |
|--------------------|------------------------------------------------|
| `sdlc-run`         | Run the orchestrated SDLC pipeline             |
| `sdlc-doctor`      | Validate repository structure                  |
| `sdlc-review`      | Review a PR or diff                            |

## Hooks

| Event | Hook | Purpose |
|-------|------|---------|
| `preToolUse` | `sdlc_gate_hook.py` | Denies **protected** writes (`app/`, `pyproject.toml`) when gate closed; unprotected paths always pass |
| `beforeShellExecution`, `subagentStart` | `sdlc_pre_gateway.py` | Blocks unsafe shell patterns; enforces handoff subagent route only when `core.gates.enforcement: strict` |
| `subagentStop` | `sdlc_post_gateway.py` | Validates handoff and returns to the previous step if evidence is incomplete |
| `sessionStart`, `stop` | `sdlc_obs_session.py` | Emits observability run metrics |

## Quick Reference

```bash
# Validate the repository
make sdlc-doctor

# Run the normal SDLC loop
# Use: @sdlc-run in Cursor chat
```
