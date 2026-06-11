#!/usr/bin/env python3
"""
Compact the SDLC memory context to prevent context-window overflow.

Reads .sdlc/memory/operational-context.md + session-gate.json,
appends a compact summary block with current state,
and truncates stale session summary sections (keeps last MAX_SUMMARIES).

Usage: python3 .sdlc/scripts/compact_memory.py
       make sdlc-compact-memory

Source: Context window management protocol (arXiv 2604.14228)
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
try:
    from datetime import UTC
except ImportError:
    UTC = timezone.utc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEMORY_DIR = ROOT / ".sdlc" / "memory"
OPS_CTX = MEMORY_DIR / "operational-context.md"
SESSION_GATE = MEMORY_DIR / "session-gate.json"
MAX_SUMMARIES = 5  # keep at most N rolling summary blocks


def load_session_gate() -> dict:
    if SESSION_GATE.is_file():
        try:
            return json.loads(SESSION_GATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def build_compact_block(gate: dict) -> str:
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    card = gate.get("card") or "(none)"
    branch = gate.get("branch") or "(none)"
    stage = gate.get("stage") or "(none)"
    last_agent = gate.get("last_agent") or "(none)"
    last_commit = gate.get("last_commit") or "(none)"
    status = gate.get("gate_status", "closed")

    return (
        f"\n## Session summary — {now}\n"
        f"Gate: {status} | Stage: {stage} | Card: {card}\n"
        f"Branch: {branch} | Last commit: {last_commit}\n"
        f"Last agent: {last_agent}\n"
        f"Compacted at: {now}\n"
    )


def prune_old_summaries(content: str) -> str:
    """Keep only the last MAX_SUMMARIES summary blocks."""
    pattern = r"\n## Session summary — .+?(?=\n## Session summary —|\Z)"
    blocks = re.findall(pattern, content, flags=re.DOTALL)
    if len(blocks) <= MAX_SUMMARIES:
        return content
    # Remove oldest blocks, keep the static header and last MAX_SUMMARIES
    static_part = re.split(r"\n## Session summary —", content, maxsplit=1)[0]
    kept = blocks[-MAX_SUMMARIES:]
    return static_part + "".join(kept)


def main() -> None:
    if not OPS_CTX.is_file():
        print(f"[compact] {OPS_CTX} not found — nothing to compact", file=sys.stderr)
        sys.exit(1)

    gate = load_session_gate()
    current = OPS_CTX.read_text(encoding="utf-8")
    block = build_compact_block(gate)
    updated = prune_old_summaries(current + block)
    OPS_CTX.write_text(updated, encoding="utf-8")
    print(f"[compact] operational-context.md compacted ({len(updated)} chars)")
    print(f"[compact] Gate: {gate.get('gate_status','closed')} | Card: {gate.get('card','(none)')}")


if __name__ == "__main__":
    main()
