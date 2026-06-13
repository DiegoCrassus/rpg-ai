"""Local, non-authoritative Studio command line entrypoint."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from studio.engine.canvas_view_model import build_canvas_from_sources, render_canvas_text
from studio.engine.compiler_core import CompilerInputError, compile_studio_sources
from studio.engine.mvp_readiness import build_mvp_readiness_from_sources, render_mvp_readiness_text
from studio.engine.mvp_test_skeleton import build_mvp_test_skeleton, render_mvp_test_skeleton_text
from studio.engine.publish_evidence import (
    PublishEvidenceInputError,
    build_publish_evidence_from_sources,
    render_publish_evidence_text,
)
from studio.engine.reporting import render_report_text
from studio.engine.simulation_preview import (
    SimulationPreviewInputError,
    build_simulation_preview_from_sources,
    render_simulation_preview_text,
)
from studio.engine.validation_inspection import (
    ValidationInspectionInputError,
    build_validation_inspection_from_sources,
    render_validation_inspection_text,
)
from studio.engine.validator_core import validate_studio_sources
from studio.engine.workflow_assistance import (
    WorkflowAssistanceInputError,
    build_workflow_assistance_from_sources,
    render_workflow_assistance_text,
)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Studio CLI and return a process exit code."""

    parser = _build_parser()
    args = parser.parse_args(argv)
    root = args.root if args.root is not None else Path.cwd()
    try:
        if args.command == "compile":
            return _run_compile(root, args.format)
        if args.command == "validate":
            return _run_validate(root, args.format)
        if args.command == "canvas":
            return _run_canvas(root, args.format)
        if args.command == "inspect-validation":
            return _run_inspect_validation(root, args)
        if args.command == "assist-workflow":
            return _run_assist_workflow(root, args)
        if args.command == "preview-simulation":
            return _run_preview_simulation(root, args)
        if args.command == "publish-evidence":
            return _run_publish_evidence(root, args)
        if args.command == "check-readiness":
            return _run_check_readiness(root, args)
        if args.command == "list-skeleton":
            return _run_list_skeleton(args)
    except (
        CompilerInputError,
        ValidationInspectionInputError,
        WorkflowAssistanceInputError,
        SimulationPreviewInputError,
        PublishEvidenceInputError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    parser.error("missing command")
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m studio.cli",
        description="Inspect derived, non-authoritative Studio compiler outputs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("compile", "validate", "canvas"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument(
            "--format",
            choices=("text", "json"),
            default="text",
            help="Output format.",
        )
        subparser.add_argument(
            "--root",
            type=Path,
            default=None,
            help="Repository root to inspect. Defaults to the current directory.",
        )
    inspect_parser = subparsers.add_parser("inspect-validation")
    inspect_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    inspect_parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root to inspect. Defaults to the current directory.",
    )
    inspect_parser.add_argument("--status", default=None, help="Filter by validation status.")
    inspect_parser.add_argument("--check-type", default=None, help="Filter by validation check type.")
    inspect_parser.add_argument("--target-type", default=None, help="Filter by validation target type.")
    inspect_parser.add_argument(
        "--group-by",
        default="status",
        help="Group visible records by status, check_type, or target_type.",
    )
    assist_parser = subparsers.add_parser("assist-workflow")
    assist_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    assist_parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root to inspect. Defaults to the current directory.",
    )
    assist_parser.add_argument("--kind", default=None, help="Filter suggestions by kind.")
    preview_parser = subparsers.add_parser("preview-simulation")
    preview_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    preview_parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root to inspect. Defaults to the current directory.",
    )
    preview_parser.add_argument("--scenario", default=None, help="Filter preview to one scenario id.")
    preview_parser.add_argument("--intent", default=None, help="Filter scenarios by intent (DOCS_ONLY or FEATURE).")
    preview_parser.add_argument("--path-label", default=None, help="Filter steps by path label.")
    preview_parser.add_argument("--step-kind", default=None, help="Filter steps by kind (handoff, stage, transition).")
    preview_parser.add_argument("--tag", default=None, help="Filter scenarios by tag.")
    evidence_parser = subparsers.add_parser("publish-evidence")
    evidence_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    evidence_parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root to inspect. Defaults to the current directory.",
    )
    evidence_parser.add_argument("--card", default=None, help="Plane card id for evidence_fields.card (RPG-N).")
    evidence_parser.add_argument("--title", default=None, help="Override evidence_fields.title.")
    evidence_parser.add_argument("--branch", default=None, help="Override evidence_fields.artifacts.branch.")
    readiness_parser = subparsers.add_parser("check-readiness")
    readiness_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    readiness_parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root to inspect. Defaults to the current directory.",
    )
    skeleton_parser = subparsers.add_parser("list-skeleton")
    skeleton_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    skeleton_parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Unused; skeleton is in-memory only. Accepted for CLI consistency.",
    )
    return parser


