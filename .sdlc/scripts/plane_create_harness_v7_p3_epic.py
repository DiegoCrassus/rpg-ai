#!/usr/bin/env python3
"""Create Harness v7 P3 epic and child cards on Plane (idempotent)."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from board_client import board_api, format_card  # noqa: E402
from plane_html import build_plan_html  # noqa: E402

EPIC_TITLE = "[AI][EPIC] Harness v7 P3 — Docs merge + support agent model"

CHILDREN = [
    {
        "title": "[AI][SDLC] Merge gates README into gateways README",
        "slug": "gates-readme-merge",
        "story": "Single harness doc for write gate + interaction gateway; gates/README becomes redirect stub.",
        "scope": [
            "Merge gates/README content into gateways/README (Write gate section)",
            "Stub gates/README pointing to gateways",
            "Update .sdlc/README module map and doctor content_markers",
            "Keep gates/paths.yaml folder (generated shim only)",
        ],
        "ac": [
            "gateways/README contains write gate ACL + interaction harness",
            "gates/README is stub redirect only",
            "make sdlc-doctor exit 0",
        ],
    },
    {
        "title": "[AI][SDLC] Support agents skills-only invocation model",
        "slug": "support-agents-skills",
        "story": "Catalog marks support agents as skill-only; orchestrator invokes via Skill not pipeline handoff.",
        "scope": [
            "catalog.yaml agents.support invocation: skill-only + skill refs",
            "AGENTS.md + subagent-delegation matrix for support vs pipeline",
            "gateways policy support_agents list (spawn without handoff route match)",
            "Doctor roster check: support not required in policy.valid_agents pipeline set",
        ],
        "ac": [
            "catalog support entries have invocation: skill-only",
            "Docs state support agents never appear as handoff Next agent",
            "Unit test catalog support invocation model",
            "make sdlc-doctor exit 0",
        ],
    },
]


def _headers(api_key: str) -> dict[str, str]:
    return {"X-API-Key": api_key, "Content-Type": "application/json", "Accept": "application/json"}


def _issues_url(workspace: str, project_id: str) -> str:
    return f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/{project_id}/issues/"


def resolve_state_id(api_key: str, workspace: str, project_id: str, *, name: str = "Todo") -> str:
    url = f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/{project_id}/states/"
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=_headers(api_key))
        resp.raise_for_status()
        data = resp.json()
        items = data if isinstance(data, list) else data.get("results") or []
        for item in items:
            if (item.get("name") or "").strip().lower() == name.lower():
                return str(item["id"])
    sys.exit(f"ERROR: Plane state '{name}' not found")


def list_issues(api_key: str, workspace: str, project_id: str) -> list[dict]:
    url = _issues_url(workspace, project_id)
    items: list[dict] = []
    cursor = ""
    with httpx.Client(timeout=60.0) as client:
        while True:
            params: dict[str, str | int] = {"per_page": 100}
            if cursor:
                params["cursor"] = cursor
            resp = client.get(url, headers=_headers(api_key), params=params)
            resp.raise_for_status()
            data = resp.json()
            items.extend(data.get("results") or [])
            cursor = data.get("next_cursor") or ""
            if not cursor or not data.get("next_page_results"):
                break
    return items


def find_by_title(issues: list[dict], title: str) -> dict | None:
    for item in issues:
        if (item.get("name") or "").strip() == title.strip():
            return item
    return None


def child_html(spec: dict, epic_card: str) -> str:
    return build_plan_html(
        {
            "task_name": spec["title"],
            "story": spec["story"],
            "scope": spec["scope"],
            "non_goals": [
                "No app/ product changes",
                "Do not delete gates/paths.yaml shim folder",
                "Do not collapse gate vs gateways YAML policy files",
            ],
            "assumptions": [
                f"Parent epic: {epic_card}",
                "P0+P1+P2 complete (RPG-17 epic Done)",
                "Authority: harness-v7-change-plan.md § P3",
            ],
            "risks": ["Doc link drift if cross-refs missed"],
            "impacted_areas": [
                ".sdlc/gateways/README.md",
                ".sdlc/gates/README.md",
                ".sdlc/manifest/catalog.yaml",
                "AGENTS.md",
                ".sdlc/gateways/policy.yaml",
            ],
            "acceptance_criteria": spec["ac"],
            "definition_of_done": [
                "pytest + sdlc-doctor green",
                "Evidence on Plane when merged",
            ],
            "task_breakdown": [f"Branch: feature/{{card}}-{spec['slug']}"],
        }
    )


def epic_html(child_lines: list[str]) -> str:
    return build_plan_html(
        {
            "task_name": EPIC_TITLE,
            "story": ["Harness v7 Phase P3: consolidate gate docs + support agent invocation model."],
            "scope": [
                "Merge gates README into gateways README",
                "Support agents skill-only in catalog and policy",
            ],
            "non_goals": ["Remove gates/ folder entirely", "Studio INVES rename"],
            "assumptions": ["P2 epic RPG-17 Done", "Orchestrator delegation enforced"],
            "risks": ["Doctor content_markers must stay aligned"],
            "impacted_areas": [".sdlc/gateways/", ".sdlc/gates/", ".sdlc/manifest/", "AGENTS.md"],
            "acceptance_criteria": [
                "Both child cards Done",
                "harness-v7-change-plan P3 checklist complete",
            ],
            "definition_of_done": ["Epic Done when children merged to develop"],
            "task_breakdown": child_lines,
        }
    )


def create_issue(
    api_key: str,
    workspace: str,
    project_id: str,
    *,
    name: str,
    description_html: str,
    parent: str | None,
    todo_state_id: str,
) -> dict:
    payload: dict[str, str] = {
        "name": name,
        "description_html": description_html,
        "state": todo_state_id,
    }
    if parent:
        payload["parent"] = parent
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(_issues_url(workspace, project_id), headers=_headers(api_key), json=payload)
        if resp.status_code >= 400:
            sys.exit(f"ERROR: create failed ({resp.status_code}): {resp.text[:500]}")
        return resp.json()


def main() -> int:
    api_key, workspace, project_id = board_api()
    todo_id = resolve_state_id(api_key, workspace, project_id)
    issues = list_issues(api_key, workspace, project_id)

    epic = find_by_title(issues, EPIC_TITLE)
    child_lines: list[str] = []

    if epic:
        epic_uuid = epic["id"]
        epic_seq = epic.get("sequence_id")
        epic_card = format_card(int(epic_seq)) if epic_seq else "RPG-?"
        print(f"OK: epic exists — {epic_card} {EPIC_TITLE}")
    else:
        placeholder_lines = [f"- {c['title']} (create on run)" for c in CHILDREN]
        epic = create_issue(
            api_key,
            workspace,
            project_id,
            name=EPIC_TITLE,
            description_html=epic_html(placeholder_lines),
            parent=None,
            todo_state_id=todo_id,
        )
        epic_uuid = epic["id"]
        epic_seq = epic.get("sequence_id")
        epic_card = format_card(int(epic_seq)) if epic_seq else "RPG-?"
        print(f"OK: created epic {epic_card}")
        issues = list_issues(api_key, workspace, project_id)

    for spec in CHILDREN:
        existing = find_by_title(issues, spec["title"])
        if existing:
            seq = existing.get("sequence_id")
            card = format_card(int(seq)) if seq else "RPG-?"
            child_lines.append(f"- {card}: {spec['title']} — branch feature/{card}-{spec['slug']}")
            print(f"OK: child exists — {card} {spec['title']}")
            continue
        created = create_issue(
            api_key,
            workspace,
            project_id,
            name=spec["title"],
            description_html=child_html(spec, epic_card),
            parent=epic_uuid,
            todo_state_id=todo_id,
        )
        seq = created.get("sequence_id")
        card = format_card(int(seq)) if seq else "RPG-?"
        child_lines.append(f"- {card}: {spec['title']} — branch feature/{card}-{spec['slug']}")
        print(f"OK: created child {card} — {spec['title']}")

    if epic_uuid and child_lines:
        url = f"{_issues_url(workspace, project_id)}{epic_uuid}/"
        with httpx.Client(timeout=60.0) as client:
            resp = client.patch(
                url,
                headers=_headers(api_key),
                json={"description_html": epic_html(child_lines)},
            )
            resp.raise_for_status()
        print("OK: epic task breakdown updated")

    print("\nChild cards:")
    for line in child_lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
