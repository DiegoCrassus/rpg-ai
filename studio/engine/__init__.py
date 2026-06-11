"""SDLC Studio Foundation engine — compile, validate, canvas, CLI helpers."""

from studio.engine.canvas_view_model import (
    CanvasViewModel,
    build_canvas_from_sources,
    build_canvas_view_model,
    render_canvas_text,
)
from studio.engine.compiler_core import (
    CompilerInputError,
    CompilerResult,
    compile_studio_sources,
)
from studio.engine.validator_core import (
    ValidationRunResult,
    validate_compiler_result,
    validate_studio_sources,
)

__all__ = [
    "CompilerInputError",
    "CompilerResult",
    "CanvasViewModel",
    "ValidationRunResult",
    "build_canvas_from_sources",
    "build_canvas_view_model",
    "compile_studio_sources",
    "render_canvas_text",
    "validate_compiler_result",
    "validate_studio_sources",
]
