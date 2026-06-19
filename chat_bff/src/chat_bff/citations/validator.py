"""Validate parsed citations against the chunks retrieved this turn.

Three checks, in order. Failure short-circuits — we don't run semantic
fidelity on a citation we already rejected for membership.

1. **Membership** (I-2): each citation's tuple
   ``(book_hash, chapter_idx, section_idx, paragraph_idx)`` must match a
   chunk that was retrieved this turn. A hallucinated-but-in-scope hash
   (``f39cb7c5·ch99§9¶999``) fails here.

2. **Coverage**: every sentence in the answer that has fact-bearing
   punctuation carries ≥1 citation. (This is a prompt rule per §3, but
   the validator surfaces it so the route can decide to regenerate.)

3. **Fidelity** (I-3): for each cited claim, the cosine similarity
   between the bare claim text and the cited chunk's snippet is at least
   ``threshold`` (default 0.55, PROVISIONAL).
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum

from chat_bff.citations.parser import CitedClaim, ParsedCitation

# (book_hash, chapter_idx, section_idx, paragraph_idx) → snippet text
ChunkLookup = dict[tuple[str, int, int, int], str]
SimilarityFn = Callable[[str, str], Awaitable[float]]


class ValidationVerdict(StrEnum):
    OK = "ok"
    NO_CITATIONS = "no_citations"  # answer contains no citations at all
    UNCITED_CLAIM = "uncited_claim"  # ≥1 fact-bearing sentence missing a marker
    UNKNOWN_CHUNK = "unknown_chunk"  # marker tuple wasn't retrieved this turn
    LOW_FIDELITY = "low_fidelity"  # snippet doesn't support the claim


@dataclass(frozen=True, slots=True)
class ValidationOutcome:
    """The verdict + the parsed citations the validator looked at.

    ``failures`` lists the offending citations when the verdict isn't OK,
    so the regeneration prompt can be specific about what went wrong.
    """

    verdict: ValidationVerdict
    verified: tuple[ParsedCitation, ...] = ()
    failures: tuple[tuple[ParsedCitation, ValidationVerdict], ...] = ()
    fidelity_scores: tuple[float, ...] = ()


def _chunk_key(c: ParsedCitation) -> tuple[str, int, int, int]:
    return (c.book_hash, c.chapter_idx, c.section_idx, c.paragraph_idx)


async def validate_answer(
    *,
    claims: tuple[CitedClaim, ...],
    retrieved: ChunkLookup,
    similarity: SimilarityFn,
    threshold: float,
) -> ValidationOutcome:
    """Run the three checks against ``claims``.

    ``similarity`` is injected so the validator stays decoupled from the
    embedder. Production wires the cemaf nomic-embed scorer; tests inject
    a deterministic fake.
    """
    if not claims or not any(c.citations for c in claims):
        return ValidationOutcome(verdict=ValidationVerdict.NO_CITATIONS)

    # Coverage — every claim must have ≥1 citation
    uncited = [c for c in claims if not c.citations]
    if uncited:
        return ValidationOutcome(verdict=ValidationVerdict.UNCITED_CLAIM)

    # Membership — every cited tuple must be in retrieved
    membership_failures: list[tuple[ParsedCitation, ValidationVerdict]] = []
    for claim in claims:
        for cite in claim.citations:
            if _chunk_key(cite) not in retrieved:
                membership_failures.append((cite, ValidationVerdict.UNKNOWN_CHUNK))
    if membership_failures:
        return ValidationOutcome(
            verdict=ValidationVerdict.UNKNOWN_CHUNK,
            failures=tuple(membership_failures),
        )

    # Fidelity — each (claim, snippet) pair must score ≥ threshold
    verified: list[ParsedCitation] = []
    scores: list[float] = []
    fidelity_failures: list[tuple[ParsedCitation, ValidationVerdict]] = []
    for claim in claims:
        for cite in claim.citations:
            snippet = retrieved[_chunk_key(cite)]
            score = await similarity(claim.sentence, snippet)
            scores.append(score)
            if score >= threshold:
                verified.append(cite)
            else:
                fidelity_failures.append((cite, ValidationVerdict.LOW_FIDELITY))

    if fidelity_failures:
        return ValidationOutcome(
            verdict=ValidationVerdict.LOW_FIDELITY,
            failures=tuple(fidelity_failures),
            fidelity_scores=tuple(scores),
        )

    return ValidationOutcome(
        verdict=ValidationVerdict.OK,
        verified=tuple(verified),
        fidelity_scores=tuple(scores),
    )
