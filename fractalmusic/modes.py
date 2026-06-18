"""The 12 modes of the Gátople clock — canonical data from the book.

Ch. 4 places each of the 12 chromatic notes at a clock hour, names it with a
Greek (heptatonic) or Penta (pentatonic) mode, and gives its quality. The seven
heptatonic modes live on the white keys; the five Penta modes on the black keys.

Clock convention (Ch. 4 & 8): A Eólico at 9 o'clock (the stable horizon / East),
moving through the cycle. The hours below are read directly from the text.
"""

from dataclasses import dataclass
from typing import Final

from fractalmusic.symbols import (
    BLACK_STAR,
    DORICO,
    EOLICO,
    FRIGIO,
    JONICO,
    LIDIO,
    LOCRIO,
    MIXOLIDIO,
)

HEPTA: Final[str] = "hepta"
PENTA: Final[str] = "penta"

MAJOR: Final[str] = "major"
MINOR: Final[str] = "minor"
DIMINISHED: Final[str] = "diminished"


# The chromatic A-order (matches pytheory's western system: A=0, C=3).
CHROMATIC_ORDER: Final[tuple[str, ...]] = (
    "A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#",
)

# The Gátople is a circle-of-FOURTHS clock ("Función Cuartal", Ch. 4): stepping a
# perfect fourth (+5 semitones) advances one hour, anchored at A Eólico = 9 o'clock.
# This bijection reproduces every clock hour the book names in prose:
#   A=9  C=12  F=1  G=11  B=7  F#=6  C#=5  E=8 ...  (all 12 hours distinct).
_HOUR_ANCHOR: Final[int] = 9  # A Eólico sits at 9 o'clock (the stable horizon, East)
_FOURTH_SEMITONES: Final[int] = 5


def _clock_hour(note: str) -> int:
    """The Gátople clock hour for a note, via the circle of fourths from A=9."""
    index = CHROMATIC_ORDER.index(note)
    return ((_HOUR_ANCHOR - 1 + _FOURTH_SEMITONES * index) % 12) + 1


@dataclass(frozen=True)
class Mode:
    """A Gátople mode: the musical identity of one of the 12 worlds."""

    note: str  # canonical note name (A-order)
    mode_name: str  # e.g. "Eólico", "Penta 3"
    family: str  # HEPTA or PENTA
    glyph: str  # the world's symbol
    quality: str  # MAJOR / MINOR / DIMINISHED
    clock_hour: int  # position on the 12-hour Gátople face (circle of fourths)
    note_order: tuple[str, ...]  # the mode's scale, spelled from its own root


def _hepta(note: str, name: str, glyph: str, quality: str) -> Mode:
    """Build a heptatonic mode rooted on a natural note (scale = 7 naturals rotated)."""
    start = "ABCDEFG".index(note)
    order = tuple("ABCDEFG"[(start + step) % 7] for step in range(7))
    return Mode(note, name, HEPTA, glyph, quality, _clock_hour(note), order)


def _penta(note: str, name: str, quality: str) -> Mode:
    """Build a pentatonic mode rooted on a black key (scale = black keys rotated)."""
    black = ("C#", "D#", "F#", "G#", "A#")
    start = black.index(note)
    order = tuple(black[(start + step) % 5] for step in range(5))
    return Mode(note, name, PENTA, BLACK_STAR, quality, _clock_hour(note), order)


# Heptatonic modes — white keys (Ch. 4 & 8).
_HEPTA_MODES: Final[tuple[Mode, ...]] = (
    _hepta("A", "Eólico", EOLICO, MINOR),
    _hepta("B", "Locrio", LOCRIO, DIMINISHED),
    _hepta("C", "Jónico", JONICO, MAJOR),
    _hepta("D", "Dórico", DORICO, MINOR),
    _hepta("E", "Frigio", FRIGIO, MINOR),
    _hepta("F", "Lidio", LIDIO, MAJOR),
    _hepta("G", "Mixolidio", MIXOLIDIO, MAJOR),
)

# Pentatonic modes — black keys (Ch. 4 & 9). Each is a rotation of the black-key cycle.
_PENTA_MODES: Final[tuple[Mode, ...]] = (
    _penta("C#", "Penta 1", MINOR),
    _penta("D#", "Penta 2", MINOR),
    _penta("F#", "Penta 3", MAJOR),
    _penta("G#", "Penta 4", MINOR),
    _penta("A#", "Penta 5", MINOR),
)

# Penta roman order follows penta-mode number: Penta1=I … Penta5=V.
# Single source of truth — consumed by showcase, gallery, dodecamundo, tests.
PENTA_ROOTS: Final[tuple[tuple[str, str], ...]] = (
    ("I", "C#"),
    ("II", "D#"),
    ("III", "F#"),
    ("IV", "G#"),
    ("V", "A#"),
)
PENTA_ROMAN_BY_NOTE: Final[dict[str, str]] = {note: roman for roman, note in PENTA_ROOTS}

MODE_BY_NOTE: Final[dict[str, Mode]] = {}
for _mode in (*_HEPTA_MODES, *_PENTA_MODES):
    MODE_BY_NOTE[_mode.note] = _mode

ALL_MODES: Final[tuple[Mode, ...]] = (*_HEPTA_MODES, *_PENTA_MODES)


def mode_for(note: str) -> Mode:
    """Return the canonical Mode for a natural or sharp note name."""
    try:
        return MODE_BY_NOTE[note]
    except KeyError as error:
        raise ValueError(f"no mode for note {note!r}") from error
