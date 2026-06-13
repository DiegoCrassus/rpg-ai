#!/usr/bin/env python3
"""Create Harness v7 epic and child cards on Plane (idempotent)."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from board_client import board_api, format_card  # noqa: E402
from plane_html import build_plan_html  # noqa: E402

EPIC_TITLE = "[AI][EPIC] Harness v7 — Manifest observability + structure slim"

CHILDREN = [
    {
        "title": "[AI][SDLC] Runtime manifest + sdlc_obs restore",
        "slug": "runtime-manifest-obs",
        "story": "Manifest-aligned observability index and working sdlc_obs package for Studio.",
        "scope": [
            ".sdlc/runtime/manifest.yaml + README",
            "app/infra/sdlc_obs/ (store, collector, hooks, auditor)",
            "sdlc.yaml runtime module + catalog reading_order",
        ],
        "ac": [
            "python app/infra/sdlc_obs/auditor.py exits 0",
            "make obs-init initializes SQLite",
            "Studio test_obs.py green",
        ],
    },
    {
        "title": "[AI][SDLC] Studio compiler lifecycle-model SoT",
        "slug": "studio-lifecycle-sot",
        "story": "Studio compiler and pipeline metadata read lifecycle-model.yaml.",
        "scope": [
            "compiler_core.py REQUIRED_SOURCE_PATHS",
            "pipeline_metadata.py write_policy from model",
            "workflow_builder_canvas source refs",
        ],
        "ac": [
            "test_compiler_core.py green",
            "pipeline metadata source_refs include lifecycle-model",
            "No gates/paths in compiler required paths",
        ],
    },
    {
        "title": "[AI][SDLC] Shim generation + L1 drift fix",
        "slug": "shim-sync-drift",
        "story": "Generated shims, doc drift fixes, registry SoT updates.",
        "scope": [
            "sdlc_sync_model.py --write",
            "change-lifecycle.md investiments → RPG",
            "integrations/README, scripts/README",
            "registry lifecycle_model + runtime.manifest artifacts",
        ],
        "ac": [
            "sdlc_sync_model check OK",
            "make sdlc-doctor exit 0",
            "Generated gates/paths.yaml header AUTO-GENERATED",
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
            "non_goals": ["No neural RL", "P2 items deferred to follow-up epic"],
            "assumptions": [
                f"Parent epic: {epic_card}",
                "Authority: .sdlc/process/harness-v7-change-plan.md",
            ],
            "risks": ["Studio frontend still uses INVES-* placeholders in tests/UI"],
            "impacted_areas": [".sdlc/runtime/", "app/infra/sdlc_obs/", "studio/engine/"],
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
            "story": [
                "Harness v7: manifest observability, sdlc_obs restore, lifecycle-model SoT, generated shims.",
            ],
            "scope": [
                "runtime/manifest.yaml index",
                "Studio compiler aligned to lifecycle-model",
                "Generated shims + L1 drift fixes",
            ],
            "non_goals": [
                "P2: pipeline→catalog merge",
                "P2: orchestrator learning hints",
                "Studio INVES-* UI rename (separate card)",
            ],
            "assumptions": ["Plane project RPG workspace rpg", "develop baseline"],
            "risks": ["Obs DB empty until hooks run in real sessions"],
            "impacted_areas": [".sdlc/", "app/infra/sdlc_obs/", "studio/"],
            "acceptance_criteria": [
                "All three child cards Done",
                "Doctor 0 failures",
                "22+ tests green including test_obs",
            ],
            "definition_of_done": [
                "Epic Done when children merged to develop",
                "harness-v7-change-plan.md status APPLIED",
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
