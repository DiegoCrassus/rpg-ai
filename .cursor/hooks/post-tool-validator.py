#!/usr/bin/env python3
"""
Cursor postToolUse hook — silent error detection in tool responses.

Detects cases where a tool returned HTTP 200 / exit 0 but the response body
indicates a logical failure (empty result, service error message, stale data).

Hook event: postToolUse
Exit 0 always — this hook is advisory, not blocking.
Emits a structured warning to stdout that Cursor surfaces to the agent.
"""

from __future__ import annotations

import json
import sys

# Patterns that signal a silent failure even when the tool "succeeded"
SILENT_ERROR_PATTERNS: list[tuple[str, str]] = [
    ("no results found", "Tool returned empty result set — verify query or inputs"),
    ("service under maintenance", "Downstream service is unavailable — retry later or escalate"),
    ("rate limit exceeded", "API rate limit hit — wait before retrying"),
    ("unauthorized", "Authentication failure — check API token configuration"),
    ("not found", "Referenced resource does not exist — verify ID or path"),
    ("internal server error", "Downstream server error — retry or escalate to DevOps"),
    ("timeout", "Tool call timed out — reduce scope or retry with smaller input"),
    ("empty response", "Tool returned an empty response — check input parameters"),
    ("no such file", "File path does not exist — verify path before proceeding"),
    ("permission denied", "File permission error — check file ownership or gate status"),
    ("connection refused", "Service is not reachable — check if local server is running"),
    ("does not exist", "Referenced object is missing — verify existence before acting"),
]

# Tool names whose empty outputs are a likely silent error
EXPECT_NONEMPTY = {"Bash", "Read", "WebFetch", "Grep", "Glob"}


def check_output(tool_name: str, output: str) -> list[str]:
    warnings: list[str] = []
    lower = output.lower()

    for pattern, message in SILENT_ERROR_PATTERNS:
        if pattern in lower:
            warnings.append(f"[silent-error] {message} (matched: '{pattern}')")

    if tool_name in EXPECT_NONEMPTY and len(output.strip()) < 10:
        warnings.append(
            f"[silent-error] Tool '{tool_name}' returned near-empty output "
            f"({len(output.strip())} chars) — verify inputs or skip if expected"
        )

    return warnings


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        sys.exit(0)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name: str = payload.get("tool_name", "")
    tool_output = payload.get("tool_result") or payload.get("output") or ""
    if isinstance(tool_output, dict):
        tool_output = json.dumps(tool_output)
    elif not isinstance(tool_output, str):
        tool_output = str(tool_output)

    warnings = check_output(tool_name, tool_output)
    if not warnings:
        sys.exit(0)

    result = {
        "type": "silent_error_warning",
        "tool": tool_name,
        "warnings": warnings,
        "agent_message": (
            f"ALTK post-tool validator detected potential silent errors in '{tool_name}' output. "
            f"Review before proceeding: {'; '.join(warnings)}"
        ),
    }
    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
