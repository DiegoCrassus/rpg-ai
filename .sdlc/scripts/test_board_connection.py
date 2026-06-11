#!/usr/bin/env python3
"""Smoke test board (Plane) API connectivity — no secrets printed."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".sdlc" / "scripts"))
sys.path.insert(0, str(ROOT / ".sdlc" / "dsl"))

from board_client import board_api, format_card  # noqa: E402
from core_config import board, card_prefix  # noqa: E402


def main() -> int:
    try:
        api_key, workspace, project_id = board_api()
    except SystemExit as exc:
        print(f"FAIL: config — {exc}")
        return 1

    cfg = board(ROOT)
    print("config from sdlc.yaml:")
    print(f"  card_prefix: {card_prefix(ROOT)}")
    print(f"  workspace (yaml): {cfg.get('workspace')}")
    print(f"  project_id (yaml): {cfg.get('project_id')}")
    print("runtime (env overrides when set):")
    print(f"  workspace: {workspace}")
    print(f"  project_id: {project_id}")

    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    with httpx.Client(timeout=30.0) as client:
        wr = client.get(f"https://api.plane.so/api/v1/workspaces/{workspace}/", headers=headers)
        print(f"workspace GET: {wr.status_code} {wr.reason_phrase}")
        if wr.status_code != 200:
            print(wr.text[:400])
            return 1
        wdata = wr.json()
        print(f"  workspace name: {wdata.get('name') or wdata.get('slug')}")

        pr = client.get(
            f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/{project_id}/",
            headers=headers,
        )
        print(f"project GET: {pr.status_code} {pr.reason_phrase}")
        if pr.status_code != 200:
            print(pr.text[:400])
            return 1
        pdata = pr.json()
        print(f"  project name: {pdata.get('name')}")
        print(f"  identifier: {pdata.get('identifier')}")

        ir = client.get(
            f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/{project_id}/issues/",
            headers=headers,
            params={"per_page": 5},
        )
        print(f"issues GET: {ir.status_code} {ir.reason_phrase}")
        if ir.status_code != 200:
            print(ir.text[:400])
            return 1
        results = ir.json().get("results") or []
        print(f"  issues on first page: {len(results)}")
        for item in results:
            seq = item.get("sequence_id")
            label = format_card(seq) if seq else "?"
            name = (item.get("name") or "")[:70]
            print(f"    {label}: {name}")

    yaml_id = str(cfg.get("project_id") or "")
    if yaml_id and yaml_id != project_id:
        print("WARN: BOARD_PROJECT_ID in .env differs from sdlc.yaml — update sdlc.yaml to match")

    yaml_ws = str(cfg.get("workspace") or "")
    if yaml_ws.lower() != workspace.lower():
        print(f"WARN: workspace slug .env ({workspace}) != sdlc.yaml ({yaml_ws})")

    print("RESULT: board connection OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
