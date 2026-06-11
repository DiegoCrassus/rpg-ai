"""Repository-level Doctor checks driven by .sdlc/doctor/checks.yaml."""

from __future__ import annotations

import os
import subprocess
import sys

try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is not installed. Run: pip install PyYAML", file=sys.stderr)
    sys.exit(1)

Finding = tuple[str, str]

DOCTOR_CHECKS = ".sdlc/doctor/checks.yaml"


def _load_doctor_checks(root: str) -> dict[str, Any]:
    path = os.path.join(root, DOCTOR_CHECKS)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Doctor config missing: {DOCTOR_CHECKS}")
    with open(path, encoding="utf-8") as fh:
        config = yaml.safe_load(fh) or {}
    return config.get("checks", config.get("doctor", {}).get("checks", config))


def _check_dir(root: str, rel_path: str) -> Finding:
    if os.path.isdir(os.path.join(root, rel_path)):
        return ("PASS", f"Required directory exists: {rel_path}")
    return ("FAIL", f"Missing directory: {rel_path}")


def _check_file(root: str, rel_path: str) -> Finding:
    if os.path.isfile(os.path.join(root, rel_path)):
        return ("PASS", f"Required file exists: {rel_path}")
    return ("FAIL", f"Missing file: {rel_path}")


def _check_absent(root: str, rel_path: str) -> Finding:
    if not os.path.exists(os.path.join(root, rel_path)):
        return ("PASS", f"Legacy path absent: {rel_path}")
    return ("FAIL", f"Legacy path must not exist in v5 layout: {rel_path}")


def _check_file_nonempty(root: str, rel_path: str) -> Finding:
    full = os.path.join(root, rel_path)
    if not os.path.isfile(full):
        return ("FAIL", f"Missing file: {rel_path}")
    if os.path.getsize(full) == 0:
        return ("FAIL", f"Empty file: {rel_path}")
    return ("PASS", f"Doc file non-empty: {rel_path}")


