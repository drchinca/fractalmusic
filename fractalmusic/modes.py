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


@dataclass(frozen=True)
class Mode:
    """A Gátople mode: the musical identity of one of the 12 worlds."""

    note: str  # canonical note name (A-order)
    mode_name: str  # e.g. "Eólico", "Penta 3"
    family: str  # HEPTA or PENTA
    glyph: str  # the world's symbol
    quality: str  # MAJOR / MINOR / DIMINISHED
    clock_hour: int  # position on the 12-hour Gátople face
    note_order: tuple[str, ...]  # the mode's scale, spelled from its own root


# Heptatonic modes — white keys (Ch. 4 & 8).
_HEPTA_MODES: Final[tuple[Mode, ...]] = (
    Mode("A", "Eólico", HEPTA, EOLICO, MINOR, 9, ("A", "B", "C", "D", "E", "F", "G")),
    Mode("B", "Locrio", HEPTA, LOCRIO, DIMINISHED, 7, ("B", "C", "D", "E", "F", "G", "A")),
    Mode("C", "Jónico", HEPTA, JONICO, MAJOR, 12, ("C", "D", "E", "F", "G", "A", "B")),
    Mode("D", "Dórico", HEPTA, DORICO, MINOR, 2, ("D", "E", "F", "G", "A", "B", "C")),
    Mode("E", "Frigio", HEPTA, FRIGIO, MINOR, 8, ("E", "F", "G", "A", "B", "C", "D")),
    Mode("F", "Lidio", HEPTA, LIDIO, MAJOR, 1, ("F", "G", "A", "B", "C", "D", "E")),
    Mode("G", "Mixolidio", HEPTA, MIXOLIDIO, MAJOR, 11, ("G", "A", "B", "C", "D", "E", "F")),
)

# Pentatonic modes — black keys (Ch. 4 & 9). note_order spelled per book.
_PENTA_MODES: Final[tuple[Mode, ...]] = (
    Mode("C#", "Penta 1", PENTA, "★", MINOR, 5, ("C#", "D#", "F#", "G#", "A#")),
    Mode("D#", "Penta 2", PENTA, "★", MINOR, 9, ("D#", "F#", "G#", "A#", "C#")),
    Mode("F#", "Penta 3", PENTA, "★", MAJOR, 6, ("F#", "G#", "C#", "A#", "D#")),
    Mode("G#", "Penta 4", PENTA, "★", MINOR, 3, ("G#", "A#", "C#", "D#", "F#")),
    Mode("A#", "Penta 5", PENTA, "★", MINOR, 1, ("A#", "C#", "D#", "F#", "G#")),
)

# Penta roman order follows penta-mode number: Penta1=I … Penta5=V.
PENTA_ROMAN_BY_NOTE: Final[dict[str, str]] = {
    "C#": "I",
    "D#": "II",
    "F#": "III",
    "G#": "IV",
    "A#": "V",
}

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
