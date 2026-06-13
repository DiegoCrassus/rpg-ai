"""Derived, non-executing MVP test traceability skeleton for SDLC Studio."""

from __future__ import annotations

from typing import Any

from studio.engine.reporting import AUTHORITY

SKELETON_ID = "skeleton.sdlc_studio.mvp"
EPIC_CARD = "RPG-53"
SOURCE_CARD = "RPG-75"
SKELETON_SOURCE_PATHS = (
    "studio/engine/mvp_test_skeleton.py",
    "studio/docs/prototypes/ai-mvp-test-skeleton-prototype.md",
    "docs/roadmap/sdlc-studio-mvp-roadmap.md",
    ".sdlc/memory/test-skeleton.md",
)
VALIDATION_TYPES = ("automated", "manual_review", "cli", "docs_review", "doctor_gate")
SKELETON_NON_GOALS = (
    "Does not run pytest, make sdlc-doctor, CI, Plane, GitHub, or shell workflows.",
    "Does not claim pass/fail results for future MVP validation areas.",
    "Does not mutate source artifacts or persist skeleton reports.",
)
EntrySpec = tuple[str, int, str, tuple[str, ...], str, tuple[str, ...], str]

SKELETON_ENTRIES: tuple[EntrySpec, ...] = (
    ("skeleton.phase.foundation", 1, "Foundation baseline", ("RPG-54", "RPG-55"), "foundation", ("docs_review", "manual_review"), "Baseline inventory and source boundaries reference authoritative paths without copying bodies."),
    ("skeleton.phase.registry", 2, "Registry/modeling hardening", ("RPG-56", "RPG-57"), "registry", ("automated",), "Registry entity IDs, paths, and relationships validate without duplicate IDs or broken refs."),
    ("skeleton.phase.graph_ir", 3, "Graph model/IR", ("RPG-58", "RPG-59"), "graph_ir", ("automated", "docs_review"), "Graph IR and validation result IR contracts match schema expectations."),
    ("skeleton.phase.compiler_validator", 4, "Compiler/validator", ("RPG-60", "RPG-61", "RPG-62"), "compiler_validator", ("automated", "cli"), "Compiler outputs are reproducible; validator reports severity, path, message, and next action."),
    ("skeleton.phase.cli", 5, "CLI command center", ("RPG-63", "RPG-64"), "cli", ("cli", "automated"), "CLI commands produce deterministic output and meaningful exit codes without mutating sources."),
    ("skeleton.phase.visual", 6, "Visual orchestration prototype", ("RPG-65", "RPG-66", "RPG-67"), "visual", ("automated", "manual_review"), "Derived canvas and validation inspection models stay non-authoritative and filterable."),
    ("skeleton.phase.ai", 7, "AI composition prototype", ("RPG-68", "RPG-69"), "ai", ("automated", "cli", "manual_review"), "Workflow assistance stays advisory with guardrails and no authoritative mutation."),
    ("skeleton.phase.simulation", 8, "Simulation/runtime preview", ("RPG-70", "RPG-71"), "simulation", ("automated", "cli"), "Simulation preview is non-executing and matches lifecycle gate behavior."),
    ("skeleton.phase.publish", 9, "Publish/operate workflows", ("RPG-72", "RPG-73"), "publish", ("cli", "docs_review"), "Publish evidence projection matches template keys without Plane/GitHub mutation."),
    ("skeleton.phase.readiness", 10, "MVP readiness", ("RPG-74", "RPG-75"), "readiness", ("cli", "automated"), "Readiness loop and test skeleton cover MVP checklist without declaring MVP complete."),
    ("skeleton.gate.registry_schema", 0, "Registry/schema gate", ("RPG-56", "RPG-57", "RPG-58", "RPG-59"), "registry_schema", ("automated",), "Schema and registry checks pass with documented warnings only."),
    ("skeleton.gate.compiler_validator", 0, "Compiler/validator gate", ("RPG-61", "RPG-62"), "compiler_validator", ("automated", "cli"), "Broken references, schema drift, and copied authoritative content fail validation."),
    ("skeleton.gate.cli", 0, "CLI gate", ("RPG-63", "RPG-64"), "cli_gate", ("cli",), "Exit codes distinguish pass, warning, and failure states."),
    ("skeleton.gate.preview_simulation", 0, "Preview/simulation gate", ("RPG-70", "RPG-71"), "preview_simulation", ("cli", "automated"), "Previews are non-executing and distinguish expected, blocked, and unsupported paths."),
    ("skeleton.gate.docs_review", 0, "Docs review gate", ("RPG-55", "RPG-73"), "docs_review", ("docs_review", "manual_review"), "Documentation states source-of-truth boundaries and derived-only previews."),
    ("skeleton.gate.doctor", 0, "Doctor gate", ("RPG-74",), "doctor", ("doctor_gate",), "make sdlc-doctor exits 0 before MVP readiness is declared."),
)


