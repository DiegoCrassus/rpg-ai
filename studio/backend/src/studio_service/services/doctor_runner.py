"""Subprocess runner for proposal doctor dry-run."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

DOCTOR_TIMEOUT_SEC = 120


def run_doctor_in_workspace(
    workspace: Path,
    repo_root: Path,
) -> tuple[int, str, list[dict[str, Any]]]:
    """Run ``make sdlc-doctor`` in *workspace*; return (exit_code, summary, details)."""

    makefile = workspace / "Makefile"
    if not makefile.is_file():
        shutil_copy_makefile = repo_root / "Makefile"
        if shutil_copy_makefile.is_file():
            makefile.write_text(shutil_copy_makefile.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            return 1, "Makefile missing in doctor workspace", []

    proc = subprocess.run(
        ["make", "sdlc-doctor"],
        cwd=workspace,
        capture_output=True,
        text=True,
        timeout=DOCTOR_TIMEOUT_SEC,
    )
    details: list[dict[str, Any]] = []
    if proc.stdout:
        details.append({"stream": "stdout", "text": proc.stdout[-4000:]})
    if proc.stderr:
        details.append({"stream": "stderr", "text": proc.stderr[-4000:]})

    if proc.returncode == 0:
        return 0, "Doctor exited 0", details

    return (
        1,
        f"Doctor exited {proc.returncode}",
        details,
    )
