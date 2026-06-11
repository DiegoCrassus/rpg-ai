"""CLI entry shim — use `python -m studio.cli` from repository root."""

from studio.engine.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
