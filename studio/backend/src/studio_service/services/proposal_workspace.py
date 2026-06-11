"""Temp workspaces for proposal dry-runs (no writes to real repo)."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from studio.engine.compiler_core import REQUIRED_SOURCE_PATHS


def _write_file(root: Path, rel_path: str, content: str) -> None:
    dest = root / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")


def build_validate_workspace(repo_root: Path, proposed_files: dict[str, str]) -> Path:
    """Minimal repo tree for ``studio`` compile + validate."""

    tmp = Path(tempfile.mkdtemp(prefix="studio-proposal-validate-"))
    for rel in REQUIRED_SOURCE_PATHS:
        src = repo_root / rel
        if src.is_file():
            dest = tmp / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    for rel, content in proposed_files.items():
        _write_file(tmp, rel, content)
    return tmp


def build_doctor_workspace(repo_root: Path, proposed_files: dict[str, str]) -> Path:
    """Temp tree for ``make sdlc-doctor`` with proposed .sdlc / .cursor overlays."""

    tmp = Path(tempfile.mkdtemp(prefix="studio-proposal-doctor-"))
    for name in ("Makefile", "pyproject.toml", "AGENTS.md"):
        src = repo_root / name
        if src.is_file():
            shutil.copy2(src, tmp / name)
    for prefix in (".sdlc", ".cursor"):
        src_dir = repo_root / prefix
        if src_dir.is_dir():
            shutil.copytree(
                src_dir,
                tmp / prefix,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
    for rel, content in proposed_files.items():
        _write_file(tmp, rel, content)
    return tmp


def cleanup_workspace(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
