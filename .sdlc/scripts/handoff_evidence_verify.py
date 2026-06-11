#!/usr/bin/env python3
"""Cross-check orchestrator handoff against board, git branch, and QA evidence."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".sdlc" / "scripts"
DSL = ROOT / ".sdlc" / "dsl"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
if str(DSL) not in sys.path:
    sys.path.insert(0, str(DSL))

from board_client import card_re  # noqa: E402

HANDOFF = ROOT / ".sdlc" / "memory" / "orchestrator-handoff.md"


def _parse_handoff() -> dict[str, str]:
    if not HANDOFF.is_file():
        return {}
    text = HANDOFF.read_text(encoding="utf-8")
    row_re = re.compile(r"^\|\s*(?:\*\*)?([^|*]+?)(?:\*\*)?\s*\|\s*([^|]+?)\s*\|$")
    section = ""
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        if set(line.strip()) <= {"|", "-", " "}:
            continue
        m = row_re.match(line.strip())
        if m and section:
            key = f"{section}.{m.group(1).strip().strip('*').lower()}"
            fields[key] = m.group(2).strip().strip("*")
    return fields


def _branch_exists(branch: str) -> bool:
    if not branch or branch in ("(none)", "-", "—"):
        return True
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", f"refs/heads/{branch}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0


def _qa_evidence_ok(card: str) -> tuple[bool, str]:
    for name in (f"qa-evidence-{card.upper()}.json", f".evidence-{card.upper()}.json"):
        path = ROOT / ".sdlc" / "memory" / name
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return False, f"invalid JSON: {path}"
            validation = data.get("validation") or {}
            val = str(validation.get("tests", ""))
            exit_code = validation.get("exit_code")
            if exit_code is not None and int(exit_code) != 0:
                return False, f"QA evidence exit_code={exit_code} in {path.name}"
            if val and "fail" in val.lower():
                return False, f"QA evidence reports failures in {path.name}"
            if val and "error" in val.lower() and "passed" not in val.lower():
                return False, f"QA evidence reports errors in {path.name}"
            if val and "passed" not in val.lower():
                return (
                    False,
                    f"QA evidence must include passing pytest summary in {path.name}",
                )
            return True, path.name
    return False, "no qa-evidence or .evidence JSON under .sdlc/memory/"


def verify(*, require_plane: bool = True) -> list[str]:
    """Return list of problems (empty = OK)."""
    fields = _parse_handoff()
    problems: list[str] = []

    stage_complete = fields.get("routing.stage complete", "").lower()
    if stage_complete != "yes":
        return []

    card = fields.get("session.card", "").upper()
    branch = fields.get("session.branch", "")
    stage = fields.get("session.stage", "").lower()
    previous = fields.get("routing.previous agent", "").lower()

    if card and not card_re().match(card):
        problems.append(f"Session.Card invalid: {card}")

    if branch and not _branch_exists(branch):
        problems.append(f"Branch '{branch}' not found locally (git)")

    if previous in ("qa", "reviewer") and stage in ("validation", "review", "deployment"):
        ok, detail = _qa_evidence_ok(card)
        if not ok:
            problems.append(f"QA evidence: {detail}")

    if require_plane and card and card_re().match(card):
        try:
            sys.path.insert(0, str(ROOT / ".sdlc" / "scripts"))
            from plane_card import _api, find_issue_uuid, get_issue, parse_card  # noqa: E402

            api_key, workspace, project_id = _api()
            uuid = find_issue_uuid(api_key, workspace, project_id, parse_card(card))
            issue = get_issue(api_key, workspace, project_id, uuid)
            state = issue.get("state") or {}
            group = ""
            if isinstance(state, dict):
                group = str(state.get("group") or "").lower()
            elif isinstance(state, str):
                group = state.lower()
            if group and group not in ("started", "completed", "unstarted"):
                problems.append(f"Plane card {card} state group unexpected: {group}")
        except SystemExit:
            raise
        except Exception as exc:
            problems.append(f"Plane verification failed: {exc}")

    return problems


def main() -> int:
    problems = verify()
    if problems:
        for p in problems:
            print(f"FAIL: {p}", file=sys.stderr)
        return 1
    print("OK: handoff evidence verification passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
