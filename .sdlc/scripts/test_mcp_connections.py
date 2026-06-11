#!/usr/bin/env python3
"""Smoke test repository (GitHub) + board (Plane) connectivity from .env."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".sdlc" / "scripts"))
sys.path.insert(0, str(ROOT / ".sdlc" / "dsl"))

from board_client import board_api, format_card, repository_api, repository_api_base  # noqa: E402
from core_config import board, card_prefix, repository  # noqa: E402


def test_repository() -> bool:
    print("=== Repository (GitHub) ===")
    try:
        token, slug = repository_api()
    except SystemExit as exc:
        print(f"FAIL: config — {exc}")
        return False

    repo_cfg = repository(ROOT)
    print(f"  slug: {slug}")
    print(f"  host: {repo_cfg.get('host', 'github.com')}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    base = repository_api_base()

    ok = True
    with httpx.Client(timeout=30.0) as client:
        me = client.get(f"{base}/user", headers=headers)
        print(f"  GET /user: {me.status_code} {me.reason_phrase}")
        if me.status_code != 200:
            print(f"    {me.text[:300]}")
            ok = False
        else:
            data = me.json()
            print(f"    login: {data.get('login')}")

        if "/" in slug:
            repo = client.get(f"{base}/repos/{slug}", headers=headers)
            print(f"  GET /repos/{slug}: {repo.status_code} {repo.reason_phrase}")
            if repo.status_code != 200:
                print(f"    {repo.text[:300]}")
                ok = False
            else:
                rdata = repo.json()
                print(f"    name: {rdata.get('full_name')}")
                print(f"    default_branch: {rdata.get('default_branch')}")
                print(f"    private: {rdata.get('private')}")

    print("  RESULT:", "OK" if ok else "FAIL")
    return ok


def test_board() -> bool:
    print("\n=== Board (Plane) ===")
    try:
        api_key, workspace, project_id = board_api()
    except SystemExit as exc:
        print(f"FAIL: config — {exc}")
        return False

    cfg = board(ROOT)
    print(f"  card_prefix: {card_prefix(ROOT)}")
    print(f"  workspace (env): {workspace}")
    print(f"  project_id (env): {project_id}")
    yaml_ws = cfg.get("workspace")
    yaml_pid = cfg.get("project_id")
    if yaml_ws and str(yaml_ws).lower() != workspace.lower():
        print(f"  WARN: sdlc.yaml workspace={yaml_ws} differs from .env")
    if yaml_pid and str(yaml_pid) != project_id:
        print("  WARN: sdlc.yaml project_id differs from BOARD_PROJECT_ID in .env")

    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    ok = True

    with httpx.Client(timeout=30.0) as client:
        me = client.get("https://api.plane.so/api/v1/users/me/", headers=headers)
        print(f"  GET /users/me: {me.status_code} {me.reason_phrase}")
        if me.status_code != 200:
            print(f"    {me.text[:300]}")
            ok = False
        else:
            u = me.json()
            print(f"    email: {u.get('email', '(hidden)')}")

        ws = client.get(f"https://api.plane.so/api/v1/workspaces/{workspace}/", headers=headers)
        print(f"  GET /workspaces/{workspace}: {ws.status_code} {ws.reason_phrase}")
        if ws.status_code != 200:
            print(f"    {ws.text[:300]}")
            ok = False
        else:
            w = ws.json()
            print(f"    name: {w.get('name') or w.get('slug')}")

        pr = client.get(
            f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/{project_id}/",
            headers=headers,
        )
        print(f"  GET /projects/{project_id[:8]}…: {pr.status_code} {pr.reason_phrase}")
        if pr.status_code != 200:
            print(f"    {pr.text[:300]}")
            ok = False
        else:
            p = pr.json()
            print(f"    project: {p.get('name')}")
            print(f"    identifier: {p.get('identifier')}")

        ir = client.get(
            f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/{project_id}/issues/",
            headers=headers,
            params={"per_page": 3},
        )
        print(f"  GET /issues: {ir.status_code} {ir.reason_phrase}")
        if ir.status_code != 200:
            print(f"    {ir.text[:300]}")
            ok = False
        else:
            items = ir.json().get("results") or []
            print(f"    sample ({len(items)} cards):")
            for item in items:
                seq = item.get("sequence_id")
                label = format_card(seq) if seq else "?"
                print(f"      {label}: {(item.get('name') or '')[:60]}")

    print("  RESULT:", "OK" if ok else "FAIL")
    return ok


def main() -> int:
    repo_ok = test_repository()
    board_ok = test_board()
    print("\n=== Summary ===")
    print(f"  GitHub: {'OK' if repo_ok else 'FAIL'}")
    print(f"  Plane:  {'OK' if board_ok else 'FAIL'}")
    return 0 if repo_ok and board_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
