"""Deterministic fractal geometry, Platonic solid mappings, and chord formulas.

Chords are defined purely as mathematical formulas (semitone step offsets) which
can be projected dynamically from ANY starting root NoteWorld on the Gátople wheel.

This eliminates hardcoded note-maps, reflecting the rotating, moving nature of the
Gátople.

Links the 12 NoteWorlds to the 12 face centers of a regular dodecahedron (represented
as the 12 vertices of its dual, a regular icosahedron, defined using the Golden Ratio φ).
"""

import math
from dataclasses import dataclass
from typing import Final

from fractalmusic.dodecamundo import DODECAMUNDO, NoteWorld, world
from fractalmusic.wheel import Wheel, clock_hour_for

# The Golden Ratio — the load-bearing logistics of the fractal geometry
PHI: Final[float] = (1.0 + math.sqrt(5.0)) / 2.0  # ≈ 1.6180339887

# The 12 vertices of a regular icosahedron (dual of the regular dodecahedron).
# Each vertex is a 3D coordinate (x, y, z) that maps deterministically to one of the 12 worlds.
_ICOSAHEDRON_VERTICES: Final[tuple[tuple[float, float, float], ...]] = (
    (0.0, 1.0, PHI),      # v0 -> A
    (0.0, -1.0, PHI),     # v1 -> A#
    (0.0, 1.0, -PHI),     # v2 -> B
    (0.0, -1.0, -PHI),    # v3 -> C
    (1.0, PHI, 0.0),      # v4 -> C#
    (-1.0, PHI, 0.0),     # v5 -> D
    (1.0, -PHI, 0.0),     # v6 -> D#
    (-1.0, -PHI, 0.0),    # v7 -> E
    (PHI, 0.0, 1.0),      # v8 -> F
    (-PHI, 0.0, 1.0),     # v9 -> F#
    (PHI, 0.0, -1.0),     # v10 -> G
    (-PHI, 0.0, -1.0),    # v11 -> G#
)


def note_3d_coordinates(note: str) -> tuple[float, float, float]:
    """Return the deterministic (x, y, z) coordinate of a note on the icosahedron/dodecahedron."""
    w = world(note)
    return _ICOSAHEDRON_VERTICES[w.index]


@dataclass(frozen=True, slots=True)
class Polygon2D:
    """A 2D polygon representing a chord's vertices on the Gátople wheel."""

    vertices: tuple[tuple[float, float], ...]

    @property
    def centroid(self) -> tuple[float, float]:
        """The geometric center of gravity (average of vertex coordinates)."""
        xs = [v[0] for v in self.vertices]
        ys = [v[1] for v in self.vertices]
        k = len(self.vertices)
        return sum(xs) / k, sum(ys) / k

    @property
    def perimeter(self) -> float:
        """The total side length of the polygon."""
        length = 0.0
        k = len(self.vertices)
        for i in range(k):
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i + 1) % k]
            length += math.hypot(x2 - x1, y2 - y1)
        return length

    @property
    def is_regular(self) -> bool:
        """True if all edges of the polygon are mathematically equal (within epsilon)."""
        k = len(self.vertices)
        if k < 3:
            return False
        edges = []
        for i in range(k):
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i + 1) % k]
            edges.append(math.hypot(x2 - x1, y2 - y1))
        first = edges[0]
        return all(math.isclose(e, first, rel_tol=1e-4) for e in edges)


def chord_polygon_2d(notes: tuple[str, ...], *, tonic: str = "A") -> Polygon2D:
    """Compute the 2D polygon for a list of notes on the Gátople wheel under a tonic rotation."""
    vertices = []
    seg_deg = 30.0
    for note in notes:
        hour = clock_hour_for(note, tonic=tonic)
        # Convert clock hour to geometric angle in radians
        angle_deg = (hour % 12) * seg_deg
        rad = (angle_deg - 90.0) * (math.pi / 180.0)
        vertices.append((math.cos(rad), math.sin(rad)))
    return Polygon2D(vertices=tuple(vertices))


@dataclass(frozen=True, slots=True)
class ChordFormula:
    """A chord formula defined purely as mathematical semitone offsets from a starting root world."""

    name: str
    semitone_offsets: tuple[int, ...]

    def project(self, root_world: NoteWorld) -> tuple[NoteWorld, ...]:
        """Project this formula dynamically from any starting root NoteWorld."""
        return tuple(DODECAMUNDO[(root_world.index + offset) % 12] for offset in self.semitone_offsets)

    def polygon_2d(self, root_world: NoteWorld, *, wheel: Wheel = Wheel()) -> Polygon2D:
        """The 2D polygon representing this chord formula on the Gátople wheel under a rotation."""
        notes = tuple(w.note for w in self.project(root_world))
        return chord_polygon_2d(notes, tonic=wheel.tonic)

    def coordinates_3d(self, root_world: NoteWorld) -> tuple[tuple[float, float, float], ...]:
        """The 3D coordinates representing this chord's face centers on the dodecahedron."""
        notes = tuple(w.note for w in self.project(root_world))
        return tuple(note_3d_coordinates(n) for n in notes)


# Diatonic triads (semitone offsets from root)
MAJOR_TRIAD: Final[ChordFormula] = ChordFormula("major", (0, 4, 7))
MINOR_TRIAD: Final[ChordFormula] = ChordFormula("minor", (0, 3, 7))
DIMINISHED_TRIAD: Final[ChordFormula] = ChordFormula("diminished", (0, 3, 6))
AUGMENTED_TRIAD: Final[ChordFormula] = ChordFormula("augmented", (0, 4, 8))  # perfectly symmetric equilateral triangle!

# Jazz seventh chords (semitone offsets from root)
MAJOR_7TH: Final[ChordFormula] = ChordFormula("maj7", (0, 4, 7, 11))
MINOR_7TH: Final[ChordFormula] = ChordFormula("min7", (0, 3, 7, 10))
DOMINANT_7TH: Final[ChordFormula] = ChordFormula("7", (0, 4, 7, 10))
HALF_DIMINISHED_7TH: Final[ChordFormula] = ChordFormula("m7b5", (0, 3, 6, 10))
DIMINISHED_7TH: Final[ChordFormula] = ChordFormula("dim7", (0, 3, 6, 9))  # perfectly symmetric square!
