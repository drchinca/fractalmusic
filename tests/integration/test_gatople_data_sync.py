"""Drift guard: every data.json snapshot must match build_payload() exactly.

The Gátople data is consumed by two surfaces:

* docs/gatople/data.json — the static page in docs/
* web/public/data.json   — the Vite/React app under web/

Both are built from the same `build_payload()`. If either drifts, this test
fails. Regenerate both with::

    uv run python scripts/build_gatople_data.py
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build_gatople_data import OUTPUT_PATHS, build_payload  # noqa: E402


@pytest.mark.parametrize("relative_parts", OUTPUT_PATHS)
def test_data_json_matches_build_payload(relative_parts: tuple[str, ...]) -> None:
    path = REPO_ROOT.joinpath(*relative_parts)
    on_disk = json.loads(path.read_text())
    fresh = build_payload()
    assert on_disk == fresh, (
        f"{path.relative_to(REPO_ROOT)} is stale. "
        "Run: uv run python scripts/build_gatople_data.py"
    )
