"""Derived, non-executing MVP readiness loop for SDLC Studio."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from studio.engine.canvas_view_model import CanvasViewModel, build_canvas_view_model
from studio.engine.compiler_core import compile_studio_sources
from studio.engine.publish_evidence import build_publish_evidence_model
from studio.engine.reporting import AUTHORITY
from studio.engine.simulation_preview import build_simulation_preview_model
from studio.engine.validation_inspection import build_validation_inspection_model
from studio.engine.validator_core import validate_compiler_result
from studio.engine.workflow_assistance import build_workflow_assistance_model

READINESS_ID = "readiness.sdlc_studio.mvp"
READINESS_SOURCE_PATHS = (
    "studio/engine/mvp_readiness.py",
    "studio/docs/prototypes/ai-mvp-readiness-prototype.md",
    "docs/roadmap/sdlc-studio-mvp-roadmap.md",
    "studio/docs/boundaries/operating-model.md",
)
CLI_COMMANDS = (
    "compile",
    "validate",
    "canvas",
    "inspect-validation",
    "assist-workflow",
    "preview-simulation",
    "publish-evidence",
    "check-readiness",
)
OPERATING_MODEL_MARKERS = ("Derived Vs Authoritative", "Plane", "python -m studio.cli")
READINESS_NON_GOALS = (
    "Does not run make sdlc-doctor, pytest, CI, Plane, GitHub, or shell workflows.",
    "Does not mutate source artifacts or persist readiness reports.",
    "Does not declare MVP complete without human reviewer sign-off on Plane.",
)
MODULE_CHECKS = (
    ("readiness.compiler", "Compiler core and compile CLI", "studio/engine/compiler_core.py", "studio/docs/contracts/compiler-validator-boundaries.md", "compile", ("graph_ir", "workflow_ir", "report")),
    ("readiness.validator", "Validator core and validate CLI", "studio/engine/validator_core.py", "studio/docs/contracts/validation-result-ir-contract.md", "validate", ("report", "results", "summary")),
    ("readiness.canvas", "Canvas view model and canvas CLI", "studio/engine/canvas_view_model.py", "studio/docs/contracts/visual-orchestration-prototype.md", "canvas", ("canvas", "nodes", "edges", "overlays", "sections", "legend")),
    ("readiness.inspection", "Validation inspection and inspect-validation CLI", "studio/engine/validation_inspection.py", "studio/docs/contracts/visual-orchestration-prototype.md", "inspect-validation", ("inspection", "summary", "groups", "records")),
    ("readiness.assistance", "Workflow assistance and assist-workflow CLI", "studio/engine/workflow_assistance.py", "studio/docs/prototypes/ai-workflow-assistance-prototype.md", "assist-workflow", ("assistance", "summary", "explanations", "suggestions", "annotations")),
    ("readiness.simulation", "Simulation preview and preview-simulation CLI", "studio/engine/simulation_preview.py", "studio/docs/prototypes/ai-simulation-preview-prototype.md", "preview-simulation", ("simulation", "summary", "scenarios", "lifecycle_map")),
    ("readiness.publish_evidence", "Publish evidence projection and publish-evidence CLI", "studio/engine/publish_evidence.py", "studio/docs/prototypes/ai-publish-evidence-prototype.md", "publish-evidence", ("projection", "summary", "evidence_fields")),
)


def build_mvp_readiness_from_sources(root: Any) -> dict[str, Any]:
    """Compile, validate, derive pipeline outputs, and evaluate the MVP checklist."""

    repo_root = Path(root)
    compiled = compile_studio_sources(repo_root)
    validation = validate_compiler_result(compiled, repo_root)
    canvas = build_canvas_view_model(compiled, validation)
    inspection = build_validation_inspection_model(compiled, validation, canvas)
    assistance = build_workflow_assistance_model(compiled, validation, canvas, inspection)
    simulation = build_simulation_preview_model(compiled, validation, canvas, inspection)
    evidence = build_publish_evidence_model(compiled, validation, canvas, inspection)
    derived = {
        "readiness.compiler": {"graph_ir": compiled.graph_ir, "workflow_ir": compiled.workflow_ir, "report": compiled.report},
        "readiness.validator": {"report": validation.report, "results": validation.results, "summary": validation.summary},
        "readiness.canvas": canvas.to_dict(),
        "readiness.inspection": inspection,
        "readiness.assistance": assistance,
        "readiness.simulation": simulation,
        "readiness.publish_evidence": evidence,
    }
    fail_count = validation.summary.get("fail", 0)
    checks = [
        _module_check(repo_root, spec, derived[spec[0]], fail_count, canvas)
        for spec in MODULE_CHECKS
    ]
    checks.append(_operating_model_check(repo_root))
    return _build_readiness_model(checks)


def _module_check(
    root: Path,
    spec: tuple[str, str, str, str, str, tuple[str, ...]],
    model: dict[str, Any],
    fail_count: int,
    canvas: CanvasViewModel,
) -> dict[str, Any]:
    check_id, label, module, doc, cli, keys = spec
    missing = [path for path in (module, doc) if not (root / path).is_file()]
    if missing:
        return _record(check_id, label, "fail", f"missing: {', '.join(missing)}", module, doc, cli)
    if set(model) != set(keys):
        return _record(check_id, label, "fail", "unexpected derived model keys", module, doc, cli)
    status = _status_for(check_id, model, fail_count, canvas)
    return _record(check_id, label, status, f"derived model ok; validation_fail={fail_count}", module, doc, cli)


def _status_for(check_id: str, model: dict[str, Any], fail_count: int, canvas: CanvasViewModel) -> str:
    if fail_count > 0 and check_id != "readiness.simulation":
        return "fail"
    if check_id == "readiness.compiler" and model["report"].get("status") == "fail":
        return "fail"
    if check_id == "readiness.canvas" and canvas.legend["validation_statuses"].get("fail", 0):
        return "fail"
    if check_id in {"readiness.assistance", "readiness.publish_evidence"} and model["summary"]["validation_fail"]:
        return "fail"
    if check_id == "readiness.simulation" and model["summary"]["validation_fail"]:
        return "fail"
    return "pass"


def _operating_model_check(root: Path) -> dict[str, Any]:
    doc = "studio/docs/boundaries/operating-model.md"
    path = root / doc
    if not path.is_file():
        return _record("readiness.operating_model", "Studio operating model documentation", "fail", f"missing: {doc}", doc=doc)
    text = path.read_text(encoding="utf-8")
    missing = [marker for marker in OPERATING_MODEL_MARKERS if marker not in text]
    if missing:
        return _record("readiness.operating_model", "Studio operating model documentation", "fail", f"missing markers: {', '.join(missing)}", doc=doc)
    return _record("readiness.operating_model", "Studio operating model documentation", "pass", "operating model doc present", doc=doc)


def _record(
    check_id: str,
    label: str,
    status: str,
    detail: str,
    module: str = "",
    doc: str = "",
    cli: str = "",
) -> dict[str, Any]:
    record: dict[str, Any] = {"id": check_id, "label": label, "status": status, "detail": detail}
    if module:
        record["module"] = module
    if doc:
        record["doc"] = doc
    if cli:
        record["cli"] = cli
    return record


def _build_readiness_model(checks: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {"pass": 0, "warn": 0, "fail": 0}
    for check in checks:
        counts[str(check["status"])] = counts.get(str(check["status"]), 0) + 1
    overall = "fail" if counts["fail"] else ("warn" if counts["warn"] else "pass")
    return {
        "readiness": {
            "id": READINESS_ID,
            "authority": AUTHORITY,
            "execution_mode": "non_executing_readiness_loop",
            "overall_status": overall,
            "source_refs": [{"ref_type": "path", "ref": path} for path in READINESS_SOURCE_PATHS],
            "non_goals": list(READINESS_NON_GOALS),
        },
        "summary": {"check_count": len(checks), **counts, "mvp_ready": overall == "pass"},
        "checks": checks,
        "cli_commands": list(CLI_COMMANDS),
    }


def render_mvp_readiness_text(model: dict[str, Any]) -> str:
    readiness, summary = model["readiness"], model["summary"]
    lines = [
        "Studio MVP readiness: derived, non-authoritative output",
        f"readiness: {readiness['id']}",
        f"authority: {readiness['authority']}",
        f"execution_mode: {readiness['execution_mode']}",
        f"overall_status: {readiness['overall_status']}",
        f"mvp_ready: {summary['mvp_ready']}",
        f"checks: {summary['check_count']} pass={summary['pass']} warn={summary['warn']} fail={summary['fail']}",
        "checks:",
        *(f"- [{check['status']}] {check['id']}: {check['detail']}" for check in model["checks"]),
        f"cli_commands: {', '.join(model['cli_commands'])}",
        "reminder: readiness is transient stdout/in-memory only; Doctor and Plane evidence remain authoritative.",
    ]
    return "\n".join(lines) + "\n"
