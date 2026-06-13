"""Rule-based policy optimizer — observe and suggest (no auto-apply)."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .event_store import read_events
    from .policy_memory import load, update_from_events
except ImportError:
    from event_store import read_events  # type: ignore[no-redef]
    from policy_memory import load, update_from_events  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[2]
PROCEDURES_PATH = ROOT / ".sdlc" / "optimization" / "procedures.yaml"


def analyze(last_n: int = 100, *, min_frequency: int = 3, root: Path | None = None) -> dict[str, Any]:
    events = read_events(root=root)[-last_n:]
    blocks = [e for e in events if e.reward < 0.5]
    by_stage = Counter(f"{e.stage}/{e.agent}" for e in blocks)
    avg_reward = sum(e.reward for e in events) / len(events) if events else 0.0

    suggestions: list[dict[str, Any]] = []
    for key, count in by_stage.most_common():
        if count < min_frequency:
            continue
        stage, agent = key.split("/", 1)
        suggestions.append(
            {
                "pattern": "low_reward_cluster",
                "stage": stage,
                "agent": agent,
                "frequency": count,
                "recommendations": {
                    "prompt": "use_detailed_handoff_template",
                    "model": "default" if agent != "implementer" else "capable",
                    "agents": _agent_chain_hint(stage, agent),
                    "human_review": stage in ("review", "deployment") or agent == "qa",
                    "context": "expand" if count >= 5 else "default",
                    "tests_timing": "before_handoff" if agent == "qa" else "after_implementation",
                },
            }
        )

    policy = update_from_events(events, root=root)

    return {
        "events_analyzed": len(events),
        "avg_reward": round(avg_reward, 3),
        "low_reward_events": len(blocks),
        "suggestions": suggestions,
        "policy_rules_count": len(policy.get("rules") or []),
        "mode": "observe",
        "proposals_written": 0,
    }


def _agent_chain_hint(stage: str, agent: str) -> list[str]:
    if stage in ("ticket", "requirements") and agent == "planner":
        return ["planner", "architect", "implementer"]
    if agent == "implementer":
        return ["architect", "implementer", "qa"]
    if agent == "qa":
        return ["qa", "reviewer"]
    return [agent]


def report_json(last_n: int = 100, **kwargs: Any) -> str:
    return json.dumps(analyze(last_n, **kwargs), indent=2, ensure_ascii=False)
