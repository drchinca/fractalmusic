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
from fractalmusic.modes import ALL_MODES, Mode, mode_for
from fractalmusic.scales import (
    FractalScale,
    microstructures,
    mode_scale,
    penta,
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
    "penta",
    "microstructures",
    "mode_scale",
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
    "is_valid_pattern",
]
