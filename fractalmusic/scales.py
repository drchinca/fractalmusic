"""Pentatonic-first scales — the 5 + 7 = 12 architecture.

Pattorres treats the 5 pentatonic modes as ontologically prior to the 7
heptatonic modes: 5 base penta-forms × 12 roots = 60 microstructures (Ch. 9).
The default origin is A minor / Eólico (matriarchal), not C major.

Penta interval patterns are derived from the book's spelling of each penta mode
(Ch. 4 & 9): no semitones, the pentatonic "no-error" property the book stresses.
"""

from dataclasses import dataclass
from typing import Final

from fractalmusic.dodecamundo import DODECAMUNDO, NoteWorld, world
from fractalmusic.modes import PENTA, mode_for

ORIGIN_NOTE: Final[str] = "A"  # La menor / Eólico — the matriarchal origin

# The 5 pentatonic modes as semitone-step patterns (each sums to 12, none has a
# semitone, per Ch. 9). Each is a rotation of the black-key cycle (2,3,2,2,3).
# The note spellings below are the canonical black-key roots; passing any other
# root to penta() transposes the same step pattern.
PENTA_MODES: Final[dict[str, tuple[int, ...]]] = {
    "I": (2, 3, 2, 2, 3),  # Penta 1, from C#: C# D# F# G# A#
    "II": (3, 2, 2, 3, 2),  # Penta 2, from D#: D# F# G# A# C#
    "III": (2, 2, 3, 2, 3),  # Penta 3, from F#: F# G# A# C# D#
    "IV": (2, 3, 2, 3, 2),  # Penta 4, from G#: G# A# C# D# F#
    "V": (3, 2, 3, 2, 2),  # Penta 5, from A#: A# C# D# F# G#
}


@dataclass(frozen=True)
class FractalScale:
    """A scale as an ordered sequence of worlds."""

    name: str
    root: str
    family: str  # "penta" or "hepta"
    worlds: tuple[NoteWorld, ...]

    @property
    def notes(self) -> tuple[str, ...]:
        """Note names in scale order."""
        return tuple(w.note for w in self.worlds)

    @property
    def glyphs(self) -> tuple[str, ...]:
        """Glyph sequence — the scale spelled in Fractal symbols."""
        return tuple(w.glyph for w in self.worlds)

    @property
    def has_semitone(self) -> bool:
        """True if any adjacent step is a single semitone."""
        return 1 in _steps_of(self.worlds)


def _walk(root: str, steps: tuple[int, ...]) -> tuple[NoteWorld, ...]:
    """Walk a step pattern from a root, yielding worlds (excludes the octave)."""
    index = world(root).index
    out: list[NoteWorld] = [DODECAMUNDO[index]]
    for step in steps[:-1]:
        index = (index + step) % 12
        out.append(DODECAMUNDO[index])
    return tuple(out)


def _steps_of(worlds: tuple[NoteWorld, ...]) -> list[int]:
    """Semitone steps between consecutive worlds, wrapping the octave."""
    indices = [w.index for w in worlds]
    steps: list[int] = []
    for current, following in zip(indices, indices[1:] + indices[:1], strict=False):
        steps.append((following - current) % 12)
    return steps


def penta(root: str = ORIGIN_NOTE, *, mode: str = "I") -> FractalScale:
    """Build one of the 5 pentatonic modes from a given root."""
    if mode not in PENTA_MODES:
        raise ValueError(f"unknown penta mode: {mode!r}; choose from {list(PENTA_MODES)}")
    return FractalScale(
        name=f"Penta {mode}",
        root=root,
        family=PENTA,
        worlds=_walk(root, PENTA_MODES[mode]),
    )


def microstructures() -> tuple[FractalScale, ...]:
    """All 60 microstructures: 5 penta modes × 12 roots."""
    return tuple(penta(w.note, mode=mode) for mode in PENTA_MODES for w in DODECAMUNDO)


def mode_scale(note: str) -> FractalScale:
    """The canonical Greek/Penta mode scale rooted on a note's own world."""
    mode = mode_for(note)
    return FractalScale(
        name=mode.mode_name,
        root=note,
        family=mode.family,
        worlds=tuple(world(n) for n in mode.note_order),
    )


# Triad qualities for the 7 diatonic positions of A natural minor — the book's
# default rotation. Index 0 = root mode (Eólico), then up the cycle of fourths.
# Confirmed against image 9 of the user's notebook: i ii° III iv v VI VII.
_TRIAD_QUALITIES: Final[dict[str, str]] = {
    "Eólico": "minor",
    "Locrio": "diminished",
    "Jónico": "major",
    "Dórico": "minor",
    "Frigio": "minor",
    "Lidio": "major",
    "Mixolidio": "major",
}


@dataclass(frozen=True)
class Triad:
    """A 1-3-5 triad picked from a heptatonic mode's scale."""

    root: str
    notes: tuple[str, str, str]
    glyphs: tuple[str, str, str]
    quality: str  # "major" / "minor" / "diminished"

    @property
    def symbol(self) -> str:
        """Conventional chord symbol (e.g. 'Am', 'B°', 'C')."""
        suffix = {"minor": "m", "diminished": "°", "major": ""}[self.quality]
        return f"{self.root}{suffix}"


def triad_for(note: str) -> Triad:
    """The diatonic 1-3-5 triad rooted on a heptatonic note (image 9 invariant).

    Picks scale positions 1, 3, 5 from the Greek mode rooted on ``note``, then
    spells the triad in glyphs. Verified against the book's diatonic theory in
    A natural minor (Am, B°, C, Dm, Em, F, G).

    Raises :class:`ValueError` for pentatonic (black-key) roots — triads in this
    sense are a heptatonic construct.
    """
    mode = mode_for(note)
    if mode.family != "hepta":
        raise ValueError(
            f"triad_for: {note!r} is a pentatonic root; "
            f"diatonic triads are heptatonic only"
        )
    scale = mode_scale(note)
    triad_notes = (scale.notes[0], scale.notes[2], scale.notes[4])
    triad_glyphs = (scale.glyphs[0], scale.glyphs[2], scale.glyphs[4])
    return Triad(
        root=note,
        notes=triad_notes,
        glyphs=triad_glyphs,
        quality=_TRIAD_QUALITIES[mode.mode_name],
    )
