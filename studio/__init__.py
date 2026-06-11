"""SDLC Studio — public Python API (re-exports Foundation engine)."""

from studio.engine import (
    CanvasViewModel,
    CompilerInputError,
    CompilerResult,
    ValidationRunResult,
    build_canvas_from_sources,
    build_canvas_view_model,
    compile_studio_sources,
    render_canvas_text,
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
