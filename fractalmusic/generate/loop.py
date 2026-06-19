"""Self-learning research loop: corpus → expert → realize → score → persist."""

import json
from pathlib import Path
from typing import Final, Protocol

from fractalmusic.generate.adapters import to_web_payload
from fractalmusic.generate.realize import realize
from fractalmusic.generate.scoring import score as score_events
from fractalmusic.generate.types import (
    PENTA_MODES,
    Event,
    GenerationRequest,
    GenerationResult,
    Pattern,
    Provenance,
    Score,
)

N_CANDIDATES: Final[int] = 5
SCORE_THRESHOLD: Final[float] = 0.75


class ExpertClient(Protocol):
    def query(self, request: GenerationRequest) -> Pattern: ...


class PatternCorpus(Protocol):
    def find(self, request: GenerationRequest) -> list[Pattern]: ...
    def append(self, pattern: Pattern, score: Score) -> None: ...


class StubExpert:
    """Deterministic in-process 'expert' — returns book-anchored skeletons.

    Real implementation wires CEMAF + meridian; the stub keeps the loop testable
    without network calls and gives the system a sane default before the agent
    is wired up.
    """

    _PROVENANCE: Final[Provenance] = Provenance(
        book_hash="b202598c",
        book_title="El Sistema Fractal (Patricio Torres, 2024)",
        chapter="Cap. 4 — La rueda y los modos",
        page=None,
        quote="El centro es A; los modos giran sobre la rueda.",
    )

    def query(self, request: GenerationRequest) -> Pattern:
        is_penta = request.mode in PENTA_MODES
        max_degree = 5 if is_penta else 7
        # PHI-flavored degree walk: alternate small / golden-ish jumps.
        walk: list[int] = []
        cursor = 1
        for i in range(request.length_events):
            walk.append(((cursor - 1) % max_degree) + 1)
            cursor += 2 if i % 3 == 0 else 1
        if request.flavor == "carta-progression":
            base = [1, 4, 5, 1]
            walk = [base[i % len(base)] for i in range(request.length_events)]
        rhythm = tuple(1.0 for _ in walk)
        return Pattern(
            name=f"{request.flavor}:{request.tonic}-{request.mode}",
            tonic=request.tonic,
            mode=request.mode,
            degrees=tuple(walk),
            rhythm=rhythm,
            provenance=self._PROVENANCE,
        )


class JsonCorpus:
    """File-backed corpus under `patterns/` (JSON-per-pattern, BE-only)."""

    def __init__(self, root: Path) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)

    def _key_for_pattern(self, pattern: Pattern) -> str:
        return f"{pattern.tonic}_{pattern.mode}".replace(" ", "")

    def _key_for_request(self, request: GenerationRequest) -> str:
        return f"{request.tonic}_{request.mode}".replace(" ", "")

    def find(self, request: GenerationRequest) -> list[Pattern]:
        prefix = self._key_for_request(request)
        patterns: list[Pattern] = []
        for path in sorted(self._root.glob(f"{prefix}__*.json")):
            with path.open(encoding="utf-8") as fh:
                patterns.append(Pattern.from_dict(json.load(fh)))
        return patterns

    def append(self, pattern: Pattern, score: Score) -> None:
        key = self._key_for_pattern(pattern)
        safe_name = pattern.name.replace("/", "_").replace(" ", "")
        target = self._root / f"{key}__{safe_name}_{int(score.total * 1000):03d}.json"
        with target.open("w", encoding="utf-8") as fh:
            json.dump(
                {**pattern.to_dict(), "_score": score.total},
                fh,
                ensure_ascii=False,
                indent=2,
            )


def _adapt_length(pattern: Pattern, length: int) -> Pattern:
    """Stretch/truncate a corpus-loaded pattern to the requested length."""
    if len(pattern.degrees) == length:
        return pattern
    degrees = tuple(pattern.degrees[i % len(pattern.degrees)] for i in range(length))
    rhythm = tuple(pattern.rhythm[i % len(pattern.rhythm)] for i in range(length))
    return Pattern(
        name=pattern.name,
        tonic=pattern.tonic,
        mode=pattern.mode,
        degrees=degrees,
        rhythm=rhythm,
        provenance=pattern.provenance,
    )


def research_loop(
    request: GenerationRequest,
    *,
    expert: ExpertClient,
    corpus: PatternCorpus,
) -> GenerationResult:
    """Best-of-N over corpus + expert candidates. Persists winners."""
    candidates: list[Pattern] = [
        _adapt_length(p, request.length_events) for p in corpus.find(request)
    ]
    while len(candidates) < N_CANDIDATES:
        candidates.append(expert.query(request))

    best: tuple[Pattern, tuple[Event, ...], Score] | None = None
    for i, pattern in enumerate(candidates[:N_CANDIDATES]):
        events = realize(pattern, seed=i)
        s = score_events(events=events, pattern=pattern)
        if best is None or s.total > best[2].total:
            best = (pattern, events, s)

    if best is None:
        raise RuntimeError("research_loop produced no candidates")
    pattern, events, s = best
    if s.total >= SCORE_THRESHOLD:
        corpus.append(pattern, s)

    return GenerationResult(
        pattern=pattern,
        events=events,
        score=s,
        midi_path=None,
        web_payload=to_web_payload(pattern=pattern, events=events, score=s),
    )
