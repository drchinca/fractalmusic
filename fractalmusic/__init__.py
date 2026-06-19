"""fractalmusic — Patricio Torres's Sistema Fractal, built on pytheory.

The Dodecamundo (12 note-worlds), the Gátople clock, the 12 Greek + Penta modes,
pentatonic-first scales, the 12 cartas, and the etno-matemática chord formulas —
A-origin throughout, with canonical bindings from *El Sistema Fractal* (2024).
"""

from fractalmusic.cartas import carta, deck, piano_stickers, spell
from fractalmusic.dodecamundo import (
    DODECAMUNDO,
    NoteWorld,
    heptatonic_worlds,
    pentatonic_worlds,
    world,
    world_by_glyph,
)
from fractalmusic.formulas import (
    PHI,
    chessboard_grains,
    consonance,
    fibonacci,
    fibonacci_chord,
    interval_ratio,
    self_squaring_grains,
)
from fractalmusic.gatople import (
    POSITIONS,
    cero_pitagoras,
    clock_hour,
    interval_angle,
    polygon,
    position,
    rotate,
)
from fractalmusic.generate import (
    Event as GeneratedEvent,
)
from fractalmusic.generate import (
    GenerationRequest,
    GenerationResult,
    JsonCorpus,
    Provenance,
    StubExpert,
    realize,
    research_loop,
    to_midi,
    to_web_payload,
)
from fractalmusic.generate import (
    Pattern as GenerationPattern,
)
from fractalmusic.generate import (
    Score as GenerationScore,
)
from fractalmusic.generate import (
    score as score_generation,
)
from fractalmusic.modes import ALL_MODES, Mode, mode_for
from fractalmusic.scales import (
    FractalScale,
    Triad,
    microstructures,
    mode_scale,
    penta,
    triad_for,
)
from fractalmusic.wheel import (
    ROLES,
    Role,
    Wheel,
    WheelMode,
    generate_scale,
    generate_twelve_outputs,
    is_valid_pattern,
    spin,
    validate_pattern,
)

__all__ = [
    # dodecamundo
    "DODECAMUNDO",
    "NoteWorld",
    "world",
    "world_by_glyph",
    "pentatonic_worlds",
    "heptatonic_worlds",
    # modes
    "Mode",
    "ALL_MODES",
    "mode_for",
    # gatople
    "POSITIONS",
    "position",
    "interval_angle",
    "clock_hour",
    "polygon",
    "cero_pitagoras",
    "rotate",
    # scales
    "FractalScale",
    "Triad",
    "penta",
    "microstructures",
    "mode_scale",
    "triad_for",
    # cartas
    "carta",
    "deck",
    "piano_stickers",
    "spell",
    # formulas
    "PHI",
    "fibonacci",
    "fibonacci_chord",
    "chessboard_grains",
    "self_squaring_grains",
    "interval_ratio",
    "consonance",
    # wheel (the spinning Gátople)
    "Wheel",
    "WheelMode",
    "Role",
    "ROLES",
    "spin",
    "generate_scale",
    "generate_twelve_outputs",
    "validate_pattern",
    "is_valid_pattern",  # alias retained for back-compat
    # generate (research loop)
    "GenerationRequest",
    "GenerationResult",
    "GenerationPattern",
    "GenerationScore",
    "GeneratedEvent",
    "Provenance",
    "JsonCorpus",
    "StubExpert",
    "realize",
    "research_loop",
    "score_generation",
    "to_midi",
    "to_web_payload",
]
