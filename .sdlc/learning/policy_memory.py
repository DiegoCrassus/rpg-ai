"""Policy memory — distilled lessons from reward history."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

try:
    from .event_store import events_for_card, read_events
    from .schemas import SDLCRunEvent
except ImportError:
    from event_store import events_for_card, read_events  # type: ignore[no-redef]
    from schemas import SDLCRunEvent  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = ROOT / ".sdlc" / "learning" / "policy_memory.yaml"


def policy_path(root: Path | None = None) -> Path:
    return (root or ROOT) / ".sdlc" / "learning" / "policy_memory.yaml"


def load(root: Path | None = None) -> dict[str, Any]:
    path = policy_path(root)
    if yaml is None or not path.is_file():
        return {"version": "1.0", "rules": [], "hints": {}}
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    data.setdefault("version", "1.0")
    data.setdefault("rules", [])
    data.setdefault("hints", {})
    return data


def save(data: dict[str, Any], root: Path | None = None) -> Path:
    if yaml is None:
        raise RuntimeError("PyYAML required for policy_memory")
    path = policy_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
    return path


def update_from_events(events: list[SDLCRunEvent], root: Path | None = None) -> dict[str, Any]:
    data = load(root)
    rules: list[dict[str, Any]] = list(data.get("rules") or [])

    by_agent: Counter[str] = Counter()
    low_reward: Counter[str] = Counter()
    for e in events:
        key = f"{e.task_type}:{e.agent}:{e.stage}"
        by_agent[key] += 1
        if e.reward < 0.5:
            low_reward[key] += 1

    for key, count in low_reward.items():
        if count < 2:
            continue
        task_type, agent, stage = key.split(":", 2)
        rule_id = f"low-reward-{task_type}-{agent}-{stage}"
        rule = {
            "id": rule_id,
            "when": {"task_type": task_type, "agent": agent, "stage": stage},
            "suggest": {
                "human_review": True,
                "detailed_prompt": True,
                "run_tests_before_handoff": stage == "validation",
            },
            "evidence_count": count,
            "avg_context": "historical low reward cluster",
        }
        existing = next((r for r in rules if r.get("id") == rule_id), None)
        if existing:
            existing.update(rule)
        else:
            rules.append(rule)

    # Static seed rules (spec examples)
    seeds = [
        {
            "id": "auth-security-agent",
            "when": {"scope_keyword": "auth"},
            "suggest": {"agents": ["security-scanner", "reviewer"], "human_review": True},
            "evidence_count": 0,
        },
        {
            "id": "small-bugfix-python",
            "when": {"task_type": "bugfix", "language": "python"},
            "suggest": {"model_tier": "fast", "context": "reduced"},
            "evidence_count": 0,
        },
        {
            "id": "large-feature-plan-first",
            "when": {"task_type": "feature", "scope": "large"},
            "suggest": {"agents_before_code": ["planner", "architect"]},
            "evidence_count": 0,
        },
    ]
    for seed in seeds:
        if not any(r.get("id") == seed["id"] for r in rules):
            rules.append(seed)

    hints = dict(data.get("hints") or {})
    if events:
        avg = sum(e.reward for e in events[-50:]) / min(len(events), 50)
        hints["rolling_avg_reward_50"] = round(avg, 3)
        hints["last_updated"] = events[-1].ts

    data["rules"] = rules
    data["hints"] = hints
    save(data, root)
    return data


def update_for_card(card: str, root: Path | None = None) -> dict[str, Any]:
    return update_from_events(events_for_card(card, root=root) or read_events(), root=root)


def hints_for_spawn(*, task_type: str, stage: str, agent: str, root: Path | None = None) -> dict[str, Any]:
    data = load(root)
    matched: dict[str, Any] = {}
    for rule in data.get("rules") or []:
        when = rule.get("when") or {}
        if when.get("task_type") and when["task_type"] != task_type:
            continue
        if when.get("stage") and when["stage"] != stage:
            continue
        if when.get("agent") and when["agent"] != agent:
            continue
        matched.update(rule.get("suggest") or {})
    matched.update(data.get("hints") or {})
    return matched
