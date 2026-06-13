#!/usr/bin/env python3
"""Sync lifecycle shims from lifecycle-model.yaml (check or write)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def _yaml_dump(data: dict[str, Any]) -> str:
    import yaml  # noqa: PLC0415

    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def _load_definitions_objectives(root: Path) -> dict[str, str]:
    import yaml  # noqa: PLC0415

    path = root / ".sdlc" / "stages" / "definitions.yaml"
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: dict[str, str] = {}
    for stage in data.get("stages") or []:
        if not isinstance(stage, dict):
            continue
        sid = str(stage.get("id") or "")
        objective = str(stage.get("objective") or stage.get("description") or "")
        if sid and objective:
            out[sid] = objective
    return out


def build_lifecycle_shim(model: dict[str, Any], root: Path) -> dict[str, Any]:
    objectives = _load_definitions_objectives(root)
    stages = []
    for stage in model.get("stages") or []:
        if not isinstance(stage, dict):
            continue
        sid = str(stage.get("id") or "")
        stages.append(
            {
                "id": sid,
                "name": stage.get("name", sid),
                "order": stage.get("order"),
                "description": objectives.get(sid, ""),
            }
        )
    return {
        "stages": stages,
    }


def build_paths_shim(model: dict[str, Any]) -> dict[str, Any]:
    policy = model.get("write_policy") or {}
    return {"gate_paths": policy}


def write_shims(root: Path) -> tuple[Path, Path]:
    sys.path.insert(0, str(root / ".sdlc" / "dsl"))
    from lifecycle_model import load_model  # noqa: E402

    model = load_model(root)
    if not model:
        raise RuntimeError("lifecycle-model.yaml missing or empty")

    lifecycle_path = root / ".sdlc" / "stages" / "lifecycle.yaml"
    paths_path = root / ".sdlc" / "gates" / "paths.yaml"

    lifecycle_payload = build_lifecycle_shim(model, root)
    lifecycle_payload["stages"] = lifecycle_payload["stages"]  # noqa: B018
    lifecycle_text = (
        "# AUTO-GENERATED from .sdlc/process/lifecycle-model.yaml — do not edit\n"
        + _yaml_dump({"stages": lifecycle_payload["stages"]})
    )
    paths_text = (
        "# AUTO-GENERATED from lifecycle-model write_policy — do not edit\n"
        + _yaml_dump(build_paths_shim(model))
    )

    lifecycle_path.write_text(lifecycle_text, encoding="utf-8")
    paths_path.write_text(paths_text, encoding="utf-8")
    return lifecycle_path, paths_path


def check_shims(root: Path) -> int:
    sys.path.insert(0, str(root / ".sdlc" / "dsl"))
    import yaml  # noqa: E402
    from lifecycle_model import load_model, load_write_policy, model_path  # noqa: E402

    model = load_model(root)
    if not model:
        print("FAIL: lifecycle-model.yaml missing or empty", file=sys.stderr)
        return 1

    expected_paths = build_paths_shim(model)
    expected_lifecycle = build_lifecycle_shim(model, root)

    legacy_path = root / ".sdlc" / "gates" / "paths.yaml"
    lifecycle_path = root / ".sdlc" / "stages" / "lifecycle.yaml"

    ok = True
    if legacy_path.is_file():
        data = yaml.safe_load(legacy_path.read_text(encoding="utf-8")) or {}
        if data.get("gate_paths") != expected_paths.get("gate_paths"):
            print("WARN: gates/paths.yaml drift from lifecycle-model write_policy", file=sys.stderr)
            ok = False
    else:
        print("WARN: gates/paths.yaml missing", file=sys.stderr)
        ok = False

    if lifecycle_path.is_file():
        data = yaml.safe_load(lifecycle_path.read_text(encoding="utf-8")) or {}
        actual_ids = [s.get("id") for s in data.get("stages") or []]
        expected_ids = [s.get("id") for s in expected_lifecycle.get("stages") or []]
        if actual_ids != expected_ids:
            print("WARN: stages/lifecycle.yaml stage order drift", file=sys.stderr)
            ok = False
    else:
        print("WARN: stages/lifecycle.yaml missing", file=sys.stderr)
        ok = False

    if ok:
        print(f"OK: shims aligned with {model_path(root)}")
        return 0

    print("Run: python .sdlc/scripts/sdlc_sync_model.py --write", file=sys.stderr)
    return 0 if load_write_policy(root) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync lifecycle shims from lifecycle-model.yaml")
    parser.add_argument("--write", action="store_true", help="Regenerate gates/paths.yaml and stages/lifecycle.yaml")
    args = parser.parse_args()

    if args.write:
        try:
            lifecycle_path, paths_path = write_shims(ROOT)
        except RuntimeError as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {lifecycle_path.relative_to(ROOT)}")
        print(f"Wrote {paths_path.relative_to(ROOT)}")
        return 0

    return check_shims(ROOT)


if __name__ == "__main__":
    sys.exit(main())
