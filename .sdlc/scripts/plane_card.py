#!/usr/bin/env python3
"""Board card formatting and evidence publishing (Plane provider)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import httpx

SCRIPTS = Path(__file__).resolve().parent
DSL = SCRIPTS.parent / "dsl"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
if str(DSL) not in sys.path:
    sys.path.insert(0, str(DSL))

from board_client import board_api, format_card, parse_card  # noqa: E402
from board_granularity import detect_intent_from_handoff, validate_granularity  # noqa: E402
from plane_evidence import build_completion_evidence  # noqa: E402
from plane_html import convert_legacy_description  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def _api() -> tuple[str, str, str]:
    return board_api()


def _headers(api_key: str) -> dict[str, str]:
    return {"X-API-Key": api_key, "Content-Type": "application/json"}


def find_issue_uuid(api_key: str, workspace: str, project_id: str, sequence_id: int) -> str:
    url = f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/{project_id}/issues/"
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=_headers(api_key), params={"per_page": 100})
        resp.raise_for_status()
        for item in resp.json().get("results", []):
            if item.get("sequence_id") == sequence_id:
                return item["id"]
    sys.exit(f"ERROR: {format_card(sequence_id)} not found")


def get_issue(api_key: str, workspace: str, project_id: str, issue_uuid: str) -> dict:
    url = (
        f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/"
        f"{project_id}/issues/{issue_uuid}/"
    )
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=_headers(api_key))
        resp.raise_for_status()
        return resp.json()


def count_child_issues(
    api_key: str, workspace: str, project_id: str, parent_uuid: str
) -> int:
    url = f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/{project_id}/issues/"
    count = 0
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=_headers(api_key), params={"per_page": 100})
        resp.raise_for_status()
        for item in resp.json().get("results", []):
            parent = item.get("parent")
            if parent == parent_uuid:
                count += 1
    return count


def patch_description(
    api_key: str, workspace: str, project_id: str, issue_uuid: str, html: str
) -> None:
    url = (
        f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/"
        f"{project_id}/issues/{issue_uuid}/"
    )
    with httpx.Client(timeout=30.0) as client:
        resp = client.patch(url, headers=_headers(api_key), json={"description_html": html})
        resp.raise_for_status()


def post_comment(
    api_key: str, workspace: str, project_id: str, issue_uuid: str, html: str
) -> None:
    url = (
        f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/"
        f"{project_id}/issues/{issue_uuid}/comments/"
    )
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, headers=_headers(api_key), json={"comment_html": html})
        resp.raise_for_status()


def reformat_description(card: str) -> None:
    api_key, workspace, project_id = _api()
    seq = parse_card(card)
    uuid = find_issue_uuid(api_key, workspace, project_id, seq)
    issue = get_issue(api_key, workspace, project_id, uuid)
    old = issue.get("description_html") or ""
    new = convert_legacy_description(old)
    patch_description(api_key, workspace, project_id, uuid, new)
    print(f"OK: reformatted description {format_card(seq)}")


def _strip_html(html: str) -> str:
    # Preserve list items as "- " bullets before stripping tags
    text = re.sub(r"<li[^>]*>", "\n- ", html or "", flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def validate_plan(card: str) -> int:
    """Validate Plane card description has required plan sections."""
    api_key, workspace, project_id = _api()
    seq = parse_card(card)
    uuid = find_issue_uuid(api_key, workspace, project_id, seq)
    issue = get_issue(api_key, workspace, project_id, uuid)
    html = issue.get("description_html") or ""
    text = _strip_html(html).lower()

    failures: list[str] = []

    if len(html) < 200:
        failures.append("description too short (< 200 chars HTML)")

    ac_markers = ("acceptance criteria", "critérios de aceite", "criteria")
    if not any(m in text for m in ac_markers):
        failures.append("missing Acceptance Criteria section")
    else:
        ac_count = len(re.findall(r"\b(ac[- ]?\d+|criterion|\d+\.\s)", text, re.I))
        bullet_count = text.count("•") + text.count("- ")
        if ac_count < 3 and bullet_count < 3:
            failures.append("need >= 3 acceptance criteria (numbered or bullets)")

    ng_markers = ("non-goals", "non goals", "fora de escopo", "nao objetivos", "não objetivos")
    if not any(m in text for m in ng_markers):
        failures.append("missing Non-Goals section (>= 2)")
    else:
        ng_region = text.split("non-goals")[-1][:400] if "non-goals" in text else text
        if ng_region.count("- ") + ng_region.count("•") < 2:
            failures.append("need >= 2 non-goals")

    risk_markers = ("risk", "risco", "mitigation", "mitiga")
    if not any(m in text for m in risk_markers):
        failures.append("missing Risks section (>= 2)")
    else:
        if text.count("risk") + text.count("risco") < 2:
            failures.append("need >= 2 risks with mitigations")

    scope_markers = ("scope", "escopo", "impacted areas", "areas impactadas")
    if not any(m in text for m in scope_markers):
        failures.append("missing Scope / Impacted Areas")

    if failures:
        print(f"FAIL: {format_card(seq)} plan validation:")
        for f in failures:
            print(f"  - {f}")
        print("Fix: use .cursor/skills/board-task-creation/SKILL.md")
        return 1

    print(f"OK: {format_card(seq)} plan validated")
    return 0


def validate_granularity_cmd(card: str, *, intent: str = "") -> int:
    """Validate epic decomposition — no monolithic FULLSTACK cards."""
    api_key, workspace, project_id = _api()
    seq = parse_card(card)
    uuid = find_issue_uuid(api_key, workspace, project_id, seq)
    issue = get_issue(api_key, workspace, project_id, uuid)
    child_count = count_child_issues(api_key, workspace, project_id, uuid)
    resolved_intent = (intent or detect_intent_from_handoff(ROOT)).upper()
    failures = validate_granularity(
        issue, intent=resolved_intent, child_count=child_count, root=ROOT
    )
    if failures:
        print(f"FAIL: {format_card(seq)} granularity (intent={resolved_intent}):")
        for f in failures:
            print(f"  - {f}")
        print("Fix: .cursor/skills/board-task-creation/SKILL.md — epic + child cards")
        return 1
    print(f"OK: {format_card(seq)} granularity validated ({child_count} linked children)")
    return 0


def validate_all(card: str, *, intent: str = "") -> int:
    if validate_plan(card) != 0:
        return 1
    name = ""
    try:
        api_key, workspace, project_id = _api()
        seq = parse_card(card)
        uuid = find_issue_uuid(api_key, workspace, project_id, seq)
        issue = get_issue(api_key, workspace, project_id, uuid)
        name = (issue.get("name") or "").upper()
    except SystemExit:
        return 1
    resolved_intent = (intent or detect_intent_from_handoff(ROOT)).upper()
    # Skip granularity for obvious child cards (not EPIC)
    if "[AI][EPIC]" in name or resolved_intent in ("GREENFIELD", "FEATURE"):
        return validate_granularity_cmd(card, intent=resolved_intent)
    return 0


def post_evidence(card: str, data: dict, *, replace: bool = False) -> None:
    api_key, workspace, project_id = _api()
    seq = parse_card(card)
    uuid = find_issue_uuid(api_key, workspace, project_id, seq)
    data.setdefault("card", card)
    html = build_completion_evidence(data)
    if replace:
        patch_description(api_key, workspace, project_id, uuid, html)
        print(f"OK: evidence appended to description {format_card(seq)}")
    else:
        post_comment(api_key, workspace, project_id, uuid, html)
        print(f"OK: evidence comment on {format_card(seq)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Board card formatting and evidence")
    sub = parser.add_subparsers(dest="command", required=True)

    r = sub.add_parser("reformat-description", help="Upgrade description to TipTap HTML")
    r.add_argument("--card", required=True)

    e = sub.add_parser("post-evidence", help="Post structured Done evidence comment")
    e.add_argument("--card", required=True)
    e.add_argument("--file", required=True, help="JSON evidence file")
    e.add_argument(
        "--append-to-description",
        action="store_true",
        help="Also append evidence block to card description",
    )

    sub.add_parser("reformat-all", help="Reformat RPG-19..24 descriptions")

    v = sub.add_parser("validate-plan", help="Validate card plan completeness")
    v.add_argument("--card", required=True)

    g = sub.add_parser("validate-granularity", help="Validate epic + child card decomposition")
    g.add_argument("--card", required=True)
    g.add_argument("--intent", default="", help="GREENFIELD|FEATURE|...")

    a = sub.add_parser("validate-all", help="validate-plan + validate-granularity")
    a.add_argument("--card", required=True)
    a.add_argument("--intent", default="")

    args = parser.parse_args()
    if args.command == "reformat-description":
        reformat_description(args.card)
    elif args.command == "post-evidence":
        data = json.loads(Path(args.file).read_text(encoding="utf-8"))
        post_evidence(args.card, data, replace=args.append_to_description)
    elif args.command == "reformat-all":
        for n in range(19, 25):
            reformat_description(format_card(n))
    elif args.command == "validate-plan":
        sys.exit(validate_plan(args.card))
    elif args.command == "validate-granularity":
        sys.exit(validate_granularity_cmd(args.card, intent=args.intent))
    elif args.command == "validate-all":
        sys.exit(validate_all(args.card, intent=args.intent))


if __name__ == "__main__":
    main()
