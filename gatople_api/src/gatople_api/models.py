"""Pydantic models exposed across the BFF/web boundary. Spec §2.2."""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# The two indexed fractal books, by short prefix.
# Meridian stores full sha256 book hashes; we match by prefix so consumers
# can keep using the friendly 8-char short form everywhere.
SCOPE_PREFIXES: tuple[str, ...] = ("f39cb7c5", "b202598c")


def in_scope(book_hash: str) -> bool:
    """True iff ``book_hash`` starts with one of the SCOPE_PREFIXES."""
    return any(book_hash.startswith(p) for p in SCOPE_PREFIXES)


def short_hash(book_hash: str) -> str:
    """Render the friendly 8-char prefix used in citations + UI."""
    return book_hash[:8]


# Backwards-compatible alias for tests / older imports.
SCOPE = SCOPE_PREFIXES


class LLMChoice(StrEnum):
    CLAUDE = "claude"
    OLLAMA = "ollama"


class ChatRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    question: Annotated[str, Field(min_length=3, max_length=500)]
    llm: LLMChoice = LLMChoice.CLAUDE


class Citation(BaseModel):
    """A retrieved chunk. ``verified`` is True when the validator confirmed
    the snippet supports an inline claim in ``ChatResponse.answer``; False
    when the chunk was retrieved but the answer didn't ground itself in it
    (returned for the FE's "here's what I found" panel)."""

    model_config = ConfigDict(frozen=True)
    book_hash: str
    book_title: str
    chapter_idx: int
    section_idx: int
    paragraph_idx: int
    page_start: int
    snippet: Annotated[str, Field(max_length=2000)]
    verified: bool = False


class ChatResponse(BaseModel):
    """Either ``answer`` (verified path) or ``model_reading`` (interpretive
    fallback) is populated, never both. When retrieval was empty, both are
    None and ``reason`` is ``"no_evidence_in_corpus"``."""

    model_config = ConfigDict(frozen=True)
    llm: LLMChoice
    answer: str | None
    citations: tuple[Citation, ...] = ()
    model_reading: str | None = None
    reason: str | None = None
    elapsed_ms: Annotated[int, Field(ge=0)]