def build_mvp_test_skeleton() -> dict[str, Any]:
    """Return the in-memory MVP test traceability skeleton (no execution)."""

    entries = [_entry_record(spec) for spec in SKELETON_ENTRIES]
    phases = sorted({entry["phase"] for entry in entries if entry["phase"] > 0})
    type_counts = {kind: 0 for kind in VALIDATION_TYPES}
    cards: set[str] = set()
    for entry in entries:
        cards.update(entry["cards"])
        for kind in entry["validation_types"]:
            type_counts[kind] = type_counts.get(kind, 0) + 1
    return {
        "skeleton": {
            "id": SKELETON_ID,
            "authority": AUTHORITY,
            "execution_mode": "non_executing_traceability_plan",
            "epic": EPIC_CARD,
            "card": SOURCE_CARD,
            "source_refs": [{"ref_type": "path", "ref": path} for path in SKELETON_SOURCE_PATHS],
            "non_goals": list(SKELETON_NON_GOALS),
        },
        "summary": {
            "entry_count": len(entries),
            "phase_count": len(phases),
            "validation_types": type_counts,
            "cards_referenced": sorted(cards),
            "execution_claimed": False,
        },
        "entries": entries,
        "validation_types": list(VALIDATION_TYPES),
    }


def list_skeleton_entries() -> list[dict[str, Any]]:
    """Return skeleton entries for CLI listing."""

    return list(build_mvp_test_skeleton()["entries"])


def render_mvp_test_skeleton_text(model: dict[str, Any]) -> str:
    skeleton, summary = model["skeleton"], model["summary"]
    lines = [
        "Studio MVP test skeleton: derived, non-authoritative traceability plan",
        f"skeleton: {skeleton['id']}",
        f"authority: {skeleton['authority']}",
        f"execution_mode: {skeleton['execution_mode']}",
        f"epic: {skeleton['epic']} card: {skeleton['card']}",
        f"entries: {summary['entry_count']} phases: {summary['phase_count']}",
        f"execution_claimed: {summary['execution_claimed']}",
        "validation_types:",
        *(f"- {kind}: {summary['validation_types'][kind]}" for kind in VALIDATION_TYPES),
        "entries:",
    ]
    for entry in model["entries"]:
        types = ", ".join(entry["validation_types"])
        cards = ", ".join(entry["cards"])
        lines.append(f"- [{entry['status']}] {entry['id']} phase={entry['phase']} cards={cards} types={types}")
        lines.append(f"  ac: {entry['ac_ref']}")
    lines.append("reminder: skeleton plans future validation only; QA executes tests on scoped cards.")
    return "\n".join(lines) + "\n"


def _entry_record(spec: EntrySpec) -> dict[str, Any]:
    entry_id, phase, label, cards, area, validation_types, ac_ref = spec
    return {
        "id": entry_id,
        "phase": phase,
        "label": label,
        "cards": list(cards),
        "area": area,
        "validation_types": list(validation_types),
        "ac_ref": ac_ref,
        "status": "planned",
    }