def _run_compile(root: Path, output_format: str) -> int:
    result = compile_studio_sources(root)
    payload = {
        "graph_ir": result.graph_ir,
        "workflow_ir": result.workflow_ir,
        "report": result.report,
    }
    if output_format == "json":
        _write_json(payload)
    else:
        _write_report_text(result.report)
    return 0


def _run_validate(root: Path, output_format: str) -> int:
    result = validate_studio_sources(root)
    payload = {
        "report": result.report,
        "results": result.results,
        "summary": result.summary,
    }
    if output_format == "json":
        _write_json(payload)
    else:
        _write_report_text(result.report)
    return 1 if result.summary.get("fail", 0) else 0


def _run_canvas(root: Path, output_format: str) -> int:
    model = build_canvas_from_sources(root)
    if output_format == "json":
        _write_json(model.to_dict())
    else:
        sys.stdout.write(render_canvas_text(model))
    return 1 if model.legend["validation_statuses"].get("fail", 0) else 0


def _run_inspect_validation(root: Path, args: argparse.Namespace) -> int:
    model = build_validation_inspection_from_sources(
        root,
        status=args.status,
        check_type=args.check_type,
        target_type=args.target_type,
        group_by=args.group_by,
    )
    if args.format == "json":
        _write_json(model)
    else:
        sys.stdout.write(render_validation_inspection_text(model))
    return 1 if model["summary"]["by_status"].get("fail", 0) else 0


def _run_assist_workflow(root: Path, args: argparse.Namespace) -> int:
    model = build_workflow_assistance_from_sources(root, kind=args.kind)
    if args.format == "json":
        _write_json(model)
    else:
        sys.stdout.write(render_workflow_assistance_text(model))
    return 1 if model["summary"]["validation_fail"] > 0 else 0


def _run_publish_evidence(root: Path, args: argparse.Namespace) -> int:
    model = build_publish_evidence_from_sources(
        root,
        card=args.card,
        title=args.title,
        branch=args.branch,
    )
    if args.format == "json":
        _write_json(model)
    else:
        sys.stdout.write(render_publish_evidence_text(model))
    return 1 if model["summary"]["validation_fail"] > 0 else 0


def _run_list_skeleton(args: argparse.Namespace) -> int:
    model = build_mvp_test_skeleton()
    if args.format == "json":
        _write_json(model)
    else:
        sys.stdout.write(render_mvp_test_skeleton_text(model))
    return 0


def _run_check_readiness(root: Path, args: argparse.Namespace) -> int:
    model = build_mvp_readiness_from_sources(root)
    if args.format == "json":
        _write_json(model)
    else:
        sys.stdout.write(render_mvp_readiness_text(model))
    summary = model["summary"]
    if summary["fail"] > 0:
        return 1
    if summary["warn"] > 0:
        return 2
    return 0


def _run_preview_simulation(root: Path, args: argparse.Namespace) -> int:
    model = build_simulation_preview_from_sources(
        root,
        scenario=args.scenario,
        intent=args.intent,
        path_label=args.path_label,
        step_kind=args.step_kind,
        tag=args.tag,
    )
    if args.format == "json":
        _write_json(model)
    else:
        sys.stdout.write(render_simulation_preview_text(model))
    blocked = model["summary"]["path_labels"].get("blocked", 0)
    return 1 if model["summary"]["validation_fail"] > 0 or blocked > 0 else 0


def _write_json(payload: dict[str, Any]) -> None:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def _write_report_text(report: dict[str, Any]) -> None:
    sys.stdout.write(render_report_text(report))


if __name__ == "__main__":
    raise SystemExit(main())
