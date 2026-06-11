"""Tests for the modular SDLC manifest loader."""

from __future__ import annotations

import sys
from pathlib import Path

DSL = Path(__file__).resolve().parent
SDLC_ROOT = DSL.parent
if str(SDLC_ROOT) not in sys.path:
    sys.path.insert(0, str(SDLC_ROOT))

from dsl import loader  # noqa: E402


def test_load_merged_manifest_accepts_list_valued_module_data(tmp_path) -> None:
    root = tmp_path
    sdlc_dir = root / ".sdlc"
    (sdlc_dir / "process").mkdir(parents=True)
    (sdlc_dir / "manifest").mkdir()
    (sdlc_dir / "process" / "master-workflow.md").write_text("# Workflow\n", encoding="utf-8")
    (sdlc_dir / "process" / "change-lifecycle.md").write_text(
        "# Lifecycle\n",
        encoding="utf-8",
    )
    (sdlc_dir / "manifest" / "catalog.yaml").write_text(
        "skills:\n  - id: qa\n",
        encoding="utf-8",
    )
    (sdlc_dir / "sdlc.yaml").write_text(
        """
version: '5.2'
contract:
  modules:
    manifest:
      data: manifest/catalog.yaml
    process:
      data:
        - process/master-workflow.md
        - process/change-lifecycle.md
""".lstrip(),
        encoding="utf-8",
    )

    loader._cache.clear()

    merged = loader.load_merged_manifest(str(root))

    assert merged["skills"] == [{"id": "qa"}]
    assert merged["contract"]["modules"]["process"]["data"] == [
        "process/master-workflow.md",
        "process/change-lifecycle.md",
    ]
