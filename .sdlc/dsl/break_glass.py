"""Emergency bypass for SDLC enforcement flags (requires explicit env)."""

from __future__ import annotations

import os
import sys


def is_break_glass() -> bool:
    return os.environ.get("SDLC_BREAK_GLASS", "").strip() == "1"


def require_break_glass(flag_name: str) -> bool:
    """Return True if break-glass is active; otherwise print error and return False."""
    if is_break_glass():
        print(
            f"WARN: {flag_name} allowed via SDLC_BREAK_GLASS=1 — audit on Plane SDLC_META card",
            file=sys.stderr,
        )
        return True
    print(
        f"ERROR: {flag_name} requires SDLC_BREAK_GLASS=1 and an SDLC_META audit note on Plane",
        file=sys.stderr,
    )
    return False
