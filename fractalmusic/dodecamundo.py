"""The Dodecamundo — the 12 note-worlds of the Sistema Fractal.

Each chromatic note is a "world" carrying a mode, glyph, color, number, and (for
the 5 pentatonic black keys) a roman numeral. Built on pytheory's ``western``
system, which is natively A-indexed — matching Pattorres's principle of measuring
music from La (A), not Do (C).
"""

from dataclasses import dataclass
from typing import Final

from pytheory import Tone
from pytheory.systems import SYSTEMS

from fractalmusic.colors import WHEEL_HEX
from fractalmusic.modes import PENTA_ROMAN_BY_NOTE, Mode, mode_for

WESTERN = SYSTEMS["western"]

# pytheory's western tone order: A is index 0, C is index 3.
TONE_NAMES: Final[tuple[str, ...]] = tuple(names[0] for names in WESTERN.tone_names)

# Black keys (the 5 pentatonic stars) live at these chromatic indices.
BLACK_KEY_INDICES: Final[tuple[int, ...]] = (1, 4, 6, 9, 11)  # A# C# D# F# G#


@dataclass(frozen=True)
class NoteWorld:
    """One of the 12 worlds of the Dodecamundo."""

    index: int  # chromatic position, A = 0
    note: str  # canonical pytheory name, e.g. "A", "A#"
    mode: Mode  # the canonical Gátople mode
    color_hex: str  # color-wheel hue for this world
    number: int  # 1-based human number (index + 1)
    roman: str | None  # roman numeral I-V for pentatonic stars, else None

    @property
    def glyph(self) -> str:
        """The world's symbol (mode glyph)."""
        return self.mode.glyph

    @property
    def is_pentatonic(self) -> bool:
        """True for the 5 black-key stars."""
        return self.roman is not None

    @property
    def clock_hour(self) -> int:
        """The world's position on the Gátople clock face."""
        return self.mode.clock_hour

    @property
    def alt_names(self) -> tuple[str, ...]:
        """Enharmonic spellings, e.g. ('Bb',) for A#."""
        return tuple(WESTERN.tone_names[self.index][1:])

    def tone(self, *, octave: int = 4) -> Tone:
        """Materialize this world as a pitched pytheory Tone."""
        return Tone.from_string(f"{self.note}{octave}")


def _build_dodecamundo() -> tuple[NoteWorld, ...]:
    """Assemble the 12 worlds from the A-indexed western system + canonical modes."""
    worlds: list[NoteWorld] = []
    for index, note in enumerate(TONE_NAMES):
        worlds.append(
            NoteWorld(
                index=index,
                note=note,
                mode=mode_for(note),
                color_hex=WHEEL_HEX[index],
                number=index + 1,
                roman=PENTA_ROMAN_BY_NOTE.get(note),
            )
        )
    return tuple(worlds)


DODECAMUNDO: Final[tuple[NoteWorld, ...]] = _build_dodecamundo()

_BY_NOTE: Final[dict[str, NoteWorld]] = {}
for _world in DODECAMUNDO:
    _BY_NOTE[_world.note] = _world
    for _alt in _world.alt_names:
        _BY_NOTE[_alt] = _world


def world(note: str) -> NoteWorld:
    """Look up a world by note name (canonical or enharmonic), e.g. 'A' or 'Bb'."""
    try:
        return _BY_NOTE[note]
    except KeyError as error:
        raise ValueError(f"unknown note: {note!r}") from error


def world_by_glyph(glyph: str, *, roman: str | None = None) -> NoteWorld:
    """Look up a world by glyph; ``roman`` disambiguates the 5 pentatonic stars."""
    for candidate in DODECAMUNDO:
        if candidate.glyph == glyph and candidate.roman == roman:
            return candidate
    raise ValueError(f"no world for glyph {glyph!r} roman={roman!r}")


def pentatonic_worlds() -> tuple[NoteWorld, ...]:
    """The 5 black-key stars (the ancestral pentatonic core)."""
    return tuple(candidate for candidate in DODECAMUNDO if candidate.is_pentatonic)


def heptatonic_worlds() -> tuple[NoteWorld, ...]:
    """The 7 white-key naturals (the diatonic modes)."""
    return tuple(candidate for candidate in DODECAMUNDO if not candidate.is_pentatonic)
