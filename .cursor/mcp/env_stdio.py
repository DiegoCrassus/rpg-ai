#!/usr/bin/env python3
"""Load repo .env and exec an MCP stdio server (secrets stay out of mcp.json)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"


def _parse_dotenv_line(line: str) -> tuple[str, str] | None:
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        return None
    key, _, raw = line.partition("=")
    key = key.strip()
    val = raw.strip().strip('"').strip("'")
    return key, val


def load_dotenv(path: Path = ENV_PATH) -> dict[str, str]:
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parsed = _parse_dotenv_line(line)
        if parsed:
            values[parsed[0]] = parsed[1]
    return values


def _resolve_source(name: str, file_env: dict[str, str]) -> str:
    if name in file_env and file_env[name]:
        return file_env[name]
    if name in os.environ and os.environ[name]:
        return os.environ[name]
    return ""


def main() -> int:
    raw = sys.argv[1:]
    if "--" not in raw:
        print("ERROR: usage: env_stdio.py [options] -- <command...>", file=sys.stderr)
        return 1
    sep = raw.index("--")
    cli_args = raw[:sep]
    command = raw[sep + 1 :]
    if not command:
        print("ERROR: missing command after --", file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser(description="Run MCP server with env from repo .env")
    parser.add_argument(
        "--from-env",
        action="append",
        default=[],
        metavar="TARGET=SOURCE",
        help="Set process env TARGET from .env key SOURCE",
    )
    parser.add_argument(
        "--default",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Set KEY=VALUE only if KEY is unset",
    )
    args = parser.parse_args(cli_args)

    file_env = load_dotenv()

    missing: list[str] = []
    for mapping in args.from_env:
        if "=" not in mapping:
            print(f"ERROR: invalid --from-env {mapping!r}", file=sys.stderr)
            return 1
        target, source = mapping.split("=", 1)
        value = _resolve_source(source.strip(), file_env)
        if not value:
            missing.append(f"{target} (from {source})")
        else:
            os.environ[target.strip()] = value

    for item in args.default:
        if "=" not in item:
            continue
        key, val = item.split("=", 1)
        key = key.strip()
        if not os.environ.get(key):
            os.environ[key] = val

    if missing:
        print(
            "ERROR: missing required env values in .env: " + ", ".join(missing),
            file=sys.stderr,
        )
        print(f"Fill them in {ENV_PATH}", file=sys.stderr)
        return 1

    argv = list(command)
    if argv[0] in ("python", "python3"):
        argv = [sys.executable, *argv[1:]]
    elif sys.platform == "win32":
        import shutil

        resolved = shutil.which(argv[0])
        if resolved:
            argv[0] = resolved

    os.execv(argv[0], argv)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
