"""Real-behavior round trip for LLMExpert — hits the actual Claude client
this deployment is wired to (Bedrock or direct Anthropic, whichever
build_services() resolves), not a fake.

Per this project's test-behavior-real.md: every spec needs at least one
test that exercises real behavior against a real client. Costs real
tokens and real latency, so it never runs by default — see
gatople_api/pyproject.toml's addopts (`-m "not eval"`).

Run explicitly:
    cd gatople_api && uv run pytest -m eval
"""

from __future__ import annotations

import pytest
from fractalmusic.generate.types import MODE_NAMES, NOTE_NAMES, GenerationRequest

from gatople_api.bootstrap import build_services

pytestmark = pytest.mark.eval


def test_real_llm_composes_a_valid_pattern_from_a_description() -> None:
    """A real mood description round-trips through the real LLM into a
    Pattern that satisfies every constraint the prompt teaches it —
    closed tonic/mode sets, matching degrees/rhythm lengths, in-range
    degrees for whichever family (penta vs hepta) it picked."""
    services = build_services()
    request = GenerationRequest(
        tonic="A",
        mode="Eólico",
        length_events=16,
        flavor="free",
        free_text="an uplifting pop melody with a bright, hopeful feel",
    )

    pattern = services.llm_expert.query(request)

    assert pattern.tonic in NOTE_NAMES
    assert pattern.mode in MODE_NAMES
    assert len(pattern.degrees) == len(pattern.rhythm)
    assert 4 <= len(pattern.degrees) <= 32
    max_degree = 5 if pattern.mode.startswith("Penta") else 7
    assert all(1 <= d <= max_degree for d in pattern.degrees)
    # Real LLM composition, not the deterministic stub — and never a
    # fabricated book citation for it.
    assert pattern.provenance.book_hash == "llm-composed"
