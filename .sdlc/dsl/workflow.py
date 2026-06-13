"""SDLC workflow meta-tool — classify, plan, arch, start, implement, validate, review, finish, status."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from gate import (  # type: ignore[import-not-found]
    close_gate,
    gate_status_text,
    load_session_gate,
    open_gate,
    repo_root,
    save_session_gate,
)

ROOT = repo_root()

GREENFIELD_WORDS = (
    "do zero",
    "greenfield",
    "não reaproveite",
    "nao reaproveite",
    "repense",
    "from scratch",
    "rethought",
)

READONLY_WORDS = (
    "como funciona",
    "explique",
    "analise",
    "analyze",
    "what is",
    "qual é",
    "?",
)

SDLC_META_PREFIXES = (".sdlc/", ".cursor/", ".github/workflows/")


def _app_is_placeholder() -> bool:
    backend = ROOT / "app" / "backend"
    frontend = ROOT / "app" / "frontend"
    backend_files = [p for p in backend.rglob("*") if p.is_file() and p.name != "README.md"]
    frontend_files = [p for p in frontend.rglob("*") if p.is_file() and p.name != "README.md"]
    return len(backend_files) == 0 and len(frontend_files) == 0


def classify_intent(text: str = "") -> dict[str, Any]:
    empty_app = _app_is_placeholder()
    from intent_rules import classify_from_rules  # noqa: E402

    ruled = classify_from_rules(text, root=ROOT, empty_app=empty_app)
    if ruled is not None:
        return ruled

    t = (text or "").lower()
    greenfield_words = any(w in t for w in GREENFIELD_WORDS)

    if not text.strip():
        intent = "READONLY"
    elif any(w in t for w in ("sdlc", "orchestrator", "gate", "workflow", "doctor")) and any(
        w in t for w in (".sdlc", ".cursor", "master-workflow")
    ):
        intent = "SDLC_META"
    elif greenfield_words and empty_app:
        intent = "GREENFIELD"
    elif greenfield_words:
        intent = "GREENFIELD"
    elif any(w in t for w in ("bugfix", "corrigir bug", "fix bug")):
        intent = "BUGFIX"
    elif any(w in t for w in ("hotfix", "urgência produção")):
        intent = "HOTFIX"
    elif any(w in t for w in ("infra", "ci/cd", "terraform", "docker")):
        intent = "INFRA"
    elif any(w in t for w in ("docs only", "só docs", "documentação")):
        intent = "DOCS_ONLY"
    elif t.strip().endswith("?") or any(w in t for w in READONLY_WORDS):
        intent = "READONLY"
    else:
        intent = "FEATURE"

    requires_plane = intent not in ("READONLY",)
    requires_branch = intent in (
        "GREENFIELD",
        "FEATURE",
        "BUGFIX",
        "HOTFIX",
        "INFRA",
        "SDLC_META",
        "DOCS_ONLY",
    )

    next_agent = {
        "READONLY": "none",
        "SDLC_META": "planner",
        "DOCS_ONLY": "planner",
        "GREENFIELD": "planner",
        "FEATURE": "planner",
        "BUGFIX": "planner",
        "HOTFIX": "planner",
        "INFRA": "architect",
    }.get(intent, "planner")

    signals = []
    if greenfield_words:
        signals.append("user_words")
    if empty_app:
        signals.append("empty_app")

    return {
        "intent": intent,
        "confidence": 0.85 if intent != "FEATURE" else 0.7,
        "greenfield_signals": signals,
        "scope_hint": text[:200] if text else "",
        "requires_plane": requires_plane,
        "requires_branch": requires_branch,
        "next_agent": next_agent,
        "rationale": f"classified as {intent}",
    }


def _yes_no(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def write_handoff(classification: dict[str, Any]) -> Path:
    """Write orchestrator handoff as Markdown (see .sdlc/memory/README.md)."""
    path = ROOT / ".sdlc" / "memory" / "orchestrator-handoff.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    intent = classification.get("intent", "")
    confidence = classification.get("confidence", "")
    next_agent = classification.get("next_agent", "")
    scope_hint = classification.get("scope_hint", "")
    rationale = classification.get("rationale", "")
    signals = classification.get("greenfield_signals") or []
    signals_text = ", ".join(signals) if signals else "none"

    body = f"""# Orchestrator Handoff (latest)

## Routing

| Field | Value |
|-------|-------|
| **Next agent** | {next_agent} |
| **Stage complete** | yes |
| **Previous agent** | workflow-classify |

## Classification

| Field | Value |
|-------|-------|
| **Intent** | {intent} |
| **Confidence** | {confidence} |
| **Requires Plane** | {_yes_no(classification.get("requires_plane", False))} |
| **Requires branch** | {_yes_no(classification.get("requires_branch", False))} |
| **Greenfield signals** | {signals_text} |

