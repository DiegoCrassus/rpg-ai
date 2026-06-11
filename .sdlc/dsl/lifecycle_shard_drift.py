"""FAIL when legacy lifecycle shards diverge from lifecycle-model.yaml."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

Finding = tuple[str, str]


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    if yaml is None or not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data if isinstance(data, dict) else {}


def check_lifecycle_shard_drift(root: Path) -> list[Finding]:
    """Compare stages/lifecycle.yaml and workflows/transitions.yaml to the canonical model."""
    from lifecycle_model import load_model  # noqa: PLC0415

    findings: list[Finding] = []
    model = load_model(root)
    if not model:
        findings.append(("FAIL", "lifecycle-model.yaml missing or empty"))
        return findings

    model_stages = model.get("stages") or []
    model_ids = [str(s.get("id")) for s in model_stages if s.get("id")]
    model_id_set = set(model_ids)

    shard_path = root / ".sdlc" / "stages" / "lifecycle.yaml"
    shard = _load_yaml_mapping(shard_path)
    shard_stages = shard.get("stages") or []
    shard_ids = [str(s.get("id")) for s in shard_stages if s.get("id")]

    if shard_ids != model_ids:
        findings.append(
            (
                "FAIL",
                "lifecycle.yaml stage ids/order diverge from lifecycle-model.yaml "
                f"(shard={shard_ids}, model={model_ids})",
            )
        )
    else:
        findings.append(("PASS", "lifecycle.yaml stage ids match lifecycle-model.yaml"))

    model_trans = {
        str(t.get("id")): (str(t.get("from_stage")), str(t.get("to_stage")))
        for t in (model.get("transitions") or [])
        if t.get("id")
    }

    trans_path = root / ".sdlc" / "workflows" / "transitions.yaml"
    trans = _load_yaml_mapping(trans_path)
    for wf in trans.get("workflows") or []:
        wid = str(wf.get("id") or "")
        if not wid:
            continue
        from_s = str(wf.get("from_stage") or "")
        to_s = str(wf.get("to_stage") or "")
        if wid not in model_trans:
            findings.append(
                (
                    "FAIL",
                    f"transitions.yaml workflow '{wid}' not in lifecycle-model transitions",
                )
            )
            continue
        exp_from, exp_to = model_trans[wid]
        if (from_s, to_s) != (exp_from, exp_to):
            findings.append(
                (
                    "FAIL",
                    f"transitions.yaml '{wid}' edge ({from_s}->{to_s}) "
                    f"!= model ({exp_from}->{exp_to})",
                )
            )

    for wid in model_trans:
        if wid not in {str(w.get("id")) for w in trans.get("workflows") or []}:
            findings.append(
                (
                    "WARN",
                    f"lifecycle-model transition '{wid}' missing from transitions.yaml shim",
                )
            )

    for wf in trans.get("workflows") or []:
        from_s = str(wf.get("from_stage") or "")
        to_s = str(wf.get("to_stage") or "")
        if from_s and from_s not in model_id_set:
            findings.append(("FAIL", f"transitions.yaml references unknown from_stage '{from_s}'"))
        if to_s and to_s not in model_id_set:
            findings.append(("FAIL", f"transitions.yaml references unknown to_stage '{to_s}'"))

    if not any(f[0] == "FAIL" for f in findings if "transitions" in f[1] or "lifecycle.yaml" in f[1]):
        if model_trans:
            findings.append(("PASS", "transitions.yaml edges align with lifecycle-model.yaml"))

    return findings


def check_committed_plane_evidence(root: Path) -> Finding:
    """Committed per-card board evidence JSON must not live under templates/plane/."""
    import re
    import subprocess

    sys.path.insert(0, str(root / ".sdlc" / "dsl"))
    from core_config import card_prefix  # noqa: E402

    prefix = card_prefix(root)
    proc = subprocess.run(
        ["git", "ls-files", "--", ".sdlc/templates/plane/"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return ("WARN", "git ls-files unavailable — skipped committed evidence check")

    pattern = re.compile(rf"^evidence-{re.escape(prefix)}-\d+\.json$", re.I)
    bad = [line.strip() for line in proc.stdout.splitlines() if pattern.search(Path(line).name)]
    if bad:
        return (
            "FAIL",
            "Committed board evidence templates forbidden (use .sdlc/memory/ ephemeral only): "
            + ", ".join(bad[:5])
            + ("..." if len(bad) > 5 else ""),
        )
    return ("PASS", f"No committed evidence-{prefix}-*.json under templates/plane/")
