"""Types for the fractal music generator. Frozen dataclasses + Literal closed sets."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, TypedDict, get_args

NoteName = Literal["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
ModeName = Literal[
    "Eólico",
    "Locrio",
    "Jónico",
    "Dórico",
    "Frigio",
    "Lidio",
    "Mixolidio",
    "PentaI",
    "PentaII",
    "PentaIII",
    "PentaIV",
    "PentaV",
]
Flavor = Literal["penta-walk", "carta-progression", "free"]
ConfidenceBand = Literal["strong", "tentative", "exploratory"]

NOTE_NAMES: frozenset[str] = frozenset(get_args(NoteName))
MODE_NAMES: frozenset[str] = frozenset(get_args(ModeName))
FLAVORS: frozenset[str] = frozenset(get_args(Flavor))
PENTA_MODES: frozenset[str] = frozenset({"PentaI", "PentaII", "PentaIII", "PentaIV", "PentaV"})


@dataclass(frozen=True, slots=True)
class Provenance:
    book_hash: str
    book_title: str
    chapter: str | None = None
    page: int | None = None
    quote: str | None = None


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    tonic: NoteName
    mode: ModeName
    length_events: int
    flavor: Flavor = "free"
    free_text: str | None = None

    def __post_init__(self) -> None:
        if self.tonic not in NOTE_NAMES:
            raise ValueError(f"unknown tonic: {self.tonic!r}")
        if self.mode not in MODE_NAMES:
            raise ValueError(f"unknown mode: {self.mode!r}")
        if self.flavor not in FLAVORS:
            raise ValueError(f"unknown flavor: {self.flavor!r}")
        if not 4 <= self.length_events <= 64:
            raise ValueError("length_events must be in 4..64")


@dataclass(frozen=True, slots=True)
class Pattern:
    name: str
    tonic: NoteName
    mode: ModeName
    degrees: tuple[int, ...]
    rhythm: tuple[float, ...]
    provenance: Provenance

    def __post_init__(self) -> None:
        if self.tonic not in NOTE_NAMES:
            raise ValueError(f"unknown tonic: {self.tonic!r}")
        if self.mode not in MODE_NAMES:
            raise ValueError(f"unknown mode: {self.mode!r}")
        if not self.degrees:
            raise ValueError("degrees must be non-empty")
        if len(self.rhythm) != len(self.degrees):
            raise ValueError("rhythm length must match degrees length")
        max_degree = 5 if self.mode in PENTA_MODES else 7
        if not all(1 <= d <= max_degree for d in self.degrees):
            raise ValueError(f"degrees must be in 1..{max_degree} for mode {self.mode!r}")
        if not self.provenance.book_hash or not self.provenance.book_title:
            raise ValueError("Provenance requires book_hash and book_title")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Pattern":
        prov = data["provenance"]
        return cls(
            name=data["name"],
            tonic=data["tonic"],
            mode=data["mode"],
            degrees=tuple(data["degrees"]),
            rhythm=tuple(float(x) for x in data["rhythm"]),
            provenance=Provenance(
                book_hash=prov["book_hash"],
                book_title=prov["book_title"],
                chapter=prov.get("chapter"),
                page=prov.get("page"),
                quote=prov.get("quote"),
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "tonic": self.tonic,
            "mode": self.mode,
            "degrees": list(self.degrees),
            "rhythm": list(self.rhythm),
            "provenance": {
                "book_hash": self.provenance.book_hash,
                "book_title": self.provenance.book_title,
                "chapter": self.provenance.chapter,
                "page": self.provenance.page,
                "quote": self.provenance.quote,
            },
        }


@dataclass(frozen=True, slots=True)
class Event:
    note: NoteName
    octave: int
    beat: float
    duration: float
    time_sec: float
    freq_hz: float
    role_hour: int
    carta_glyph: str


@dataclass(frozen=True, slots=True)
class Score:
    total: float
    mode_membership: float
    rhythmic_coherence: float
    fractal_shape: float
    breaches: tuple[str, ...] = field(default_factory=tuple)

    @property
    def band(self) -> ConfidenceBand:
        if self.total >= 0.85:
            return "strong"
        if self.total >= 0.75:
            return "tentative"
        return "exploratory"


class ConfidencePayload(TypedDict):
    score: float
    band: ConfidenceBand


class EventPayload(TypedDict):
    note: str
    octave: int
    beat: float
    duration: float
    time_sec: float
    freq_hz: float
    role_hour: int
    carta_glyph: str


class ProvenancePayload(TypedDict):
    book_hash: str
    book_title: str
    chapter: str | None
    page: int | None
    quote: str | None


class WebPayload(TypedDict):
    schema_version: int
    pattern_name: str
    bpm: int
    tonic: str
    mode: str
    key_label: str
    total_beats: float
    requires_user_gesture: bool
    confidence: ConfidencePayload
    events: list[EventPayload]
    provenance: ProvenancePayload
    audio_url: str | None


class StrudelPayload(TypedDict):
    schema_version: int
    pattern_name: str
    bpm: int
    total_beats: float
    code: str
    generated_from: WebPayload
    book_guidance: list["StrudelBookGuidancePayload"]
    warnings: list[str]


class StrudelBookGuidancePayload(TypedDict):
    book_hash: str
    book_title: str
    chapter_idx: int
    section_idx: int
    paragraph_idx: int
    page_start: int
    snippet: str
    strudel_use: str


@dataclass(frozen=True, slots=True)
class CandidateTrace:
    """One candidate research_loop actually considered, and what happened
    to it — not just the winner. Source is "corpus" (a pattern already
    persisted for this tonic/mode/flavor) or "expert" (freshly queried
    this run, StubExpert/LLMExpert/whichever ExpertClient was passed in).
    """

    source: str  # "corpus" | "expert"
    pattern_name: str
    score_total: float
    won: bool


@dataclass(frozen=True, slots=True)
class GenerationTrace:
    """What research_loop actually did, for audit/provenance — every
    candidate it weighed, not just the one that made it into the response.

    This is the "what created what and how" record: whether the winner
    came from the corpus or was freshly composed, and what it beat to get
    there. Two real bugs this session (a stale corpus pattern silently
    outscoring a fresh free-text/flavor-specific composition) were only
    findable by manually re-deriving this by hand — this makes it visible
    directly, without needing to reproduce the bug to see it.
    """

    candidates: tuple[CandidateTrace, ...]
    winner_source: str  # "corpus" | "expert"


@dataclass(frozen=True, slots=True)
class GenerationResult:
    pattern: Pattern
    events: tuple[Event, ...]
    score: Score
    midi_path: Path | None
    web_payload: WebPayload
    trace: GenerationTrace
