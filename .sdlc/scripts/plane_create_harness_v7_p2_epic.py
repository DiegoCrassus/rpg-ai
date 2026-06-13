#!/usr/bin/env python3
"""Create Harness v7 P2 epic and child cards on Plane (idempotent)."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from board_client import board_api, format_card  # noqa: E402
from plane_html import build_plan_html  # noqa: E402

EPIC_TITLE = "[AI][EPIC] Harness v7 P2 — Learning loop + structure slim"

CHILDREN = [
    {
        "title": "[AI][SDLC] Warm learning loop — QA evidence to reward",
        "slug": "warm-learning-loop",
        "story": "Close the operational learning loop: QA writes qa-evidence, hooks record real pytest metrics, events.jsonl populated.",
        "scope": [
            "QA subagentStop → qa-evidence-RPG-N.json",
            "learning hook reads pytest/doctor/gateway_block",
            "policy_memory.yaml seed on workflow finish",
        ],
        "ac": [
            "learning/data/events.jsonl has task events after QA run",
            "reward reflects tests_fail > 0",
            "make learning-loop-status shows count > 0 after session",
        ],
    },
    {
        "title": "[AI][SDLC] Orchestrator policy hints before Task spawn",
        "slug": "orchestrator-hints",
        "story": "Orchestrator reads learning_loop hints and injects policy_memory into Task spawn.",
        "scope": [
            "AGENTS.md decision tree: hints step before Task",
            "learning_loop.py hints --json CLI",
            "orchestrator-handoff includes policy slice when present",
        ],
        "ac": [
            "Orchestrator spawn template references hints output",
            "policy_memory.yaml consulted when file exists",
            "Unit test or smoke for hints CLI exit 0",
        ],
    },
    {
        "title": "[AI][SDLC] Merge pipeline roster into catalog",
        "slug": "catalog-pipeline-merge",
        "story": "Single agent roster in catalog.yaml; pipeline/agents.yaml becomes generated view or removed.",
        "scope": [
            "catalog.yaml absorbs stage→agent→skill bindings",
            "loader/roster_sync reads catalog only",
            "Doctor + Studio metadata updated",
        ],
        "ac": [
            "No duplicate agent definitions between catalog and pipeline",
            "make sdlc-doctor exit 0",
            "Studio pipeline metadata unchanged behavior",
        ],
    },
    {
        "title": "[AI][SDLC] Slim master-workflow to index",
        "slug": "slim-master-workflow",
        "story": "Reduce master-workflow.md prose; point to lifecycle-model and harness plans.",
        "scope": [
            "master-workflow.md ~80 lines index",
            "Remove duplicate stage tables and shim references",
            "Update L1 cross-links only",
        ],
        "ac": [
            "master-workflow.md under 120 lines",
            "change-lifecycle.md remains L1 authority for gitflow",
            "Doctor content_markers still pass",
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
                "P3 gates README merge deferred",
                "Studio INVES-* UI rename out of scope",
            ],
            "assumptions": [
                f"Parent epic: {epic_card}",
                "Builds on Harness v7 P0+P1 (PR #9, RPG-13)",
                "Authority: .sdlc/process/harness-v7-change-plan.md § P2",
            ],
            "risks": [
                "Learning loop needs real QA sessions to validate rewards",
                "Catalog merge may break Studio palette if roster drift",
            ],
            "impacted_areas": [
                ".sdlc/learning/",
                "AGENTS.md",
                ".cursor/hooks/sdlc_learning_hook.py",
                ".sdlc/manifest/catalog.yaml",
                ".sdlc/process/master-workflow.md",
            ],
            "acceptance_criteria": spec["ac"],
            "definition_of_done": [
                "pytest + sdlc-doctor green",
                "Evidence on Plane card when merged",
            ],
            "task_breakdown": [f"Branch: feature/{{card}}-{spec['slug']}"],
        }
    )


def epic_html(child_lines: list[str]) -> str:
    return build_plan_html(
        {
            "task_name": EPIC_TITLE,
            "story": [
                "Harness v7 Phase P2: warm learning loop, orchestrator hints, catalog merge, slim L1 docs.",
            ],
            "scope": [
                "Operational learning loop (not neural RL)",
                "Policy hints at Task spawn",
                "Roster consolidation",
                "master-workflow slim index",
            ],
            "non_goals": [
                "P3: gates README merge, support agents→skills",
                "Studio frontend INVES rename",
                "LLM gateway central",
            ],
            "assumptions": [
                "P0+P1 merged in PR #9 (RPG-13 Done)",
                "runtime/manifest.yaml and sdlc_obs operational",
            ],
            "risks": [
                "Cold loop until agents run full pipeline",
                "Catalog merge touches many readers",
            ],
            "impacted_areas": [
                ".sdlc/learning/",
                "AGENTS.md",
                ".cursor/rules/orchestrator.mdc",
                ".sdlc/manifest/",
                ".sdlc/process/",
            ],
            "acceptance_criteria": [
                "All four child cards Done",
                "Learning events populated in observe mode",
                "Orchestrator reads hints before Task spawn",
                "Single roster source in catalog",
                "master-workflow under 120 lines",
            ],
            "definition_of_done": [
                "Epic Done when all children merged to develop",
                "harness-v7-change-plan P2 checklist complete",
            ],
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
    print("\nStart workflow on first child (not epic):")
    first = child_lines[0].split(":")[0].strip("- ") if child_lines else "RPG-N"
    print(f"  python .sdlc/dsl/cli.py workflow start --card {first} --slug <slug> --stage sdlc_meta")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
