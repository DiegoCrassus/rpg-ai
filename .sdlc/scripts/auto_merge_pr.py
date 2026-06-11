#!/usr/bin/env python3
"""Autonomous squash-merge of a PR into develop when CI and review gates pass.

Requires green check-runs on the PR head SHA and an APPROVED review (GitHub or
handoff from Reviewer). See auto-merge-policy.md.

Usage:
  python3 .sdlc/scripts/auto_merge_pr.py --pr 32
  python3 .sdlc/scripts/auto_merge_pr.py --branch feature/RPG-20-market-data
  python3 .sdlc/scripts/auto_merge_pr.py --pr 32 --card RPG-20 --plane-comment
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = Path(__file__).resolve().parent
DSL = ROOT / ".sdlc" / "dsl"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
if str(DSL) not in sys.path:
    sys.path.insert(0, str(DSL))

from board_client import card_re, repository_api, repository_api_base  # noqa: E402

HANDOFF_PATH = ROOT / ".sdlc" / "memory" / "orchestrator-handoff.md"

REQUIRED_CHECK_NAMES = frozenset(
    {
        "SDLC Doctor",
        "Secrets Scan (gitleaks)",
        "Studio E2E (smoke + builder)",
        "SDLC Pytest",
        "SDLC Validate",
    }
)

FAIL_CONCLUSIONS = frozenset({"failure", "cancelled", "timed_out", "action_required"})


def _repository_credentials() -> tuple[str, str]:
    return repository_api()


def _gh_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _require_break_glass(flag_name: str) -> bool:
    sys.path.insert(0, str(ROOT / ".sdlc" / "dsl"))
    from break_glass import require_break_glass  # noqa: E402

    return require_break_glass(flag_name)


def find_pr_by_branch(token: str, repo: str, branch: str) -> int:
    owner, name = repo.split("/", 1)
    url = f"{repository_api_base()}/repos/{repo}/pulls"
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(
            url,
            headers=_gh_headers(token),
            params={"head": f"{owner}:{branch}", "state": "open", "base": "develop"},
        )
        resp.raise_for_status()
        pulls = resp.json()
        if not pulls:
            print(f"ERROR: no open PR for branch {branch}", file=sys.stderr)
            sys.exit(1)
        return pulls[0]["number"]


def get_pr(token: str, repo: str, pr_number: int) -> dict:
    url = f"{repository_api_base()}/repos/{repo}/pulls/{pr_number}"
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=_gh_headers(token))
        resp.raise_for_status()
        return resp.json()


def _fetch_check_runs(token: str, repo: str, sha: str) -> list[dict]:
    url = f"{repository_api_base()}/repos/{repo}/commits/{sha}/check-runs"
    runs: list[dict] = []
    page = 1
    with httpx.Client(timeout=30.0) as client:
        while True:
            resp = client.get(
                url,
                headers=_gh_headers(token),
                params={"per_page": 100, "page": page},
            )
            resp.raise_for_status()
            data = resp.json()
            runs.extend(data.get("check_runs") or [])
            if page >= (data.get("total_count", 0) // 100) + 1:
                break
            if not data.get("check_runs"):
                break
            page += 1
    return runs


def wait_for_checks_at_head(
    token: str,
    repo: str,
    sha: str,
    timeout_sec: int,
    poll_sec: int,
) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        runs = _fetch_check_runs(token, repo, sha)
        if not runs:
            print(f"CI: no check-runs yet for {sha[:7]}…")
            time.sleep(poll_sec)
            continue

        by_name: dict[str, dict] = {}
        pending = 0
        for run in runs:
            name = run.get("name") or ""
            by_name[name] = run
            status = run.get("status")
            conclusion = run.get("conclusion")
            print(f"CI: {name} status={status} conclusion={conclusion}")
            if status != "completed":
                pending += 1
            elif conclusion in FAIL_CONCLUSIONS:
                print(f"ERROR: check failed — {name} ({conclusion})", file=sys.stderr)
                return False

        if pending:
            time.sleep(poll_sec)
            continue

        missing = REQUIRED_CHECK_NAMES - set(by_name)
        if missing:
            print(f"CI: waiting for required checks: {', '.join(sorted(missing))}")
            time.sleep(poll_sec)
            continue

        for name in REQUIRED_CHECK_NAMES:
            run = by_name[name]
            if run.get("conclusion") not in ("success", "skipped"):
                print(
                    f"ERROR: required check not green — {name} ({run.get('conclusion')})",
                    file=sys.stderr,
                )
                return False

        print(f"OK: all required checks green on {sha[:7]}")
        return True

    print("ERROR: CI wait timeout", file=sys.stderr)
    return False


def _handoff_reviewer_approved() -> bool:
    if not HANDOFF_PATH.is_file():
        return False
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    row_re = re.compile(r"^\|\s*(?:\*\*)?([^|*]+?)(?:\*\*)?\s*\|\s*([^|]+?)\s*\|$")
    routing: dict[str, str] = {}
    in_routing = False
    for line in text.splitlines():
        if line.startswith("## Routing"):
            in_routing = True
            continue
        if line.startswith("## ") and in_routing:
            break
        if not in_routing:
            continue
        if set(line.strip()) <= {"|", "-", " "}:
            continue
        match = row_re.match(line.strip())
        if match:
            routing[match.group(1).strip().strip("*").lower()] = (
                match.group(2).strip().strip("*").lower()
            )
    previous = routing.get("previous agent", "")
    stage_complete = routing.get("stage complete", "")
    return previous in ("reviewer", "devops") and stage_complete == "yes"


def has_github_review_approval(token: str, repo: str, pr_number: int) -> bool:
    url = f"{repository_api_base()}/repos/{repo}/pulls/{pr_number}/reviews"
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=_gh_headers(token))
        resp.raise_for_status()
        reviews = resp.json()
    for review in reviews:
        if review.get("state") == "APPROVED":
            return True
    return False


def assert_review_gate(token: str, repo: str, pr_number: int) -> None:
    github_ok = has_github_review_approval(token, repo, pr_number)
    handoff_ok = _handoff_reviewer_approved()
    if github_ok or handoff_ok:
        source = "GitHub APPROVED" if github_ok else "handoff Reviewer→DevOps"
        print(f"OK: review gate — {source}")
        return
    print(
        "ERROR: merge blocked — need GitHub review APPROVED or handoff "
        "(Previous agent=reviewer|devops, Stage complete=yes)",
        file=sys.stderr,
    )
    sys.exit(1)


def merge_pr(token: str, repo: str, pr_number: int, title: str | None) -> dict:
    url = f"{repository_api_base()}/repos/{repo}/pulls/{pr_number}/merge"
    body: dict = {"merge_method": "squash"}
    if title:
        body["commit_title"] = title
    with httpx.Client(timeout=60.0) as client:
        resp = client.put(url, headers=_gh_headers(token), json=body)
        if resp.status_code == 405:
            print(f"ERROR: merge not allowed — {resp.json().get('message')}", file=sys.stderr)
            sys.exit(1)
        resp.raise_for_status()
        return resp.json()


def delete_branch(token: str, repo: str, branch: str) -> None:
    if branch in ("develop", "main"):
        return
    url = f"{repository_api_base()}/repos/{repo}/git/refs/heads/{branch}"
    with httpx.Client(timeout=30.0) as client:
        resp = client.delete(url, headers=_gh_headers(token))
        if resp.status_code in (204, 404):
            print(f"OK: branch {branch} deleted (or already gone)")
        else:
            print(f"WARN: could not delete branch {branch}: {resp.status_code}", file=sys.stderr)


def _resolve_evidence_path(card: str, explicit: str | None) -> str | None:
    if explicit and Path(explicit).is_file():
        return explicit
    for candidate in (
        ROOT / ".sdlc" / "memory" / f".evidence-{card.upper()}.json",
        ROOT / ".sdlc" / "memory" / f"qa-evidence-{card.upper()}.json",
        ROOT / ".sdlc" / "templates" / "plane" / f"evidence-{card.upper()}.json",
    ):
        if candidate.is_file():
            return str(candidate)
    return None


def plane_done(card: str, pr_url: str, pr_number: int, evidence_file: str | None = None) -> None:
    import subprocess

    script = ROOT / ".sdlc" / "scripts" / "plane_state.py"
    ev_path = _resolve_evidence_path(card, evidence_file)

    if ev_path:
        data = json.loads(Path(ev_path).read_text(encoding="utf-8"))
        art = data.setdefault("artifacts", {})
        art.setdefault("pr", str(pr_number))
        art.setdefault("pr_url", pr_url)
        tmp = ROOT / ".sdlc/memory/.plane-evidence-tmp.json"
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        subprocess.run(
            [
                sys.executable,
                str(script),
                "done",
                "--card",
                card,
                "--evidence-file",
                str(tmp),
            ],
            check=True,
            cwd=ROOT,
        )
        tmp.unlink(missing_ok=True)
        return

    subprocess.run(
        [
            sys.executable,
            str(script),
            "done",
            "--card",
            card,
            "--comment",
            f"Autonomous merge — PR #{pr_number}: {pr_url}",
        ],
        check=True,
        cwd=ROOT,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous PR squash merge")
    parser.add_argument("--pr", type=int, help="Pull request number")
    parser.add_argument("--branch", help="Head branch name")
    parser.add_argument("--card", help="Plane card RPG-N for Done transition")
    parser.add_argument("--plane-comment", action="store_true", help="Move Plane card to Done")
    parser.add_argument(
        "--evidence-file",
        default="",
        help="Structured JSON evidence for Plane Done comment",
    )
    parser.add_argument("--timeout", type=int, default=600, help="CI wait seconds")
    parser.add_argument("--poll", type=int, default=15, help="CI poll interval")
    parser.add_argument("--skip-ci-wait", action="store_true", help="Merge immediately (dangerous)")
    parser.add_argument(
        "--skip-review-check",
        action="store_true",
        help="Skip GitHub/handoff review gate (requires SDLC_BREAK_GLASS)",
    )
    args = parser.parse_args()

    if args.skip_ci_wait and not _require_break_glass("--skip-ci-wait"):
        sys.exit(1)
    if args.skip_review_check and not _require_break_glass("--skip-review-check"):
        sys.exit(1)

    token, repo = _repository_credentials()
    if not args.pr and not args.branch:
        print("ERROR: provide --pr or --branch", file=sys.stderr)
        sys.exit(1)

    pr_number = args.pr or find_pr_by_branch(token, repo, args.branch)
    pr = get_pr(token, repo, pr_number)
    branch = pr["head"]["ref"]
    head_sha = pr["head"]["sha"]
    pr_url = pr["html_url"]

    if pr.get("merged"):
        print(f"Already merged: {pr_url}")
        if args.plane_comment and args.card:
            plane_done(args.card, pr_url, pr_number, args.evidence_file or None)
        sys.exit(0)

    if pr.get("mergeable") is False and pr.get("mergeable_state") == "dirty":
        print("ERROR: PR has merge conflicts", file=sys.stderr)
        sys.exit(1)

    if not args.skip_review_check:
        assert_review_gate(token, repo, pr_number)

    if not args.skip_ci_wait:
        if not wait_for_checks_at_head(token, repo, head_sha, args.timeout, args.poll):
            print("ERROR: CI not green on PR head — merge blocked", file=sys.stderr)
            sys.exit(1)

    title = pr.get("title")
    result = merge_pr(token, repo, pr_number, title)
    if not result.get("merged"):
        print(f"ERROR: merge failed — {result}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: merged PR #{pr_number} -> develop")
    delete_branch(token, repo, branch)

    if args.card and card_re().match(args.card):
        if args.plane_comment:
            plane_done(args.card, pr_url, pr_number, args.evidence_file or None)
        else:
            print(f"Hint: run plane_state.py done --card {args.card}")


if __name__ == "__main__":
    main()
