#!/usr/bin/env python3
"""Triage open GitHub issues — close superseded or delegate via comment.

Primary tracker is Plane (RPG-N). Legacy issues referencing specs/ or
INVESTIMENTS-N without Plane linkage are closed with redirect.

Usage:
  python3 .sdlc/scripts/github_issue_triage.py --dry-run
  python3 .sdlc/scripts/github_issue_triage.py --close-superseded
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
GITHUB_API = "https://api.github.com"

# Known supersession map from Investment Radar MVP delivery (Plane INVES-*)
SUPERSEDED = {
    25: {
        "plane": "RPG-20",
        "pr": 32,
        "reason": "FastAPI foundation delivered via Plane workflow and PR #32 (market data includes app bootstrap).",
    },
    26: {
        "plane": "RPG-20",
        "pr": 32,
        "reason": "Market data with fallback delivered in RPG-20 / PR #32.",
    },
    27: {
        "plane": "RPG-21, RPG-22",
        "pr": "33, 34",
        "reason": "Watchlist and simulated portfolio APIs delivered (RPG-21 #33, RPG-22 #34). Alerts were out of MVP scope.",
    },
    28: {
        "plane": "RPG-23",
        "pr": 35,
        "reason": "React+Vite frontend shell delivered in RPG-23 / PR #35.",
    },
    29: {
        "plane": "RPG-23",
        "pr": 35,
        "reason": "Discover/search views included in RPG-23 frontend / PR #35.",
    },
    30: {
        "plane": "RPG-23",
        "pr": 35,
        "reason": "Portfolio and watchlist UI delivered in RPG-23 / PR #35. Alert UI was out of MVP scope.",
    },
    31: {
        "plane": "RPG-24",
        "pr": 36,
        "reason": "Run documentation delivered in RPG-24 / PR #36.",
    },
}

TRIAGE_COMMENT = """## Triagem — Issue Analyst (automated)

**Classificação:** `Duplicada` / superseded  
**Fonte da verdade:** Plane project `investiments` — cards `RPG-N`  
**Motivo:** Esta issue referencia o fluxo legado (`specs/`, `INVESTIMENTS-N`). O trabalho foi replanejado e entregue via SDLC Plane-first.

**Entrega Plane:** {plane}  
**PR(s):** {pr_links}  
**Detalhe:** {reason}

### Próximos passos
- Novo trabalho → criar card no Plane via `plane-task-creation`, **não** GitHub Issue
- Scope residual (ex.: alerts) → novo card `[AI][TYPE]` no Plane se ainda for necessário

---
*Triagem automática · sdlc-ai · Issue Analyst policy*
"""


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def _token_repo() -> tuple[str, str]:
    _load_dotenv()
    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC") or os.environ.get(
        "GITHUB_PERSONAL_ACCESS_TOKEN"
    )
    repo = os.environ.get("GITHUB_REPOSITORY", "DiegoCrassus/sdlc-ai")
    if not token:
        sys.exit("ERROR: GitHub token required")
    return token, repo


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}


def list_open_issues(token: str, repo: str) -> list[dict]:
    url = f"{GITHUB_API}/repos/{repo}/issues"
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=_headers(token), params={"state": "open", "per_page": 50})
        resp.raise_for_status()
        return [i for i in resp.json() if "pull_request" not in i]


def pr_links(pr_field) -> str:
    if isinstance(pr_field, int):
        return f"https://github.com/DiegoCrassus/sdlc-ai/pull/{pr_field}"
    parts = [p.strip() for p in str(pr_field).split(",")]
    return ", ".join(f"https://github.com/DiegoCrassus/sdlc-ai/pull/{p}" for p in parts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--close-superseded", action="store_true")
    args = parser.parse_args()
    token, repo = _token_repo()

    issues = list_open_issues(token, repo)
    print(f"Open issues (non-PR): {len(issues)}")

    for issue in issues:
        num = issue["number"]
        if num not in SUPERSEDED:
            print(f"  #{num}: OPEN — needs Issue Analyst delegation (not in superseded map)")
            continue
        meta = SUPERSEDED[num]
        body = TRIAGE_COMMENT.format(
            plane=meta["plane"],
            pr_links=pr_links(meta["pr"]),
            reason=meta["reason"],
        )
        print(f"  #{num}: superseded -> {meta['plane']}")
        if args.dry_run:
            continue
        if not args.close_superseded:
            continue
        base = f"{GITHUB_API}/repos/{repo}/issues/{num}"
        with httpx.Client(timeout=30.0) as client:
            client.post(f"{base}/comments", headers=_headers(token), json={"body": body})
            client.patch(
                f"{base}",
                headers=_headers(token),
                json={"state": "closed", "state_reason": "not_planned"},
            )
        print(f"    closed #{num}")


if __name__ == "__main__":
    main()
