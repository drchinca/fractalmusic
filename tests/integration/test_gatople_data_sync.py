"""Drift guard: docs/gatople/data.json must match build_payload() exactly.

If this test fails, the JSON snapshot consumed by the interactive wheel is
stale. Regenerate it with::

    uv run python scripts/build_gatople_data.py
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build_gatople_data import build_payload  # noqa: E402


def test_gatople_data_json_matches_build_payload() -> None:
    on_disk = json.loads((REPO_ROOT / "docs" / "gatople" / "data.json").read_text())
    fresh = build_payload()
    assert on_disk == fresh, (
        "docs/gatople/data.json is stale. "
        "Run: uv run python scripts/build_gatople_data.py"
    )