def _check_yaml(root: str, rel_path: str) -> Finding:
    full = os.path.join(root, rel_path)
    if not os.path.isfile(full):
        return ("FAIL", f"YAML file missing: {rel_path}")
    try:
        with open(full, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if data is None:
            return ("FAIL", f"YAML file is empty: {rel_path}")
        return ("PASS", f"YAML valid: {rel_path}")
    except yaml.YAMLError as exc:
        return ("FAIL", f"YAML parse error in {rel_path}: {exc}")


def _check_file_contains(root: str, rel_path: str, marker: str) -> Finding:
    full = os.path.join(root, rel_path)
    if not os.path.isfile(full):
        return ("FAIL", f"Missing file for marker check: {rel_path}")
    with open(full, encoding="utf-8") as fh:
        content = fh.read()
    if marker in content:
        return ("PASS", f"Required marker found in {rel_path}: {marker}")
    return ("FAIL", f"Missing required marker in {rel_path}: {marker}")


def _check_file_not_contains(root: str, rel_path: str, marker: str) -> Finding:
    full = os.path.join(root, rel_path)
    if not os.path.isfile(full):
        return ("PASS", f"File absent for forbidden marker check: {rel_path}")
    with open(full, encoding="utf-8") as fh:
        content = fh.read()
    if marker not in content:
        return ("PASS", f"Forbidden marker absent in {rel_path}: {marker}")
    return ("FAIL", f"Forbidden marker found in {rel_path}: {marker}")


def _check_makefile_target(root: str, target: str) -> Finding:
    makefile = os.path.join(root, "Makefile")
    if not os.path.isfile(makefile):
        return ("FAIL", f"Makefile missing — cannot check target: {target}")
    with open(makefile, encoding="utf-8") as fh:
        content = fh.read()
    if f"{target}:" in content:
        return ("PASS", f"Makefile target exists: {target}")
    return ("FAIL", f"Missing Makefile target: {target}")


def _check_integration_env(role: str, env_var: str) -> Finding:
    if os.environ.get(env_var):
        return ("PASS", f"Integration configured: {role} ({env_var})")
    return ("WARN", f"Integration not configured: {role} ({env_var} not set)")


def _check_studio_import(root: str, module: str) -> Finding:
    """Import studio_service without starting Uvicorn (validates PYTHONPATH layout)."""
    backend_src = os.path.join(root, "studio", "backend", "src")
    main_py = os.path.join(backend_src, "studio_service", "main.py")
    if not os.path.isfile(main_py):
        return ("FAIL", f"Studio backend entry missing: {main_py}")

    env = os.environ.copy()
    env["STUDIO_REPO_ROOT"] = root
    env["PYTHONPATH"] = f"{backend_src}{os.pathsep}{root}"

    snippet = (
        f"import importlib; m = importlib.import_module({module!r}); "
        "getattr(m, 'app', None) or getattr(m, 'create_app', lambda: None)()"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", snippet],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return ("FAIL", f"Studio import timed out: {module}")
    if proc.returncode == 0:
        return ("PASS", f"Studio backend import OK: {module}")
    detail = (proc.stderr or proc.stdout or "unknown error").strip().splitlines()
    tail = detail[-1] if detail else "import failed"
    return ("FAIL", f"Studio backend import failed ({module}): {tail}")


def run_doctor(root: str) -> list[Finding]:
    findings: list[Finding] = []

    try:
        checks = _load_doctor_checks(root)
    except FileNotFoundError as exc:
        findings.append(("FAIL", str(exc)))
        return findings

    for item in checks.get("directories", {}).get("items", []):
        findings.append(_check_dir(root, item))

    for item in checks.get("files", {}).get("items", []):
        findings.append(_check_file(root, item))

    for item in checks.get("forbidden_paths", {}).get("items", []):
        findings.append(_check_absent(root, item))

    cursor = checks.get("cursor", {})
    for section in ("commands", "rules", "skills", "agents", "hooks"):
        for item in cursor.get(section, []):
            findings.append(_check_file(root, item))

    for item in checks.get("docs", {}).get("items", []):
        findings.append(_check_file_nonempty(root, item))

    for item in checks.get("yaml_validity", {}).get("files", []):
        findings.append(_check_yaml(root, item))

    for item in checks.get("content_markers", {}).get("items", []):
        path = item.get("path")
        for marker in item.get("contains", []):
            if path and marker:
                findings.append(_check_file_contains(root, path, marker))

    for item in checks.get("forbidden_content", {}).get("items", []):
        path = item.get("path")
        for marker in item.get("not_contains", []):
            if path and marker:
                findings.append(_check_file_not_contains(root, path, marker))

    for target in checks.get("makefile", {}).get("targets", []):
        findings.append(_check_makefile_target(root, target))

    for item in checks.get("workflow_files", {}).get("items", []):
        findings.append(_check_file_nonempty(root, item))

    try:
        sys.path.insert(0, os.path.join(root, ".sdlc", "dsl"))
        from core_config import env_map  # noqa: WPS433

        logical_env = env_map(root)
    except Exception:
        logical_env = {}

    for entry in checks.get("integrations", {}).get("items", []):
        role = entry.get("role") or entry.get("id", "integration")
        env_var = entry.get("env") or entry.get("config_env") or ""
        if entry.get("env_logical") and logical_env:
            env_var = logical_env.get(entry["env_logical"], env_var)
        if env_var:
            findings.append(_check_integration_env(role, env_var))

    dsl_entry = checks.get("python_dsl", {}).get("importable")
    if dsl_entry:
        findings.append(_check_file(root, dsl_entry))

    studio_cfg = checks.get("studio", {})
    import_module = studio_cfg.get("import_app")
    if import_module:
        findings.append(_check_studio_import(root, import_module))

    try:
        sys.path.insert(0, os.path.join(root, ".sdlc", "dsl"))
        from roster_sync import check_roster_sync  # noqa: WPS433

        for level, message in check_roster_sync(Path(root)):
            findings.append((level, message))
    except Exception as exc:
        findings.append(("WARN", f"roster sync check skipped: {exc}"))

    try:
        sys.path.insert(0, os.path.join(root, ".sdlc", "dsl"))
        from lifecycle_shard_drift import (  # noqa: WPS433
            check_committed_plane_evidence,
            check_lifecycle_shard_drift,
        )

        for level, message in check_lifecycle_shard_drift(Path(root)):
            findings.append((level, message))
        findings.append(check_committed_plane_evidence(Path(root)))
    except Exception as exc:
        findings.append(("WARN", f"lifecycle shard drift check skipped: {exc}"))

    return findings


def _write_compliance_metrics(findings: list[Finding], root: Path) -> None:
    """Persist Doctor health for obs/auditor (P2.2 compliance metrics)."""
    import json
    from datetime import datetime

    pass_count = sum(1 for lvl, _ in findings if lvl == "PASS")
    warn_count = sum(1 for lvl, _ in findings if lvl == "WARN")
    fail_count = sum(1 for lvl, _ in findings if lvl == "FAIL")
    total = max(len(findings), 1)
    payload = {
        "source": "sdlc-doctor",
        "updated_at": datetime.now(UTC).isoformat(),
        "pass": pass_count,
        "warn": warn_count,
        "fail": fail_count,
        "health_pct": round(pass_count / total * 100),
        "compliance_pct": round((pass_count + warn_count * 0.5) / total * 100),
    }
    out = root / ".sdlc" / "memory" / "sdlc-compliance.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def print_report(findings: list[Finding], root: str | None = None) -> int:
    pass_count = warn_count = fail_count = 0

    for level, message in findings:
        if level == "PASS":
            pass_count += 1
            print(f"[PASS] {message}")
        elif level == "WARN":
            warn_count += 1
            print(f"[WARN] {message}")
        elif level == "FAIL":
            fail_count += 1
            print(f"[FAIL] {message}")
        else:
            print(f"[{level}] {message}")

    print()
    print(f"Doctor summary: {pass_count} passed, {warn_count} warnings, {fail_count} failed")

    repo = Path(root or os.getcwd())
    try:
        _write_compliance_metrics(findings, repo)
    except Exception as exc:
        print(f"[WARN] Could not write compliance metrics: {exc}")

    try:
        from doctor_health_canvas import write_health_canvas  # noqa: WPS433

        canvas_path = write_health_canvas(findings, repo)
        score = round(pass_count / max(len(findings), 1) * 100)
        print(f"[CANVAS] Health report: {canvas_path} (score {score}%)")
        print("[INFO] Summary: .sdlc/memory/doctor-health.json")
    except Exception as exc:
        print(f"[WARN] Could not write health canvas: {exc}")

    return 0 if fail_count == 0 else 1
