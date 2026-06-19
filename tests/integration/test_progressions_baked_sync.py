"""Drift guard: docs/gatople/progressions_baked.json must match build_baked()."""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build_progressions_data import build_baked  # noqa: E402


def test_progressions_baked_json_matches_build_baked() -> None:
    on_disk = json.loads((REPO_ROOT / "docs" / "gatople" / "progressions_baked.json").read_text())
    fresh = build_baked()
    assert on_disk == fresh, (
        "docs/gatople/progressions_baked.json is stale. "
        "Run: uv run python scripts/build_progressions_data.py"
    )
