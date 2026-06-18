"""The Gátople — the astrolabio musical (trigonometric note clock).

Places the 12 worlds on a circle and exposes their angular positions, so
intervals become angles and chords/scales become polygons inscribed in the
Dodecamundo. This is the geometric heart of Pattorres's "ubicación y medida
musical" — the Cero Pitágoras measurement (Ch. 4).

Two angular frames coexist:
  * ``angle_deg`` (ClockPosition) — uniform 30°/semitone from A, for interval math.
  * ``clock_hour`` — the book's circle-of-fourths mode positions on the 12-hour face.
"""

from dataclasses import dataclass
from math import cos, radians, sin
from typing import Final

from fractalmusic.dodecamundo import DODECAMUNDO, NoteWorld, world
from fractalmusic.scales import penta

DEGREES_PER_WORLD: Final[float] = 30.0  # 360° / 12
TOP_OF_CLOCK: Final[float] = 90.0  # 12 o'clock at standard math 90°


@dataclass(frozen=True)
class ClockPosition:
    """A world's placement on the Gátople face (chromatic frame)."""

    world: NoteWorld
    angle_deg: float  # clockwise from A, 30° per semitone
    xy: tuple[float, float]  # unit-circle coordinates


def _position(world_obj: NoteWorld) -> ClockPosition:
    """Compute a world's chromatic clock angle and unit-circle (x, y)."""
    angle = world_obj.index * DEGREES_PER_WORLD
    math_angle = radians(TOP_OF_CLOCK - angle)  # clockwise, starting at top
    return ClockPosition(
        world=world_obj,
        angle_deg=angle,
        xy=(round(cos(math_angle), 6), round(sin(math_angle), 6)),
    )


POSITIONS: Final[tuple[ClockPosition, ...]] = tuple(_position(w) for w in DODECAMUNDO)


def position(note: str) -> ClockPosition:
    """Chromatic clock position of a note by name."""
    return POSITIONS[world(note).index]


def interval_angle(from_note: str, to_note: str) -> float:
    """Clockwise chromatic angle (degrees) swept from one world to another."""
    delta = (world(to_note).index - world(from_note).index) % 12
    return delta * DEGREES_PER_WORLD


def clock_hour(note: str) -> int:
    """The book's named mode hour for a note (A Eólico = 9, C Jónico = 12, ...)."""
    return world(note).clock_hour


def polygon(notes: list[str]) -> tuple[tuple[float, float], ...]:
    """Vertices of the polygon a chord or scale inscribes on the Gátople."""
    return tuple(position(note).xy for note in notes)


def cero_pitagoras(root: str) -> list[str]:
    """The Cero Pitágoras pentatonic seed (Penta-1 step pattern) from any root.

    Ch. 4 narrates this as 'poner los cinco dedos sobre las cinco teclas negras'
    — the literal five black keys. That is the special case ``root='C#'``
    (returns ``C# D# F# G# A#``). For any other root the same step pattern is
    transposed, e.g. ``cero_pitagoras('A') → ['A','B','D','E','F#']``.
    """
    return list(penta(root, mode="I").notes)


def rotate(notes: list[str], *, steps: int) -> list[str]:
    """Transpose a set of worlds by rotating the clock ``steps`` semitones."""
    return [DODECAMUNDO[(world(note).index + steps) % 12].note for note in notes]
