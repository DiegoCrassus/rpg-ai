"""YAML loader — index at .sdlc/sdlc.yaml, modules under .sdlc/<module>/."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is not installed. Run: pip install PyYAML", file=sys.stderr)
    sys.exit(1)

from .models import (
    Agent,
    Integration,
    LifecycleStage,
    Rule,
    SDLCConfig,
    Skill,
    StageDefinition,
    Workflow,
)

SDLC_MANIFEST = "sdlc.yaml"
_cache: dict[str, dict[str, Any]] = {}

try:
    from . import core_config
except ImportError:
    core_config = None  # type: ignore[assignment]


class LoadError(Exception):
    pass


def _sdlc_dir(root: str) -> Path:
    return Path(root) / ".sdlc"


def _sdlc_path(root: str) -> str:
    return str(_sdlc_dir(root) / SDLC_MANIFEST)


def _load_yaml(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise LoadError(f"File not found: {path}")
    try:
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            raise LoadError(f"Empty YAML file: {path}")
        if not isinstance(data, dict):
            raise LoadError(f"Expected YAML mapping in {path}")
        return data
    except yaml.YAMLError as e:
        raise LoadError(f"YAML parse error in {path}: {e}") from e


def _merge_modules(root: str, index: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(index)
    modules = (index.get("contract") or {}).get("modules") or {}
    sdlc_dir = _sdlc_dir(root)

    for _mod_name, mod_cfg in modules.items():
        data_rel = mod_cfg.get("data")
        if not data_rel:
            continue
        data_paths = data_rel if isinstance(data_rel, list) else [data_rel]
        for rel_path in data_paths:
            if not isinstance(rel_path, str):
                continue
            chunk_path = sdlc_dir / rel_path
            if not chunk_path.is_file() or chunk_path.suffix not in {".yaml", ".yml"}:
                continue
            chunk = _load_yaml(str(chunk_path))
            for key, value in chunk.items():
                merged[key] = value

    return merged


def load_merged_manifest(root: str) -> dict[str, Any]:
    if root in _cache:
        return _cache[root]
    index = _load_yaml(_sdlc_path(root))
    merged = _merge_modules(root, index)
    _cache[root] = merged
    return merged


def load_lifecycle(root: str) -> list[LifecycleStage]:
    from .lifecycle_model import load_model

    model = load_model(Path(root))
    raw = model.get("stages") or []
    if not raw:
        raise LoadError(
            "lifecycle-model.yaml must define stages (legacy lifecycle.yaml is deprecated)"
        )
    stages = []
    for s in raw:
        stages.append(
            LifecycleStage(
                id=s["id"],
                name=s["name"],
                order=s["order"],
                description=s.get("description", s.get("name", s["id"])),
            )
        )
    return stages


def load_stages(root: str) -> list[StageDefinition]:
    data = _load_yaml(os.path.join(root, ".sdlc", "stages", "definitions.yaml"))
    defs = []
    for s in data.get("stages", []):
        defs.append(
            StageDefinition(
                id=s["id"],
                name=s["name"],
                objective=s.get("objective", s["name"]),
                inputs=s.get("inputs", []),
                outputs=s.get("outputs", []),
                required_evidence=s.get("required_evidence", []),
                gates=s.get("gates", []),
            )
        )
    return defs


def load_workflows(root: str) -> list[Workflow]:
    from .lifecycle_model import load_model, transition_overlay

    model = load_model(Path(root))
    transitions = model.get("transitions") or []
    if not transitions:
        raise LoadError("lifecycle-model.yaml must define transitions")
    overlay = transition_overlay(Path(root))
    workflows = []
    for tr in transitions:
        tid = tr["id"]
        extra = overlay.get(tid, {})
        name = extra.get("name") or tr.get("name") or tid.replace("_", " → ")
        workflows.append(
            Workflow(
                id=tid,
                name=name,
                from_stage=tr["from_stage"],
                to_stage=tr["to_stage"],
                description=extra.get("description", tr.get("description", "")),
                agent=extra.get("agent") or tr.get("agent"),
                skill=extra.get("skill") or tr.get("skill"),
                preconditions=extra.get("preconditions", tr.get("preconditions", [])),
                outputs=extra.get("outputs", tr.get("outputs", [])),
            )
        )
    return workflows


def _load_stage_bindings(root: str) -> list[dict[str, Any]]:
    catalog_path = os.path.join(root, ".sdlc", "manifest", "catalog.yaml")
    if os.path.isfile(catalog_path):
        catalog = _load_yaml(catalog_path)
        bindings = catalog.get("stage_bindings")
        if bindings:
            return bindings
    pipeline = _load_yaml(os.path.join(root, ".sdlc", "pipeline", "agents.yaml"))
    return pipeline.get("pipeline", [])


def load_agents(root: str) -> list[Agent]:
    agents = []
    for a in _load_stage_bindings(root):
        skill = a.get("skill") or {}
        agents.append(
            Agent(
                id=a["id"],
                name=a["name"],
                stages=a.get("stages", []),
                description=a.get("skill", {}).get("description", a["name"]),
                primary_skill=skill.get("id"),
            )
        )
    return agents


def load_skills(root: str) -> list[Skill]:
    skills: list[Skill] = []
    for a in _load_stage_bindings(root):
        sk = a.get("skill")
        if not sk:
            continue
        skills.append(
            Skill(
                id=sk["id"],
                name=sk["name"],
                stages=a.get("stages", []),
                description=sk.get("description", ""),
                expected_outputs=sk.get("expected_outputs", []),
            )
        )
    catalog_path = os.path.join(root, ".sdlc", "manifest", "catalog.yaml")
    if os.path.isfile(catalog_path):
        cat = _load_yaml(catalog_path)
        for s in (cat.get("skills") or []):
            if any(x.id == s["id"] for x in skills):
                continue
            skills.append(
                Skill(
                    id=s["id"],
                    name=s["id"],
                    stages=[],
                    description=s.get("when", ""),
                    expected_outputs=[],
                )
            )
    return skills


def load_rules(root: str) -> list[Rule]:
    data = _load_yaml(os.path.join(root, ".sdlc", "rules", "governance.yaml"))
    rules = []
    for r in data.get("rules", []):
        rules.append(
            Rule(
                id=r["id"],
                name=r["name"],
                severity=r["severity"],
                description=r.get("description", ""),
                enforced_at=r.get("enforced_at", []),
            )
        )
    return rules


def load_integrations(root: str) -> list[Integration]:
    data = _load_yaml(os.path.join(root, ".sdlc", "integrations", "services.yaml"))
    integrations = []
    env_logical = {}
    if core_config:
        env_logical = core_config.env_map(root)

    for i in data.get("integrations", []):
        logical = i.get("env_logical")
        config_env = i.get("config_env")
        if logical and env_logical.get(logical):
            config_env = env_logical[logical]
        integrations.append(
            Integration(
                id=i["id"],
                name=i["name"],
                status=i.get("status", "placeholder"),
                description=i.get("description", ""),
                config_env=config_env,
                capabilities=i.get("capabilities", []),
                notes=i.get("notes"),
            )
        )
    return integrations


def load_sdlc_config(root: str) -> SDLCConfig:
    main = _load_yaml(_sdlc_path(root))
    return SDLCConfig(
        version=main.get("version", main.get("contract", {}).get("version", "unknown")),
        name=main.get("name", "unknown"),
        description=main.get("description", ""),
        lifecycle_stages=load_lifecycle(root),
        stage_definitions=load_stages(root),
        workflows=load_workflows(root),
        agents=load_agents(root),
        skills=load_skills(root),
        rules=load_rules(root),
        integrations=load_integrations(root),
    )
