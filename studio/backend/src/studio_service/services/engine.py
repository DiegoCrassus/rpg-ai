"""Thin wrapper over Foundation ``studio/`` engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from studio.engine.canvas_view_model import build_canvas_from_sources
from studio.engine.compiler_core import CompilerInputError, compile_studio_sources
from studio.engine.mvp_readiness import build_mvp_readiness_from_sources
from studio.engine.validator_core import validate_studio_sources


class EngineService:
    def compile(self, root: Path) -> dict[str, Any]:
        try:
            result = compile_studio_sources(root)
        except CompilerInputError as exc:
            raise _compiler_input_error(exc) from exc
        return {
            "graph_ir": result.graph_ir,
            "workflow_ir": result.workflow_ir,
            "report": result.report,
        }

    def validate(self, root: Path) -> dict[str, Any]:
        try:
            result = validate_studio_sources(root)
        except CompilerInputError as exc:
            raise _compiler_input_error(exc) from exc
        return {
            "report": result.report,
            "results": result.results,
            "summary": result.summary,
        }

    def canvas(self, root: Path) -> dict[str, Any]:
        try:
            model = build_canvas_from_sources(root)
        except CompilerInputError as exc:
            raise _compiler_input_error(exc) from exc
        return model.to_dict()

    def readiness(self, root: Path) -> dict[str, Any]:
        return build_mvp_readiness_from_sources(root)


def _compiler_input_error(exc: CompilerInputError):
    from studio_service.api.errors import StudioApiError

    return StudioApiError(
        422,
        "COMPILER_INPUT_ERROR",
        "Required compiler inputs are missing or unreadable",
        details={
            "missing_paths": exc.missing_paths,
            "unreadable_yaml": exc.unreadable_yaml,
            "unreadable_paths": exc.unreadable_paths,
        },
    )
