"""Internal protocols the route depends on.

Keeping these as Protocols (not concrete classes) lets us inject either
the cemaf/meridian-backed real implementations *or* in-process fakes,
without ``patch()`` anywhere in tests.
"""

from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    """Whatever the retriever returns. Mirrors meridian's Chunk shape but
    avoids importing meridian into the protocol layer."""

    book_hash: str
    book_title: str
    chapter_idx: int
    section_idx: int
    paragraph_idx: int
    page_start: int
    text: str


class Retriever(Protocol):
    async def search(self, *, question: str, k: int) -> tuple[RetrievedChunk, ...]:
        """Return up to ``k`` chunks scoped to the fractal corpus."""
        ...


class LLM(Protocol):
    async def complete(self, *, system: str, user: str) -> str:
        """Single-turn completion: user message in, assistant text out."""
        ...


class Similarity(Protocol):
    async def __call__(self, claim: str, snippet: str) -> Awaitable[float] | float:
        ...
