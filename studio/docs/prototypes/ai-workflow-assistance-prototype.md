# AI Workflow Assistance Prototype

Deterministic advisory projection for `INVES-69` (roadmap phase 7). Simulates output shape/heuristics for future LLM assistance; no LLM, agents, or mutations. Guardrails: `studio/ai-composition-guardrails.md`. Canvas: `studio/visual-orchestration-prototype.md`. Roadmap: `docs/roadmap/sdlc-studio-mvp-roadmap.md`.

Pipeline: compile → validate → canvas → validation_inspection → workflow_assistance. CLI: `python -m studio.cli assist-workflow [--format text|json] [--root PATH] [--kind KIND]`.

Output: `assistance` (`derived_non_authoritative`, `derived_inputs_only`), `summary`, `explanations`, advisory `suggestions`, optional `annotations`; all cite `source_refs` only. Non-goals: LLM/MCP/shell, persistence, Plane/GitHub mutation, QA/gate claims. Implementation: `studio/workflow_assistance.py`.
