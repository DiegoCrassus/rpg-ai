#!/usr/bin/env python3
"""SDLC DSL CLI — doctor, validate, list-stages."""

import os
import sys

# Resolve repository root relative to this file's location: .sdlc/dsl/cli.py -> root
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

# Add root to path so relative imports work when run as a script
sys.path.insert(0, _ROOT)


def cmd_doctor() -> int:
    from _sdlc_dsl.doctor import print_report, run_doctor  # type: ignore[import]

    findings = run_doctor(_ROOT)
    return print_report(findings, _ROOT)


def cmd_validate() -> int:
    from _sdlc_dsl.loader import LoadError, load_sdlc_config  # type: ignore[import]
    from _sdlc_dsl.validator import validate  # type: ignore[import]

    try:
        config = load_sdlc_config(_ROOT)
    except LoadError as e:
        print(f"[FAIL] Load error: {e}")
        return 1

    findings = validate(config)
    fail_count = 0
    for level, message in findings:
        print(f"[{level}] {message}")
        if level == "FAIL":
            fail_count += 1

    if not findings:
        print("[PASS] All schema consistency checks passed.")
    else:
        print(f"\nValidation summary: {len(findings)} findings, {fail_count} failures")

    return 0 if fail_count == 0 else 1


def cmd_list_stages() -> int:
    from _sdlc_dsl.loader import LoadError, load_lifecycle  # type: ignore[import]

    try:
        stages = load_lifecycle(_ROOT)
    except LoadError as e:
        print(f"[FAIL] Load error: {e}")
        return 1

    print(f"SDLC Lifecycle — {len(stages)} stages\n")
    for stage in sorted(stages, key=lambda s: s.order):
        print(f"  {stage.order:2d}. [{stage.id:<15}] {stage.name}")
        print(f"      {stage.description}")
    return 0


def cmd_workflow() -> int:
    dsl_path = os.path.join(_ROOT, ".sdlc", "dsl")
    if dsl_path not in sys.path:
        sys.path.insert(0, dsl_path)
    from workflow import run_workflow  # type: ignore[import-not-found]

    return run_workflow(sys.argv[2:])


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python .sdlc/dsl/cli.py <command>")
        print("Commands: doctor | validate | list-stages | workflow")
        return 1

    command = sys.argv[1]

    # Expose the dsl package under a dot-safe alias
    _setup_import_alias()

    if command == "doctor":
        return cmd_doctor()
    elif command == "validate":
        return cmd_validate()
    elif command == "list-stages":
        return cmd_list_stages()
    elif command == "workflow":
        return cmd_workflow()
    else:
        print(f"Unknown command: {command}")
        print("Commands: doctor | validate | list-stages | workflow")
        return 1


def _setup_import_alias() -> None:
    """
    Register .sdlc/dsl as '_sdlc_dsl' module so imports work
    even though '.sdlc' starts with a dot (invalid Python identifier).
    """
    import importlib.util
    import types

    dsl_path = os.path.join(_ROOT, ".sdlc", "dsl")

    # Create a synthetic package '_sdlc_dsl' pointing to .sdlc/dsl
    if "_sdlc_dsl" not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            "_sdlc_dsl",
            os.path.join(dsl_path, "__init__.py"),
            submodule_search_locations=[dsl_path],
        )
        if spec is None or spec.loader is None:
            print("[FAIL] Cannot load _sdlc_dsl package", file=sys.stderr)
            sys.exit(1)
        module = types.ModuleType("_sdlc_dsl")
        module.__path__ = [dsl_path]  # type: ignore[assignment]
        module.__package__ = "_sdlc_dsl"
        sys.modules["_sdlc_dsl"] = module

    # Register submodules
    for submod in ["models", "loader", "validator", "doctor"]:
        full_name = f"_sdlc_dsl.{submod}"
        if full_name not in sys.modules:
            spec = importlib.util.spec_from_file_location(
                full_name,
                os.path.join(dsl_path, f"{submod}.py"),
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                mod.__package__ = "_sdlc_dsl"
                sys.modules[full_name] = mod
                spec.loader.exec_module(mod)  # type: ignore[union-attr]


if __name__ == "__main__":
    sys.exit(main())
