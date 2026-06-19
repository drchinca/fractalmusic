# SPEC-fractal-generator

> Generate music on demand from the Sistema Fractal — a research loop that pulls
> patterns from the indexed books, realizes them through `Wheel` + pytheory, and
> learns from each successful run. **All theory lives in BE; FE plays inert
> JSON** (CLAUDE.md cardinal 6).

## 1. Context

Today the core teaches the wheel; it does not *play* it. Users want to ask "give
me something in A Eólico, fractal-shaped" and hear it. The book is full of
generation recipes (penta skeletons, carta progressions, etno-matemática
ratios) — they exist as prose, not as code.

This spec adds `fractalmusic.generate`: turns a structured request into played
music via a research → realize → score loop, and **learns** by appending winning
patterns to `patterns/*.yaml` so the next request reads the corpus before re-
querying the books.

```mermaid
sequenceDiagram
  actor User
  participant Loop as research_loop
  participant Corpus as patterns/*.yaml
  participant Expert as ExpertClient (CEMAF + meridian)
  participant Realize as realize()
  participant Score as score()
  User->>Loop: GenerationRequest
  Loop->>Corpus: read matching patterns
  alt corpus hit
    Corpus-->>Loop: Pattern (cited)
  else miss
    Loop->>Expert: query(books=fractal hashes)
    Expert-->>Loop: Pattern (cited)
  end
  loop best-of-5
    Loop->>Realize: realize(pattern, wheel)
    Realize-->>Loop: events
    Loop->>Score: score(events, pattern)
    Score-->>Loop: total + breaches
  end
  Loop->>Corpus: append winner if total >= 0.75
  Loop-->>User: GenerationResult (events, MIDI, web payload)
```

## 2. Interface

```python
# fractalmusic/generate/types.py
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol, TypedDict

NoteName = Literal["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]
ModeName = Literal[                # mirrors ALL_MODES; single source in modes.py
    "Eólico","Locrio","Jónico","Dórico","Frigio","Lidio","Mixolidio",
    "PentaI","PentaII","PentaIII","PentaIV","PentaV",
]
Flavor = Literal["penta-walk","carta-progression","free"]

@dataclass(frozen=True, slots=True)
class Provenance:
    book_hash: str            # f39cb7c5 | b202598c | local
    book_title: str           # "Fractal Music World 2025" — shown to user
    chapter: str | None
    page: int | None
    quote: str | None         # ≤140 chars — the line a musician sees

@dataclass(frozen=True, slots=True)
class GenerationRequest:
    tonic: NoteName
    mode: ModeName
    length_events: int        # 4..64
    flavor: Flavor = "free"
    free_text: str | None = None   # optional NL hint to the expert

@dataclass(frozen=True, slots=True)
class Pattern:
    name: str
    tonic: NoteName
    mode: ModeName
    degrees: tuple[int, ...]  # 1..5 for penta modes, 1..7 for hepta
    rhythm: tuple[float, ...] # beats per event; len(rhythm) == len(degrees)
    provenance: Provenance

@dataclass(frozen=True, slots=True)
class Event:
    note: NoteName
    octave: int               # 3..5
    beat: float               # absolute beat offset
    duration: float           # beats
    time_sec: float           # PRE-BAKED; FE never multiplies bpm
    freq_hz: float            # PRE-BAKED; FE never computes from note name
    role_hour: int            # 1..12, the carta the FE highlights
    carta_glyph: str          # the painted card glyph

@dataclass(frozen=True, slots=True)
class Score:
    total: float              # 0..1
    mode_membership: float
    rhythmic_coherence: float
    fractal_shape: float      # PHI-aware ratio score from formulas.py
    breaches: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class GenerationResult:
    pattern: Pattern
    events: tuple[Event, ...]
    score: Score
    midi_path: Path | None
    web_payload: WebPayload   # ready to write to web/public/generated/

class WebPayload(TypedDict):
    schema_version: int       # 1
    pattern_name: str
    bpm: int
    tonic: NoteName
    mode: ModeName
    key_label: str            # pre-baked "A Eólico" — FE never formats
    total_beats: float
    requires_user_gesture: bool   # always True (iOS/Safari)
    confidence: dict          # {"score": 0.78, "band": "tentative"}
    events: list[dict]
    provenance: dict          # mirrors Provenance with human fields
```

