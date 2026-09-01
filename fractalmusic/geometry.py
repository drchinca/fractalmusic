"""Deterministic fractal geometry and Platonic solid mappings for chords and notes.

Links the 12 notes of El Sistema Fractal to the 12 face centers of a regular
dodecahedron (represented as the 12 vertices of its dual, a regular icosahedron,
which are defined mathematically using the Golden Ratio φ).

Also models chords (triads and jazz seventh chords) as 2D polygons on the Gátople
wheel, calculating their centroids, perimeters, and regularity.
"""

import math
from dataclasses import dataclass
from typing import Final, Self

from fractalmusic.dodecamundo import world
from fractalmusic.wheel import clock_hour_for

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


# Seventh chord interval patterns (root, third, fifth, seventh) as semitones from root.
_JAZZ_INTERVAL_MAP: Final[dict[str, tuple[int, int, int, int]]] = {
    "maj7": (0, 4, 7, 11),  # Major 7th
    "min7": (0, 3, 7, 10),  # Minor 7th
    "dom7": (0, 4, 7, 10),  # Dominant 7th
    "m7b5": (0, 3, 6, 10),  # Half-diminished 7th
    "dim7": (0, 3, 6, 9),   # Fully-diminished 7th (forms a perfect square!)
}


@dataclass(frozen=True)
class JazzChord:
    """A 4-note jazz seventh chord mapped onto 2D and 3D geometries."""

    root: str
    quality: str  # "maj7" | "min7" | "dom7" | "m7b5" | "dim7"
    notes: tuple[str, str, str, str]

    @property
    def symbol(self) -> str:
        """Chord symbol (e.g., 'Cmaj7', 'Amin7', 'G7')."""
        suffix = {"maj7": "maj7", "min7": "min7", "dom7": "7", "m7b5": "ø7", "dim7": "dim7"}[self.quality]
        return f"{self.root}{suffix}"

    @property
    def glyphs(self) -> tuple[str, str, str, str]:
        """Symbols for each note-world in the chord."""
        return tuple(world(n).glyph for n in self.notes)

    def polygon_2d(self, *, tonic: str = "A") -> Polygon2D:
        """The 2D polygon representing this jazz chord on the Gátople wheel."""
        return chord_polygon_2d(self.notes, tonic=tonic)

    def coordinates_3d(self) -> tuple[tuple[float, float, float], ...]:
        """The 3D coordinates representing the chord's face centers on the dodecahedron."""
        return tuple(note_3d_coordinates(n) for n in self.notes)

    @classmethod
    def build(cls, root: str, quality: str) -> Self:
        """Deterministic constructor to build a JazzChord from its root and quality."""
        if quality not in _JAZZ_INTERVAL_MAP:
            raise ValueError(f"unknown jazz chord quality: {quality!r}")
        intervals = _JAZZ_INTERVAL_MAP[quality]

        # Build chord notes by walking semitones from root
        from fractalmusic.wheel import CHROMATIC_ORDER, _note_index
        base = _note_index(root)
        notes = tuple(CHROMATIC_ORDER[(base + semitones) % 12] for semitones in intervals)
        return cls(root=root, quality=quality, notes=notes)
