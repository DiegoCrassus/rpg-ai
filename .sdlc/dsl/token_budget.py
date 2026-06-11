"""Token budget ledger — config from sdlc.yaml, state in .sdlc/memory/token-budget.json."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from datetime import UTC
except ImportError:
    UTC = timezone.utc

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


def repo_root(start: Path | None = None) -> Path:
    if start is None:
        start = Path(__file__).resolve()
    cur = start if start.is_dir() else start.parent
    for _ in range(8):
        if (cur / ".sdlc").is_dir() and (cur / "Makefile").is_file():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return Path(__file__).resolve().parents[2]


def ledger_path(root: Path | None = None) -> Path:
    return (root or repo_root()) / ".sdlc" / "memory" / "token-budget.json"


@dataclass
class TokenBudgetConfig:
    enforce: str = "strict"
    session_budget: int = 500_000
    turn_budget: int = 32_000
    subagent_budget: int = 120_000
    handoff_max_lines: int = 45
    warn_ratio: float = 0.85
    estimate_chars_per_token: int = 4
    block_task_on_exceed: bool = True
    block_prompt_on_exceed: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TokenBudgetConfig:
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        cfg = cls(**{k: v for k, v in data.items() if k in known})
        if cfg.enforce not in ("strict", "warn", "off"):
            cfg.enforce = "strict"
        return cfg


@dataclass
class TokenLedger:
    session_id: str = ""
    started_at: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_tokens: int = 0
    turns: int = 0
    subagent_spawns: int = 0
    blocked: bool = False
    block_reason: str = ""
    last_event: str = ""
    events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens + self.estimated_tokens

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TokenLedger:
        return cls(
            session_id=str(data.get("session_id") or ""),
            started_at=str(data.get("started_at") or ""),
            input_tokens=int(data.get("input_tokens") or 0),
            output_tokens=int(data.get("output_tokens") or 0),
            estimated_tokens=int(data.get("estimated_tokens") or 0),
            turns=int(data.get("turns") or 0),
            subagent_spawns=int(data.get("subagent_spawns") or 0),
            blocked=bool(data.get("blocked")),
            block_reason=str(data.get("block_reason") or ""),
            last_event=str(data.get("last_event") or ""),
            events=list(data.get("events") or [])[-50:],
        )


def load_config(root: Path | None = None) -> TokenBudgetConfig:
    root = root or repo_root()
    path = root / ".sdlc" / "sdlc.yaml"
    if yaml is None or not path.is_file():
        return TokenBudgetConfig()
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return TokenBudgetConfig.from_dict((data.get("core") or {}).get("tokens") or {})


def load_ledger(root: Path | None = None) -> TokenLedger:
    path = ledger_path(root)
    if not path.is_file():
        return TokenLedger()
    try:
        return TokenLedger.from_dict(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return TokenLedger()


def save_ledger(ledger: TokenLedger, root: Path | None = None) -> Path:
    path = ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path


def reset_session(root: Path | None = None) -> TokenLedger:
    ledger = TokenLedger(session_id=str(uuid.uuid4()), started_at=datetime.now(UTC).isoformat())
    save_ledger(ledger, root)
    return ledger


def _dig(data: dict[str, Any], *keys: str) -> Any:
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def extract_usage(payload: dict[str, Any]) -> tuple[int, int, bool]:
    pairs = (
        (("usage", "input_tokens"), ("usage", "output_tokens")),
        (("usage", "inputTokens"), ("usage", "outputTokens")),
        (("usage", "prompt_tokens"), ("usage", "completion_tokens")),
        (("token_usage", "prompt_tokens"), ("token_usage", "completion_tokens")),
    )
    for inp_path, out_path in pairs:
        inp = _dig(payload, *inp_path)
        out = _dig(payload, *out_path)
        if isinstance(inp, (int, float)) or isinstance(out, (int, float)):
            return int(inp or 0), int(out or 0), True
    if isinstance(payload.get("input_tokens"), (int, float)):
        return int(payload["input_tokens"]), int(payload.get("output_tokens") or 0), True
    return 0, 0, False


def estimate_text_tokens(payload: dict[str, Any], cfg: TokenBudgetConfig) -> int:
    chunks: list[str] = []
    for key in ("text", "response", "content", "message", "thought", "output"):
        if isinstance(payload.get(key), str):
            chunks.append(payload[key])
    nested = payload.get("message")
    if isinstance(nested, dict):
        for key in ("content", "text"):
            if isinstance(nested.get(key), str):
                chunks.append(nested[key])
    text = "\n".join(chunks)
    if not text.strip():
        return 0
    return max(1, len(text) // max(cfg.estimate_chars_per_token, 1))


def record_usage(payload: dict[str, Any], *, event: str, root: Path | None = None) -> TokenLedger:
    cfg = load_config(root)
    ledger = load_ledger(root)
    if not ledger.session_id:
        ledger = reset_session(root)

    inp, out, from_api = extract_usage(payload)
    estimated = 0
    if from_api:
        ledger.input_tokens += inp
        ledger.output_tokens += out
    else:
        estimated = estimate_text_tokens(payload, cfg)
        ledger.estimated_tokens += estimated

    if event in ("after-response", "after-thought", "before-prompt"):
        ledger.turns += 1

    ledger.last_event = event
    ledger.events.append(
        {
            "at": datetime.now(UTC).isoformat(),
            "event": event,
            "input": inp,
            "output": out,
            "estimated": estimated,
            "total": ledger.total_tokens,
        }
    )
    ledger.events = ledger.events[-50:]

    reason = _evaluate_block(ledger, cfg, event)
    if reason:
        ledger.blocked = True
        ledger.block_reason = reason

    save_ledger(ledger, root)
    return ledger


def _evaluate_block(ledger: TokenLedger, cfg: TokenBudgetConfig, event: str) -> str:
    if cfg.enforce == "off":
        return ""
    if ledger.total_tokens >= cfg.session_budget:
        return f"session budget exceeded ({ledger.total_tokens}/{cfg.session_budget})"
    if ledger.events:
        last = ledger.events[-1]
        turn_total = int(last.get("input") or 0) + int(last.get("output") or 0) + int(last.get("estimated") or 0)
        if event in ("after-response", "after-thought") and turn_total > cfg.turn_budget:
            return f"turn budget exceeded ({turn_total}/{cfg.turn_budget})"
    return ""


def check_allow_action(action: str, root: Path | None = None) -> tuple[bool, str, TokenLedger]:
    cfg = load_config(root)
    ledger = load_ledger(root)
    if cfg.enforce == "off":
        return True, "enforcement off", ledger
    if ledger.blocked and cfg.enforce == "strict":
        return False, ledger.block_reason or "budget blocked", ledger
    total = ledger.total_tokens
    if total >= cfg.session_budget:
        msg = f"session budget exceeded ({total}/{cfg.session_budget})"
        return (False, msg, ledger) if cfg.enforce == "strict" else (True, f"WARN: {msg}", ledger)
    ratio = total / cfg.session_budget if cfg.session_budget else 0
    if ratio >= cfg.warn_ratio:
        return True, f"WARN: {ratio:.0%} session budget used", ledger
    if action == "subagent-start":
        ledger.subagent_spawns += 1
        if total > cfg.subagent_budget and cfg.block_task_on_exceed and cfg.enforce == "strict":
            return False, f"subagent budget pressure ({total}>{cfg.subagent_budget})", ledger
    save_ledger(ledger, root)
    return True, "ok", ledger


def status_text(root: Path | None = None) -> str:
    cfg = load_config(root)
    ledger = load_ledger(root)
    total = ledger.total_tokens
    pct = (100.0 * total / cfg.session_budget) if cfg.session_budget else 0
    return "\n".join(
        [
            f"enforce: {cfg.enforce}",
            f"session: {total}/{cfg.session_budget} ({pct:.1f}%)",
            f"turn_cap: {cfg.turn_budget} | subagent_cap: {cfg.subagent_budget}",
            f"turns: {ledger.turns} | subagent_spawns: {ledger.subagent_spawns}",
            f"input: {ledger.input_tokens} | output: {ledger.output_tokens} | est: {ledger.estimated_tokens}",
            f"blocked: {ledger.blocked}" + (f" — {ledger.block_reason}" if ledger.block_reason else ""),
            f"session_id: {ledger.session_id or '(none)'}",
        ]
    )