## Session

| Field | Value |
|-------|-------|
| **Card** | — |
| **Epic** | — |
| **Branch** | — |
| **Stage** | — |

## Scope

{scope_hint or "—"}

## Rationale

{rationale or "—"}

## Blockers

- none
"""
    path.write_text(body, encoding="utf-8")
    return path


def update_session_intent(classification: dict[str, Any]) -> None:
    state = load_session_gate()
    state.intent = classification.get("intent", "")
    save_session_gate(state)


def cmd_classify(args: argparse.Namespace) -> int:
    text = args.text or ""
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    result = classify_intent(text)
    write_handoff(result)
    update_session_intent(result)
    print(json.dumps(result, indent=2))
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    if not args.card:
        print("ERROR: --card RPG-N required", file=sys.stderr)
        return 1
    script = ROOT / ".sdlc" / "scripts" / "plane_card.py"
    proc = subprocess.run(
        [sys.executable, str(script), "validate-all", "--card", args.card],
        cwd=ROOT,
    )
    return proc.returncode


def cmd_discover(_args: argparse.Namespace) -> int:
    script = ROOT / ".sdlc" / "scripts" / "discovery_hook.py"
    return subprocess.run([sys.executable, str(script)], cwd=ROOT).returncode


def cmd_arch(args: argparse.Namespace) -> int:
    state = load_session_gate()
    if state.gate_status != "open":
        print("WARN: gate not open — architecture stage should follow validated plan")
    if not args.card and state.card:
        args.card = state.card
    if args.card:
        return cmd_plan(args)
    print("ERROR: no card — pass --card RPG-N", file=sys.stderr)
    return 1


def cmd_start(args: argparse.Namespace) -> int:
    from break_glass import require_break_glass  # noqa: E402

    card = args.card
    if not card:
        print("ERROR: --card RPG-N required", file=sys.stderr)
        return 1

    if args.force and not require_break_glass("--force"):
        return 1
    if args.skip_plane and not require_break_glass("--skip-plane"):
        return 1
    if args.skip_validate and not require_break_glass("--skip-validate"):
        return 1

    # Block workflow start on epic — use child implementable card
    try:
        sys.path.insert(0, str(ROOT / ".sdlc" / "scripts"))
        from plane_card import _api, find_issue_uuid, get_issue, parse_card  # noqa: E402

        api_key, workspace, project_id = _api()
        seq = parse_card(card)
        uuid = find_issue_uuid(api_key, workspace, project_id, seq)
        issue = get_issue(api_key, workspace, project_id, uuid)
        title = (issue.get("name") or "").upper()
        if "[AI][EPIC]" in title:
            print(
                "ERROR: cannot workflow start on EPIC card — use a child card "
                "(BACKEND/FRONTEND/INFRA)",
                file=sys.stderr,
            )
            return 1
    except SystemExit:
        raise
    except Exception as exc:
        if not args.force:
            print(f"ERROR: could not verify epic/child (Plane API): {exc}", file=sys.stderr)
            return 1
        print(f"WARN: could not verify epic/child: {exc}", file=sys.stderr)

    stage = args.stage or "implementation"
    branch = args.branch or f"feature/{card}-{args.slug or 'work'}"

    if not args.skip_plane:
        plane_script = ROOT / ".sdlc" / "scripts" / "plane_state.py"
        if plane_script.is_file():
            proc = subprocess.run(
                [
                    sys.executable,
                    str(plane_script),
                    "in-progress",
                    "--card",
                    card,
                    "--branch",
                    branch,
                ],
                cwd=ROOT,
            )
            if proc.returncode != 0 and not args.force:
                print("ERROR: plane_state in-progress failed — gate stays closed", file=sys.stderr)
                return proc.returncode

    if not args.skip_validate and stage != "sdlc_meta":
        plan_rc = cmd_plan(argparse.Namespace(card=card))
        if plan_rc != 0 and not args.force:
            print("ERROR: validate-plan failed — fix Plane description or use --force", file=sys.stderr)
            return plan_rc

    prior = load_session_gate()
    from transition_check import transition_allowed  # noqa: E402

    prev_stage = prior.stage if prior.gate_status == "open" else (prior.meta or {}).get("last_gate_stage", "")
    allowed, msg = transition_allowed(prev_stage, stage, root=ROOT)
    if not allowed and not args.force:
        print(f"ERROR: {msg}", file=sys.stderr)
        return 1
    if not allowed and args.force:
        print(f"WARN: {msg}", file=sys.stderr)

    intent = args.intent or prior.intent or "FEATURE"
    state = open_gate(card=card, branch=branch, stage=stage, intent=intent)
    state.meta["last_gate_stage"] = stage
    save_session_gate(state)
    print(f"OK: workflow start — {card} branch={branch} stage={stage}")
    return 0


def cmd_implement(args: argparse.Namespace) -> int:
    state = load_session_gate()
    if state.gate_status != "open":
        print("ERROR: gate closed — run workflow start first", file=sys.stderr)
        return 1
    if state.stage not in ("implementation", "validation", "sdlc_meta"):
        print(f"ERROR: stage '{state.stage}' does not allow implementation writes", file=sys.stderr)
        return 1
    print(f"OK: implementation gate ready — {state.card} stage={state.stage}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    state = load_session_gate()
    if state.gate_status == "open" and state.stage == "implementation":
        open_gate(
            card=state.card,
            branch=state.branch,
            stage="validation",
            intent=state.intent,
        )
    proc = subprocess.run(["make", "sdlc-doctor"], cwd=ROOT)
    return proc.returncode


def cmd_review(args: argparse.Namespace) -> int:
    state = load_session_gate()
    if state.gate_status != "open":
        print("WARN: gate closed during review prep")
    print(f"OK: review gate prep — card={state.card or args.card or '(none)'}")
    return 0


def _ledger_snapshot(card: str) -> None:
    if not card:
        return
    script = ROOT / ".sdlc" / "scripts" / "execution_ledger.py"
    if script.is_file():
        subprocess.run(
            [sys.executable, str(script), "snapshot", "--card", card],
            cwd=ROOT,
            capture_output=True,
        )
    policy = ROOT / ".sdlc" / "scripts" / "learning_loop.py"
    if policy.is_file():
        subprocess.run(
            [sys.executable, str(policy), "policy-update", "--card", card],
            cwd=ROOT,
            capture_output=True,
        )


def cmd_finish(args: argparse.Namespace) -> int:
    card = args.card or load_session_gate().card
    if args.pr and card:
        merge = ROOT / ".sdlc" / "scripts" / "auto_merge_pr.py"
        proc = subprocess.run(
            [sys.executable, str(merge), "--pr", str(args.pr), "--card", card, "--plane-comment"],
            cwd=ROOT,
        )
        _ledger_snapshot(card)
        close_gate()
        return proc.returncode
    if card:
        _ledger_snapshot(card)
    close_gate()
    print("OK: gate closed" + (" — merge skipped (no --pr)" if not args.pr else ""))
    return 0


def cmd_status(_args: argparse.Namespace) -> int:
    print(gate_status_text())
    handoff = ROOT / ".sdlc" / "memory" / "orchestrator-handoff.md"
    if handoff.is_file():
        print("\n--- handoff ---")
        print(handoff.read_text(encoding="utf-8")[:800])
    return 0


def cmd_gates(args: argparse.Namespace) -> int:
    script = ROOT / ".sdlc" / "scripts" / "sdlc_gate.py"
    cmd = ["enforcement", args.gates_command]
    proc = subprocess.run([sys.executable, str(script), *cmd], cwd=ROOT)
    return proc.returncode


def run_workflow(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="workflow")
    sub = parser.add_subparsers(dest="wf_command", required=True)

    c = sub.add_parser("classify")
    c.add_argument("--text", default="")
    c.add_argument("--file", default="")

    p = sub.add_parser("plan")
    p.add_argument("--card", required=True)

    sub.add_parser("discover", help="Run discovery hook (legacy docs, app state)")

    a = sub.add_parser("arch")
    a.add_argument("--card", default="")

    s = sub.add_parser("start")
    s.add_argument("--card", required=True)
    s.add_argument("--branch", default="")
    s.add_argument("--slug", default="work")
    s.add_argument("--stage", default="implementation")
    s.add_argument("--intent", default="")
    s.add_argument("--skip-plane", action="store_true")
    s.add_argument("--skip-validate", action="store_true")
    s.add_argument("--force", action="store_true")

    sub.add_parser("implement")
    sub.add_parser("validate")
    sub.add_parser("review")
    f = sub.add_parser("finish")
    f.add_argument("--card", default="")
    f.add_argument("--pr", default="")
    sub.add_parser("status")

    g = sub.add_parser("gates", help="Show or change write-gate enforcement (core.gates in sdlc.yaml)")
    g_sub = g.add_subparsers(dest="gates_command", required=True)
    g_sub.add_parser("status", help="Show enforcement mode")
    g_sub.add_parser("off", help="Disable write-gate checks for structural repo work")
    g_sub.add_parser("strict", help="Re-enable write-gate checks")

    args = parser.parse_args(argv)
    handlers = {
        "classify": cmd_classify,
        "discover": cmd_discover,
        "plan": cmd_plan,
        "arch": cmd_arch,
        "start": cmd_start,
        "implement": cmd_implement,
        "validate": cmd_validate,
        "review": cmd_review,
        "finish": cmd_finish,
        "status": cmd_status,
        "gates": cmd_gates,
    }
    return handlers[args.wf_command](args)
