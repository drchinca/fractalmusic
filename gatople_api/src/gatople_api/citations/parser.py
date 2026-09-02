"""Parse ``[<hash> ch<N>§<M>¶<P> p.<page>]`` markers from LLM answer text.

The grammar is permissive — the prompt asks for the canonical glyphs, but
real LLMs drift to ASCII separators 2% of the time and we don't want
regeneration storms over cosmetics. The membership *tuple* is what's
load-bearing, not the middle-dot. Spec §2.3.
"""

import re
from dataclasses import dataclass

# Permissive separator class: middle-dot, period, colon, hyphen, or whitespace.
_SEP = r"[·.:\-\s]"

CITATION_RE = re.compile(
    rf"\[(?P<book>[a-f0-9]{{8}})"
    rf"\s*{_SEP}\s*ch(?P<ch>\d+)"
    rf"\s*[§{_SEP[1:-1]}]\s*(?P<sec>\d+)"
    rf"\s*[¶{_SEP[1:-1]}]\s*(?P<para>\d+)"
    rf"\s+p\.?\s*(?P<page>\d+)\]"
)

# Sentence boundary on `.`, `;`, `:`, `?` (Spanish opener `¿` doesn't end one).
_SENTENCE_END_RE = re.compile(r"(?<=[.;:?])\s+")


@dataclass(frozen=True, slots=True)
class ParsedCitation:
    """A citation marker extracted from text, before membership/fidelity checks."""

    book_hash: str
    chapter_idx: int
    section_idx: int
    paragraph_idx: int
    page_start: int
    raw: str  # the literal `[…]` matched, for error messages


@dataclass(frozen=True, slots=True)
class CitedClaim:
    """One sentence and the citations that immediately followed it."""

    sentence: str  # trimmed, no trailing whitespace
    citations: tuple[ParsedCitation, ...]


def _to_parsed(match: re.Match[str]) -> ParsedCitation:
    return ParsedCitation(
        book_hash=match["book"],
        chapter_idx=int(match["ch"]),
        section_idx=int(match["sec"]),
        paragraph_idx=int(match["para"]),
        page_start=int(match["page"]),
        raw=match.group(0),
    )


def parse_answer(text: str) -> tuple[CitedClaim, ...]:
    """Split ``text`` into sentences and attach citation markers to each.

    A marker belongs to the sentence whose end-punctuation precedes it (and
    whose next end-punctuation, if any, comes after it). Markers that
    appear before any end-punctuation are dropped — the prompt requires
    a sentence terminator before the citation.
    """
    sentences = [s.strip() for s in _SENTENCE_END_RE.split(text) if s.strip()]
    out: list[CitedClaim] = []
    for sentence in sentences:
        cites = tuple(_to_parsed(m) for m in CITATION_RE.finditer(sentence))
        # Strip the citations from the sentence text itself for cleaner display
        bare = CITATION_RE.sub("", sentence).strip()
        out.append(CitedClaim(sentence=bare, citations=cites))
    return tuple(out)
