"""Load and apply canonical intent rules from `.sdlc/process/intent_rules.yaml`."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

RULES_PATH_REL = ".sdlc/process/intent_rules.yaml"


def rules_path(root: Path) -> Path:
    return root / RULES_PATH_REL


def load_rules(root: Path | None = None) -> dict[str, Any]:
    if yaml is None:
        return {}
    from gate import repo_root  # noqa: PLC0415

    base = root or repo_root()
    path = rules_path(base)
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def _text_matches(text: str, rule: dict[str, Any], *, empty_app: bool) -> bool:
    match = rule.get("match") or {}
    t = text.lower().strip()

    if match.get("empty_text") and not t:
        return True
    if match.get("ends_with_question") and t.endswith("?"):
        return True

    all_kw = [str(k).lower() for k in (match.get("all_keywords") or [])]
    any_kw = [str(k).lower() for k in (match.get("any_keywords") or [])]

    if all_kw and not all(k in t for k in all_kw):
        return False
    if any_kw and not any(k in t for k in any_kw):
        return False
    if all_kw or any_kw:
        return True

    if rule.get("id") == "greenfield" and match.get("any_keywords"):
        # greenfield also signals empty_app when placeholder app
        return any(k in t for k in any_kw)

    return False


def classify_from_rules(
    text: str,
    *,
    root: Path | None = None,
    empty_app: bool = False,
) -> dict[str, Any] | None:
    """Return classification dict or None if rules file missing."""
    data = load_rules(root)
    if not data:
        return None

    rules = sorted(
        data.get("rules") or [],
        key=lambda r: int(r.get("priority") or 0),
        reverse=True,
    )
    defaults = data.get("defaults") or {}
    next_map = defaults.get("next_agent_map") or {}

    for rule in rules:
        if not _text_matches(text, rule, empty_app=empty_app):
            continue
        intent = str(rule.get("intent") or defaults.get("intent") or "FEATURE")
        confidence = 0.9 if intent != "FEATURE" else float(defaults.get("confidence") or 0.7)
        signals: list[str] = []
        if intent == "GREENFIELD":
            signals.append("rules")
            if empty_app:
                signals.append("empty_app")
        return {
            "intent": intent,
            "confidence": confidence,
            "greenfield_signals": signals,
            "scope_hint": text[:200] if text else "",
            "requires_plane": intent != "READONLY",
            "requires_branch": intent
            in ("GREENFIELD", "FEATURE", "BUGFIX", "HOTFIX", "INFRA", "SDLC_META", "DOCS_ONLY"),
            "next_agent": next_map.get(intent, "planner"),
            "rationale": f"classified as {intent} via intent_rules.yaml ({rule.get('id')})",
        }

    intent = str(defaults.get("intent") or "FEATURE")
    return {
        "intent": intent,
        "confidence": float(defaults.get("confidence") or 0.7),
        "greenfield_signals": [],
        "scope_hint": text[:200] if text else "",
        "requires_plane": True,
        "requires_branch": intent
        in ("GREENFIELD", "FEATURE", "BUGFIX", "HOTFIX", "INFRA", "SDLC_META", "DOCS_ONLY"),
        "next_agent": next_map.get(intent, "planner"),
        "rationale": f"classified as {intent} (default)",
    }
