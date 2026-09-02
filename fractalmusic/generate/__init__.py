"""Fractal music generator — BE-only logic, FE just renders.

Public surface is enumerated in ``__all__`` below. Anything not re-exported
is internal — import paths are not stable.
"""

from fractalmusic.generate.adapters import (
    MidiUnavailable,
    to_midi,
    to_strudel_code,
    to_strudel_payload,
    to_web_payload,
)
from fractalmusic.generate.loop import (
    ExpertClient,
    JsonCorpus,
    PatternCorpus,
    StubExpert,
    research_loop,
)
from fractalmusic.generate.realize import realize
from fractalmusic.generate.scoring import score
from fractalmusic.generate.types import (
    CandidateTrace,
    Event,
    Flavor,
    GenerationRequest,
    GenerationResult,
    GenerationTrace,
    ModeName,
    NoteName,
    Pattern,
    Provenance,
    Score,
    StrudelBookGuidancePayload,
    StrudelPayload,
    WebPayload,
)

__all__ = [
    "CandidateTrace",
    "Event",
    "ExpertClient",
    "Flavor",
    "GenerationRequest",
    "GenerationResult",
    "GenerationTrace",
    "JsonCorpus",
    "MidiUnavailable",
    "ModeName",
    "NoteName",
    "Pattern",
    "PatternCorpus",
    "Provenance",
    "Score",
    "StrudelBookGuidancePayload",
    "StrudelPayload",
    "StubExpert",
    "WebPayload",
    "realize",
    "research_loop",
    "score",
    "to_midi",
    "to_strudel_code",
    "to_strudel_payload",
    "to_web_payload",
]
