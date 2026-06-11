"""Read-only pipeline and lifecycle metadata for Studio authoring UIs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from studio.engine.compiler_core import CompilerInputError, compile_studio_sources
from studio_service.api.errors import StudioApiError


def build_pipeline_metadata(root: Path) -> dict[str, Any]:
    """Agents, skills, and lifecycle stages for dropdowns and asset palette."""

    lifecycle_path = root / ".sdlc" / "stages" / "lifecycle.yaml"
    pipeline_path = root / ".sdlc" / "pipeline" / "agents.yaml"
    gates_path = root / ".sdlc" / "gates" / "paths.yaml"

    stages = _load_lifecycle_stages(lifecycle_path)
    agents = _load_pipeline_agents(pipeline_path)
    gates = _load_gate_paths(gates_path, stages)

    skills: list[dict[str, str]] = []
    seen: set[str] = set()
    for agent in agents:
        skill = agent.get("skill") or {}
        skill_id = str(skill.get("id", ""))
        if skill_id and skill_id not in seen:
            seen.add(skill_id)
            skills.append({"id": skill_id, "name": str(skill.get("name", skill_id))})

    try:
        compiled = compile_studio_sources(root)
        workflow = (compiled.workflow_ir or {}).get("workflow") or {}
        transition_count = len(workflow.get("transitions") or [])
    except CompilerInputError as exc:
        raise StudioApiError(
            422,
            "COMPILER_INPUT_ERROR",
            "Required compiler inputs are missing or unreadable",
            details={"missing_paths": exc.missing_paths},
        ) from exc

    return {
        "stages": stages,
        "agents": agents,
        "skills": sorted(skills, key=lambda item: item["id"]),
        "gates": gates,
        "summary": {
            "stage_count": len(stages),
            "agent_count": len(agents),
            "skill_count": len(skills),
            "gate_count": len(gates),
            "transition_count": transition_count,
        },
        "source_refs": [
            ".sdlc/stages/lifecycle.yaml",
            ".sdlc/pipeline/agents.yaml",
            ".sdlc/gates/paths.yaml",
            ".sdlc/workflows/transitions.yaml",
        ],
    }


def _load_lifecycle_stages(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    stages = []
    for item in data.get("stages") or []:
        if not isinstance(item, dict):
            continue
        stage_id = str(item.get("id", ""))
        stages.append(
            {
                "id": stage_id,
                "name": str(item.get("name", stage_id)),
                "order": item.get("order"),
                "description": str(item.get("description", "")),
            }
        )
    return sorted(stages, key=lambda s: (s.get("order") is None, s.get("order", 999), s["id"]))


def _load_pipeline_agents(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    agents = []
    for item in data.get("pipeline") or []:
        if not isinstance(item, dict):
            continue
        agent_id = str(item.get("id", ""))
        skill = item.get("skill") or {}
        agents.append(
            {
                "id": agent_id,
                "name": str(item.get("name", agent_id)),
                "stages": list(item.get("stages") or []),
                "cursor_agent": str(item.get("cursor_agent", "")),
                "skill": {
                    "id": str(skill.get("id", "")),
                    "name": str(skill.get("name", "")),
                },
            }
        )
    return agents


def _load_gate_paths(
    path: Path,
    stages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Read-only gate path badges from paths.yaml for builder annotations."""

    if not path.is_file():
        return []

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    gate_paths = data.get("gate_paths") or {}
    stage_names = {str(item.get("id", "")): str(item.get("name", "")) for item in stages}
    gates: list[dict[str, Any]] = []

    for stage_id, config in (gate_paths.get("stages") or {}).items():
        if not isinstance(config, dict):
            continue
        allowed = [str(prefix) for prefix in (config.get("allowed_prefixes") or [])]
        gates.append(
            {
                "id": str(stage_id),
                "name": stage_names.get(str(stage_id), str(stage_id)),
                "stage": str(stage_id),
                "allowed_prefixes": allowed,
                "source_ref": ".sdlc/gates/paths.yaml",
            }
        )

    return sorted(gates, key=lambda item: item["stage"])
