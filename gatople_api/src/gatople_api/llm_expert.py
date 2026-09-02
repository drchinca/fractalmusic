"""LLMExpert — turns a free-text mood/style description into a real Pattern.

Implements fractalmusic.generate.loop.ExpertClient. Reuses the same LLM
client already wired for /api/chat (gatople_api.protocols.LLM) — no new
LLM infrastructure, just a new prompt and a new adapter at the boundary.

The ExpertClient Protocol is synchronous (research_loop calls it in a plain
loop), but LLM.complete() is async — that impedance mismatch is bridged
entirely here, not by pushing async-ness into fractalmusic's core, which
stays dependency-light and has no async anything today.
"""

import asyncio
import concurrent.futures
import json
from typing import Any, Final

import structlog
from fractalmusic.generate.loop import StubExpert
from fractalmusic.generate.types import (
    MODE_NAMES,
    NOTE_NAMES,
    PENTA_MODES,
    GenerationRequest,
    Pattern,
    Provenance,
)

from gatople_api import prompts
from gatople_api.protocols import LLM

log = structlog.get_logger("gatople_api.llm_expert")

_MAX_ATTEMPTS: Final[int] = 2  # one try, one retry, then fall back to StubExpert
_MIN_DEGREES: Final[int] = 4
_MAX_DEGREES: Final[int] = 32

# LLM-composed patterns are not from the book corpus — never fabricate a
# real-looking [hash] citation for them (this project's own citation-
# honesty standard, learned the hard way earlier in this repo's history).
_LLM_BOOK_HASH: Final[str] = "llm-composed"
_LLM_BOOK_TITLE: Final[str] = "Generado por IA a partir de una descripción"


def _run_async(coro: Any) -> Any:
    """Run an async call from sync code, whether or not a loop is already
    running on this thread (the sync /api/generate route and the async
    /api/generate/strudel route both end up here)."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


def _extract_json(text: str) -> dict[str, Any]:
    """Parse the LLM's response as JSON, tolerating a ```json fence even
    though the prompt asks for none — models don't always comply."""
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.startswith("json"):
            stripped = stripped[4:]
        stripped = stripped.strip()
    data = json.loads(stripped)
    if not isinstance(data, dict):
        raise ValueError(f"expected a JSON object, got {type(data).__name__}")
    return data


def _pattern_from_llm_json(data: dict[str, Any], *, free_text: str) -> Pattern:
    """Validate and construct a Pattern from the LLM's chosen fields.

    Deliberately re-checks the closed sets and length constraints before
    handing off to Pattern.__post_init__ — a clear ValueError here (vs. a
    dict-indexing KeyError) is what the retry/fallback logic catches.
    """
    tonic = data["tonic"]
    mode = data["mode"]
    degrees = [int(d) for d in data["degrees"]]
    rhythm = [float(r) for r in data["rhythm"]]

    if tonic not in NOTE_NAMES:
        raise ValueError(f"LLM chose an unknown tonic: {tonic!r}")
    if mode not in MODE_NAMES:
        raise ValueError(f"LLM chose an unknown mode: {mode!r}")
    if not _MIN_DEGREES <= len(degrees) <= _MAX_DEGREES:
        raise ValueError(f"LLM produced {len(degrees)} degrees, want {_MIN_DEGREES}..{_MAX_DEGREES}")
    max_degree = 5 if mode in PENTA_MODES else 7
    if not all(1 <= d <= max_degree for d in degrees):
        raise ValueError(f"LLM degree out of range 1..{max_degree} for mode {mode!r}: {degrees}")

    return Pattern(
        name=f"describe:{tonic}-{mode}",
        tonic=tonic,
        mode=mode,
        degrees=tuple(degrees),
        rhythm=tuple(rhythm),
        provenance=Provenance(
            book_hash=_LLM_BOOK_HASH,
            book_title=_LLM_BOOK_TITLE,
            quote=free_text,
        ),
    )


class LLMExpert:
    """Real ExpertClient backed by an LLM. Falls back to StubExpert on
    repeated failure — a bad LLM response degrades gracefully, it never
    breaks the request."""

    def __init__(self, *, llm: LLM) -> None:
        self._llm = llm
        self._fallback = StubExpert()

    def query(self, request: GenerationRequest) -> Pattern:
        free_text = request.free_text
        if not free_text:
            # No description given — nothing for the LLM to compose from.
            return self._fallback.query(request)

        prompt = prompts.load("compose_from_text")
        system = prompts.render_compose(prompt.template, free_text=free_text)

        last_error: Exception | None = None
        for attempt in range(1, _MAX_ATTEMPTS + 1):
            try:
                raw = _run_async(self._llm.complete(system=system, user=free_text))
                data = _extract_json(raw)
                return _pattern_from_llm_json(data, free_text=free_text)
            except (json.JSONDecodeError, ValueError, KeyError, TypeError) as error:
                last_error = error
                log.warning(
                    "llm_expert.attempt_failed",
                    attempt=attempt,
                    max_attempts=_MAX_ATTEMPTS,
                    error=str(error),
                )

        log.warning("llm_expert.fallback_to_stub", error=str(last_error))
        return self._fallback.query(request)
