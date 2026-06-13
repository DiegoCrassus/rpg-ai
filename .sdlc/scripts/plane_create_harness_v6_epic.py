#!/usr/bin/env python3
"""Create Harness v6 + Learning Loop epic and child cards on Plane (idempotent)."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from board_client import board_api, format_card  # noqa: E402
from plane_html import build_plan_html  # noqa: E402

EPIC_TITLE = "[AI][EPIC] Harness v6 — SDLC learning loop"

CHILDREN = [
    {
        "title": "[AI][SDLC] Learning loop — schemas and reward engine",
        "slug": "learning-reward-engine",
        "story": "Implement .sdlc/learning/schemas.py and reward_engine.py with deterministic reward [-1,1].",
        "scope": [
            "SDLCRunEvent schema v1",
            "RewardEngine with test/lint/security/rollback/token rules",
            "Unit tests pytest",
        ],
        "ac": [
            "reward_engine.py returns -1 on security fail or rollback",
            "tests fail caps reward at 0",
            "pytest green for learning module",
        ],
    },
    {
        "title": "[AI][SDLC] Learning loop — event store and hook integration",
        "slug": "learning-event-store",
        "story": "Task-level event store + subagentStop bridge from hooks and token budget.",
        "scope": [
            "event_store.py JSONL under .sdlc/learning/data/",
            "Hook records task events on subagentStop",
            "Rollup into execution_ledger stage events",
        ],
        "ac": [
            "Every subagentStop with open gate writes task event",
            "event_store tail/status CLI works",
            "Integration test or smoke script passes",
        ],
    },
    {
        "title": "[AI][SDLC] Learning loop — policy memory and optimizer",
        "slug": "learning-policy-optimizer",
        "story": "Rule-based policy_memory.yaml and policy_optimizer from reward history.",
        "scope": [
            "policy_memory.py load/save lessons",
            "policy_optimizer.py suggest model/agent/context (observe mode)",
            "Orchestrator reads policy hints before Task spawn",
        ],
        "ac": [
            "policy_memory.yaml updated after workflow finish",
            "optimizer report JSON with patterns",
            "harness-v6-plan Phase D-E complete",
        ],
    },
    {
        "title": "[AI][SDLC] Harness strict gates and lifecycle merge",
        "slug": "harness-strict-gates",
        "story": "Re-enable strict enforcement and consolidate lifecycle shims.",
        "scope": [
            "core.gates.enforcement strict",
            "Repointer gate/loader to lifecycle-model only",
            "Remove deprecated paths.yaml / transitions.yaml shims",
        ],
        "ac": [
            "Protected app/ writes blocked without open gate",
            "make sdlc-doctor exit 0",
            "make sdlc-validate exit 0",
        ],
    },
    {
        "title": "[AI][SDLC] SDLC structure cleanup",
        "slug": "sdlc-structure-cleanup",
        "story": "Remove SDLC duplicates, legacy evidence, plane-* stubs, doc drift. No studio/ app.",
        "scope": [
            "Delete plane-* skill stubs after board-* ref update",
            "Remove rpg-*-evidence.json local files",
            "Fix investiments/sdlc-ai drift in .sdlc/ and .cursor/",
            "Remove dead Makefile targets and orphan scripts",
        ],
        "ac": [
            "No plane-sdlc/plane-task-creation stubs remain",
            "change-lifecycle.md matches sdlc.yaml vendors",
            "Doctor green after cleanup",
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
                "No changes under app/ or studio/",
                "No LLM training or neural RL",
            ],
            "assumptions": [
                f"Parent epic: {epic_card}",
                "Authority: .sdlc/process/harness-v6-plan.md",
            ],
            "risks": [
                "Hook integration may need Cursor restart",
                "Strict gates may block mid-session without workflow start",
            ],
            "impacted_areas": [".sdlc/learning/", ".cursor/hooks/", ".sdlc/process/"],
            "acceptance_criteria": spec["ac"],
            "definition_of_done": [
                "pytest + sdlc-doctor green",
                "Evidence on Plane card when merged",
            ],
            "task_breakdown": [
                f"Branch: feature/{{card}}-{spec['slug']}",
                "See harness-v6-plan.md for file list",
            ],
        }
    )


def epic_html(child_lines: list[str]) -> str:
    return build_plan_html(
        {
            "task_name": EPIC_TITLE,
            "story": [
                "Deliver Harness v6: deterministic gates, execution ledger, "
                "and operational learning loop (no LLM training).",
            ],
            "scope": [
                "Five-layer architecture: Harness, Ledger, Learning, Optimization, Governance",
                "Caveman inter-agent communication law",
                "SDLC-only cleanup (exclude studio/ and app/)",
            ],
            "non_goals": [
                "No app/ or studio/ changes in this epic",
                "No neural RL or model fine-tuning",
                "No local specs/ folder",
            ],
            "assumptions": [
                "Plane project RPG workspace rpg",
                "develop branch baseline",
            ],
            "risks": [
                "Duplicate stores if ledger and learning not unified",
                "Gate strict may friction agents until habit formed",
            ],
            "impacted_areas": [".sdlc/", ".cursor/rules/", ".cursor/hooks/", ".cursor/skills/"],
            "acceptance_criteria": [
                "All five child cards Done",
                "Learning loop records task events and computes reward",
                "Policy memory suggests strategy hints in observe mode",
                "SDLC cleanup complete per child 5",
                "make sdlc-doctor and learning pytest green",
            ],
            "definition_of_done": [
                "Epic Done when all children merged to develop",
                "harness-v6-plan.md status COMPLETE",
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

    # Refresh epic description with real card IDs
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
