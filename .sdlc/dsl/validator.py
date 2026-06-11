"""Schema-level consistency validation for SDLC configuration."""


from .models import SDLCConfig

# (level, message)
Finding = tuple[str, str]


def validate(config: SDLCConfig) -> list[Finding]:
    """Run all consistency checks. Returns list of (level, message) findings."""
    findings: list[Finding] = []

    lifecycle_ids = {s.id for s in config.lifecycle_stages}
    stage_def_ids = {s.id for s in config.stage_definitions}
    agent_ids = {a.id for a in config.agents}
    skill_ids = {s.id for s in config.skills}

    # Lifecycle vs stage definitions parity
    for lid in lifecycle_ids:
        if lid not in stage_def_ids:
            findings.append(
                ("WARN", f"Lifecycle stage '{lid}' has no entry in stages.yaml")
            )
    for sid in stage_def_ids:
        if sid not in lifecycle_ids:
            findings.append(
                ("WARN", f"Stage definition '{sid}' not found in lifecycle.yaml")
            )

    # Workflow references
    for wf in config.workflows:
        if wf.from_stage not in lifecycle_ids:
            findings.append(
                (
                    "FAIL",
                    f"Workflow '{wf.id}' references unknown from_stage '{wf.from_stage}'",
                )
            )
        if wf.to_stage not in lifecycle_ids:
            findings.append(
                (
                    "FAIL",
                    f"Workflow '{wf.id}' references unknown to_stage '{wf.to_stage}'",
                )
            )
        if wf.agent and wf.agent not in agent_ids:
            findings.append(
                (
                    "FAIL",
                    f"Workflow '{wf.id}' references unknown agent '{wf.agent}'",
                )
            )
        if wf.skill and wf.skill not in skill_ids:
            findings.append(
                (
                    "FAIL",
                    f"Workflow '{wf.id}' references unknown skill '{wf.skill}'",
                )
            )

    # Agent stage references
    for agent in config.agents:
        for stage in agent.stages:
            if stage not in lifecycle_ids:
                findings.append(
                    (
                        "FAIL",
                        f"Agent '{agent.id}' references unknown stage '{stage}'",
                    )
                )
        if agent.primary_skill and agent.primary_skill not in skill_ids:
            findings.append(
                (
                    "FAIL",
                    f"Agent '{agent.id}' references unknown skill '{agent.primary_skill}'",
                )
            )

    # Skill stage references
    for skill in config.skills:
        for stage in skill.stages:
            if stage not in lifecycle_ids:
                findings.append(
                    (
                        "WARN",
                        f"Skill '{skill.id}' references unknown stage '{stage}'",
                    )
                )

    # Rule severity values
    valid_severities = {"required", "warning"}
    for rule in config.rules:
        if rule.severity not in valid_severities:
            findings.append(
                (
                    "FAIL",
                    f"Rule '{rule.id}' has invalid severity '{rule.severity}' (expected: required|warning)",
                )
            )

    # Integration status values
    valid_statuses = {"placeholder", "not_configured", "active", "deprecated"}
    for integration in config.integrations:
        if integration.status not in valid_statuses:
            findings.append(
                (
                    "WARN",
                    f"Integration '{integration.id}' has unknown status '{integration.status}'",
                )
            )

    _validate_lifecycle_model(findings, lifecycle_ids)

    return findings


def _validate_lifecycle_model(findings: list[Finding], lifecycle_ids: set[str]) -> None:
    try:
        from pathlib import Path

        from .gate import repo_root
        from .lifecycle_model import gate_stage_aliases, load_model, load_write_policy
    except ImportError:
        return

    root = repo_root()
    model = load_model(root)
    if not model:
        findings.append(("WARN", "lifecycle-model.yaml missing — using gates/paths.yaml only"))
        return

    model_ids = {str(s.get("id")) for s in (model.get("stages") or []) if s.get("id")}
    for lid in lifecycle_ids:
        if lid not in model_ids:
            findings.append(
                (
                    "FAIL",
                    f"Loaded lifecycle stage '{lid}' not in lifecycle-model.yaml",
                )
            )
    if lifecycle_ids != model_ids and lifecycle_ids and model_ids:
        findings.append(
            (
                "FAIL",
                "Lifecycle stage set must match lifecycle-model.yaml exactly",
            )
        )

    try:
        from pathlib import Path

        from .lifecycle_shard_drift import check_lifecycle_shard_drift

        for level, message in check_lifecycle_shard_drift(Path(root)):
            if level in ("FAIL", "WARN"):
                findings.append((level, message))
    except ImportError:
        pass

    aliases = gate_stage_aliases(root)
    policy = load_write_policy(root)
    for gate_key in (policy.get("stages") or {}):
        mapped = aliases.get(gate_key, [gate_key])
        for sid in mapped:
            if sid not in model_ids:
                findings.append(
                    (
                        "FAIL",
                        f"write_policy gate key '{gate_key}' maps to unknown stage '{sid}'",
                    )
                )

    for tr in model.get("transitions") or []:
        for field in ("from_stage", "to_stage"):
            val = tr.get(field)
            if val and val not in model_ids:
                findings.append(
                    (
                        "FAIL",
                        f"transition '{tr.get('id')}' references unknown {field} '{val}'",
                    )
                )