```python
# fractalmusic/generate/__init__.py
def realize(pattern: Pattern, *, seed: int = 0) -> tuple[Event, ...]: ...
def score(events: tuple[Event, ...], pattern: Pattern) -> Score: ...
def to_midi(events: tuple[Event, ...], path: Path, *, bpm: int = 96) -> Path: ...
def to_web_payload(
    pattern: Pattern, events: tuple[Event, ...], score: Score, *, bpm: int = 96
) -> WebPayload: ...

# fractalmusic/generate/loop.py
class ExpertClient(Protocol):
    def query(self, request: GenerationRequest) -> Pattern: ...

class PatternCorpus(Protocol):
    def find(self, request: GenerationRequest) -> list[Pattern]: ...
    def append(self, pattern: Pattern, score: Score) -> None: ...

def research_loop(
    request: GenerationRequest,
    *,
    expert: ExpertClient,
    corpus: PatternCorpus,
) -> GenerationResult: ...    # n_candidates=5, threshold=0.75 are constants
```

Corpus is `patterns/*.json` (JSON over YAML — zero new deps). Loaded via
`Pattern.from_dict()` with manual boundary validation (Literal checks, length
matches, provenance presence). Pydantic deferred until a second YAML/JSON
boundary appears. `mido` is an optional dep (`[project.optional-dependencies]
midi`); `to_midi` raises `MidiUnavailable` when missing.

Confidence bands: `≥0.85 strong`, `0.75..0.85 tentative`, `<0.75 exploratory`.
Exploratory results are still returned, with the band shown.

Generated JSON is committed to `web/public/generated/<slug>.json` like the
existing `data.json` — Vite serves them as static assets. Runtime writes from
the Python loop are dev-time; production deploys ship committed payloads.

## 3. Invariants

(See CLAUDE.md cardinals 1–6 — A-origin, function-on-the-wheel, two-disc, penta-
first, cartas canonical, BE-owns-logic. Spec-local additions only:)

1. **Mode-tone membership.** Every `Event.note` is in
   `Wheel(pattern.tonic).mode_for(<degree-derived-note>).scale_notes()`. Out-of-
   mode notes lower `score.mode_membership`, never raise — soft scoring per
   project decision.
2. **Provenance required.** No `Pattern` exists without a `Provenance` carrying
   `book_hash` + `book_title`. YAML missing either fails Pydantic validation.
3. **Pre-baked rendering.** `time_sec`, `freq_hz`, `role_hour`, `carta_glyph`,
   and `key_label` are computed by BE and present in every `WebPayload`. FE
   imports zero music-theory constants.

Budget: ≤5 invariants. Used 3.

## 4. Acceptance

```gherkin
Feature: Generate music from a fractal request

Scenario: A Eólico penta walk
  Given a GenerationRequest(tonic="A", mode="Eólico", length_events=8, flavor="penta-walk")
  When research_loop runs with stub ExpertClient + in-memory PatternCorpus
  Then every Event.note is in Wheel("A").penta scale notes
  And score.total >= 0.75
  And web_payload["events"][0] has time_sec == 0.0
  And web_payload["confidence"]["band"] in {"strong","tentative"}

Scenario: Carta progression in F
  Given a GenerationRequest(tonic="F", mode="Eólico", length_events=4, flavor="carta-progression")
  When research_loop runs
  Then events[].role_hour visit cartas in the order requested by the pattern
  And every Event.carta_glyph matches Wheel("F") at that role_hour

Scenario: Out-of-mode candidate is scored down
  Given a Pattern claiming Eólico with degrees that imply Dórico
  When score(events, pattern) is called
  Then score.mode_membership < 0.6
  And "mode-tone violation" in score.breaches

Scenario: Successful patterns persist
  Given research_loop returns score.total >= 0.75
  When the loop finishes
  Then corpus.append was called once
  And the next call for the same request reads the corpus before the expert

Scenario: Web app stays a renderer
  Given a generated WebPayload
  Then events carry pre-baked time_sec and freq_hz
  And web_payload["requires_user_gesture"] is True
  And no file under web/src/ imports anything from fractalmusic theory modules
```

## 5. Out of scope

- DAW VST plugins, real-time MIDI input, microtonal tunings.
- Aesthetic scoring beyond fractal correctness (mode/rhythm/PHI).
- Cross-book corpus expansion. Loop queries only the two indexed fractal hashes.
- Generic browser synth — minimum WebAudio scheduler reading the emitted JSON.
- Hard-gated UAT. Soft scoring with best-of-5 + 0.75 threshold (project decision).
- Free-text `request: str` parser. v1 takes only the structured `GenerationRequest`.
