"""Validator tests. The similarity fn is injected; no patch() anywhere."""

import pytest

from chat_bff.citations.parser import parse_answer
from chat_bff.citations.validator import (
    ChunkLookup,
    ValidationVerdict,
    validate_answer,
)

_RETRIEVED: ChunkLookup = {
    ("b202598c", 0, 0, 17): "Función Cíclica volvemos a la tonalidad CERO Alteraciones",
    ("b202598c", 0, 0, 27): "El Dodecamundo es doce mundos sonoros",
    ("f39cb7c5", 0, 0, 3): "Sistema Fractal rompe con los esquemas tradicionales",
}


async def _high_sim(_a: str, _b: str) -> float:
    return 0.9


async def _low_sim(_a: str, _b: str) -> float:
    return 0.2


async def _by_substring(claim: str, snippet: str) -> float:
    """Cheap deterministic stand-in: high if the claim shares ≥1 word with
    the snippet, low otherwise. Useful for exercising mixed verdicts."""
    claim_words = {w.lower() for w in claim.split() if len(w) > 3}
    snippet_words = {w.lower() for w in snippet.split() if len(w) > 3}
    overlap = claim_words & snippet_words
    return 0.9 if overlap else 0.2


async def test_no_citations_at_all() -> None:
    claims = parse_answer("Frigio is the dominant of Eólico.")
    out = await validate_answer(
        claims=claims,
        retrieved=_RETRIEVED,
        similarity=_high_sim,
        threshold=0.55,
    )
    assert out.verdict == ValidationVerdict.NO_CITATIONS


async def test_uncited_claim_among_cited_ones() -> None:
    claims = parse_answer(
        "Frigio is dominant of Eólico [b202598c·ch0§0¶17 p.11]. "
        "And another point with no cite."
    )
    out = await validate_answer(
        claims=claims,
        retrieved=_RETRIEVED,
        similarity=_high_sim,
        threshold=0.55,
    )
    assert out.verdict == ValidationVerdict.UNCITED_CLAIM


async def test_membership_failure_on_fabricated_chunk() -> None:
    """The exact §4 'hash-fabrication' scenario from the spec."""
    claims = parse_answer(
        "Frigio is dominant of Eólico [f39cb7c5·ch99§9¶999 p.999]."
    )
    out = await validate_answer(
        claims=claims,
        retrieved=_RETRIEVED,
        similarity=_high_sim,
        threshold=0.55,
    )
    assert out.verdict == ValidationVerdict.UNKNOWN_CHUNK
    assert len(out.failures) == 1


async def test_low_fidelity_rejects() -> None:
    claims = parse_answer(
        "Frigio is dominant of Eólico [b202598c·ch0§0¶17 p.11]."
    )
    out = await validate_answer(
        claims=claims,
        retrieved=_RETRIEVED,
        similarity=_low_sim,
        threshold=0.55,
    )
    assert out.verdict == ValidationVerdict.LOW_FIDELITY
    assert len(out.fidelity_scores) == 1
    assert out.fidelity_scores[0] == 0.2


async def test_repetition_gaming_caught_by_fidelity() -> None:
    """Same citation repeated for unrelated claims — only the related one
    scores high; the rest fail fidelity. Spec §4 'repetition gaming'."""
    claims = parse_answer(
        "Función cíclica returns to the tonality [b202598c·ch0§0¶17 p.11]. "
        "And penta has nothing to do with semitones [b202598c·ch0§0¶17 p.11]."
    )
    out = await validate_answer(
        claims=claims,
        retrieved=_RETRIEVED,
        similarity=_by_substring,
        threshold=0.55,
    )
    # First claim shares "tonality"-ish words → wait, _by_substring needs >3-letter overlap
    # "función"/"cíclica"/"tonality" don't overlap with the snippet's spanish words
    # The point is mixed scores; verdict is LOW_FIDELITY because at least one fails.
    assert out.verdict == ValidationVerdict.LOW_FIDELITY


async def test_happy_path_returns_ok_with_verified_citations() -> None:
    claims = parse_answer(
        "El Dodecamundo es doce mundos [b202598c·ch0§0¶27 p.16]."
    )
    out = await validate_answer(
        claims=claims,
        retrieved=_RETRIEVED,
        similarity=_high_sim,
        threshold=0.55,
    )
    assert out.verdict == ValidationVerdict.OK
    assert len(out.verified) == 1
    assert out.verified[0].book_hash == "b202598c"


async def test_threshold_is_inclusive() -> None:
    """A score exactly equal to the threshold should pass."""
    claims = parse_answer("Anything [b202598c·ch0§0¶17 p.11].")

    async def at_threshold(_a: str, _b: str) -> float:
        return 0.55

    out = await validate_answer(
        claims=claims,
        retrieved=_RETRIEVED,
        similarity=at_threshold,
        threshold=0.55,
    )
    assert out.verdict == ValidationVerdict.OK
