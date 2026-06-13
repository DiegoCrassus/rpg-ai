#!/usr/bin/env python3
"""Write QA evidence JSON for learning loop reward (RPG-18)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def evidence_path(card: str, root: Path | None = None) -> Path:
    base = root or ROOT
    return base / ".sdlc" / "memory" / f"qa-evidence-{card.upper()}.json"


def _parse_pytest_counts(output: str) -> tuple[int, int]:
    passed = failed = 0
    summary = re.search(r"(\d+) passed(?:.*?(\d+) failed)?", output)
    if summary:
        passed = int(summary.group(1))
        if summary.group(2):
            failed = int(summary.group(2))
    fail_only = re.search(r"(\d+) failed", output)
    if fail_only and not summary:
        failed = int(fail_only.group(1))
    return passed, failed


def run_command(cmd: list[str], *, cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output


def build_evidence(
    *,
    card: str,
    test_cmd: list[str],
    root: Path | None = None,
    run_doctor: bool = True,
) -> dict:
    base = root or ROOT
    test_exit, test_output = run_command(test_cmd, cwd=base)
    passed, failed = _parse_pytest_counts(test_output)

    doctor_exit = 0
    doctor_summary = ""
    if run_doctor:
        doctor_exit, doctor_output = run_command(
            [sys.executable, ".sdlc/dsl/cli.py", "doctor"],
            cwd=base,
        )
        for line in doctor_output.splitlines():
            if "Doctor summary" in line:
                doctor_summary = line.strip()

    verdict = "PASS" if test_exit == 0 and doctor_exit == 0 else "FAIL"
    return {
        "card": card.upper(),
        "timestamp": _now_iso(),
        "tests": {
            "command": " ".join(test_cmd),
            "exit_code": test_exit,
            "passed": passed,
            "failed": failed,
        },
        "doctor": {
            "exit_code": doctor_exit,
            "summary": doctor_summary,
        },
        "verdict": verdict,
    }


def write_evidence(
    *,
    card: str,
    test_cmd: list[str] | None = None,
    root: Path | None = None,
    run_doctor: bool = True,
) -> Path:
    if not card:
        raise ValueError("card required")
    cmd = test_cmd or [
        sys.executable,
        "-m",
        "pytest",
        ".sdlc/dsl/test_learning_loop.py",
        ".sdlc/dsl/test_execution_ledger.py",
        "-q",
    ]
    payload = build_evidence(card=card, test_cmd=cmd, root=root, run_doctor=run_doctor)
    path = evidence_path(card, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def cmd_write(args: argparse.Namespace) -> int:
    cmd = args.test_cmd.split() if args.test_cmd else None
    path = write_evidence(
        card=args.card,
        test_cmd=cmd,
        run_doctor=not args.skip_doctor,
    )
    data = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"OK: wrote {path.relative_to(ROOT)}", file=sys.stderr)
    return 0 if data.get("verdict") == "PASS" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="QA evidence writer for learning loop")
    sub = parser.add_subparsers(dest="command", required=True)

    w = sub.add_parser("write", help="Run tests + doctor and write qa-evidence JSON")
    w.add_argument("--card", required=True)
    w.add_argument("--test-cmd", default="", help='Shell-style command, e.g. "python -m pytest -q"')
    w.add_argument("--skip-doctor", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "write":
        return cmd_write(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
