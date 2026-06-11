#!/usr/bin/env python3
"""Board work item state transitions (Plane provider)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import httpx

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from board_client import board_api, format_card, parse_card  # noqa: E402
from plane_evidence import build_completion_evidence, build_start_comment  # noqa: E402
from plane_html import document, paragraph_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
# RPG project (workspace rpg) — resolved 2026-06-11 via GET .../projects/{id}/states/
STATE_IDS = {
    "backlog": "bbc265c2-f254-4f69-95c9-241c83313270",
    "todo": "88bcb3dd-2608-4273-b365-c928a9aae8d6",
    "in_progress": "5e0a9f62-c844-4947-94c6-cd1db81f11e3",
    "done": "e77bb0d8-30f9-4071-9766-77854b7b9086",
    "cancelled": "bbad9436-2a55-41e2-ba5e-d0437f2fb507",
}


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
    print(f"ERROR: {format_card(sequence_id)} not found", file=sys.stderr)
    sys.exit(1)


def set_state(api_key: str, workspace: str, project_id: str, issue_uuid: str, state_key: str) -> dict:
    url = (
        f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/"
        f"{project_id}/issues/{issue_uuid}/"
    )
    with httpx.Client(timeout=30.0) as client:
        resp = client.patch(
            url, headers=_headers(api_key), json={"state": STATE_IDS[state_key]}
        )
        resp.raise_for_status()
        return resp.json()


def add_comment_html(
    api_key: str, workspace: str, project_id: str, issue_uuid: str, html: str
) -> None:
    url = (
        f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/"
        f"{project_id}/issues/{issue_uuid}/comments/"
    )
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, headers=_headers(api_key), json={"comment_html": html})
        resp.raise_for_status()


def wrap_comment(comment: str) -> str:
    if comment.strip().startswith("<div"):
        return comment
    if comment.strip().startswith("<"):
        return document(paragraph_text(comment))
    return document(paragraph_text(comment))


def main() -> None:
    parser = argparse.ArgumentParser(description="Board card state transitions")
    sub = parser.add_subparsers(dest="command", required=True)

    for name, state_key in (
        ("in-progress", "in_progress"),
        ("done", "done"),
        ("todo", "todo"),
        ("backlog", "backlog"),
        ("cancelled", "cancelled"),
    ):
        p = sub.add_parser(name)
        p.add_argument("--card", required=True)
        p.add_argument("--comment", default="")
        p.add_argument("--branch", default="", help="For in-progress start comment")
        p.add_argument("--evidence-file", default="", help="JSON completion evidence (done)")
        p.set_defaults(state_key=state_key)

    c = sub.add_parser("comment")
    c.add_argument("--card", required=True)
    c.add_argument("--comment", default="")
    c.add_argument("--evidence-file", default="")
    c.set_defaults(state_key=None)

    args = parser.parse_args()
    api_key, workspace, project_id = _api()
    seq = parse_card(args.card)
    issue_uuid = find_issue_uuid(api_key, workspace, project_id, seq)

    html_comment = ""
    if args.evidence_file:
        import json

        data = json.loads(Path(args.evidence_file).read_text(encoding="utf-8"))
        data.setdefault("card", args.card)
        html_comment = build_completion_evidence(data)
    elif args.command == "in-progress" and args.branch:
        html_comment = build_start_comment(args.card, args.branch)
    elif args.comment:
        html_comment = wrap_comment(args.comment)

    if args.command == "comment":
        if not html_comment:
            sys.exit("ERROR: --comment or --evidence-file required")
        add_comment_html(api_key, workspace, project_id, issue_uuid, html_comment)
        print(f"OK: comment on {format_card(seq)}")
        return

    data = set_state(api_key, workspace, project_id, issue_uuid, args.state_key)
    state_name = (data.get("state_detail") or {}).get("name", args.state_key)
    print(f"OK: {format_card(seq)} -> {state_name}")
    if html_comment:
        add_comment_html(api_key, workspace, project_id, issue_uuid, html_comment)


if __name__ == "__main__":
    main()
