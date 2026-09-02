"""Unit tests — deterministic Gátople 2D polygons and 3D dodecahedron coordinates."""

import math

import pytest
from fractalmusic.geometry import (
    PHI,
    JazzChord,
    Polygon2D,
    chord_polygon_2d,
    note_3d_coordinates,
)


def test_dodecahedron_face_coordinates_are_deterministic_and_golden():
    # Note A (index 0) must map exactly to v0: (0.0, 1.0, PHI)
    ax, ay, az = note_3d_coordinates("A")
    assert math.isclose(ax, 0.0)
    assert math.isclose(ay, 1.0)
    assert math.isclose(az, PHI)

    # Note B (index 2) must map exactly to v2: (0.0, 1.0, -PHI)
    bx, by, bz = note_3d_coordinates("B")
    assert math.isclose(bx, 0.0)
    assert math.isclose(by, 1.0)
    assert math.isclose(bz, -PHI)


def test_augmented_triad_forms_equilateral_triangle_on_gatople_wheel():
    # An augmented triad (e.g., C augmented: C, E, G#) jumps exactly 4 semitones per note.
    # On the Gátople clock face: C sits at 12 o'clock, G# sits at 4 o'clock, and E sits at 8 o'clock.
    # This forms a perfect equilateral triangle on the Gátople wheel!
    notes = ("C", "G#", "E")
    poly = chord_polygon_2d(notes)

    assert len(poly.vertices) == 3
    # Check that centroid is exactly at the circle center (0, 0)
    cx, cy = poly.centroid
    assert math.isclose(cx, 0.0, abs_tol=1e-6)
    assert math.isclose(cy, 0.0, abs_tol=1e-6)

    # Check that it is recognized as mathematically regular
    assert poly.is_regular is True


def test_chord_polygon_2d_puts_hour_twelve_at_the_top():
    # Same "hour 12 = straight up" convention as svg.py's _polar and
    # gatople.py's POSITIONS. Shape-only checks (regularity, centroid) are
    # invariant to a sign flip in the angle offset, so nothing else pins
    # down this absolute orientation.
    x, y = chord_polygon_2d(("C",)).vertices[0]
    assert math.isclose(x, 0.0, abs_tol=1e-9)
    assert math.isclose(y, -1.0)


def test_jazz_seventh_chord_construction_and_geometry():
    # Build C Major 7th (C, E, G, B)
    chord = JazzChord.build("C", "maj7")
    assert chord.notes == ("C", "E", "G", "B")
    assert chord.symbol == "Cmaj7"

    # Verify its 2D polygon properties on the wheel
    poly = chord.polygon_2d()
    assert len(poly.vertices) == 4
    assert poly.is_regular is False  # A maj7 is not a regular square
    assert poly.perimeter > 0.0

    # Verify its 3D coordinates on the dodecahedron/icosahedron
    coords = chord.coordinates_3d()
    assert len(coords) == 4
    for x, y, z in coords:
        # Check that coordinates are bounded by icosahedron geometry
        assert abs(x) in (0.0, 1.0, PHI)
        assert abs(y) in (0.0, 1.0, PHI)
        assert abs(z) in (0.0, 1.0, PHI)


def test_diminished_seventh_chord_notes():
    # Build A diminished 7th (A, C, D#, F#)
    chord = JazzChord.build("A", "dim7")
    assert chord.notes == ("A", "C", "D#", "F#")
    assert chord.symbol == "Adim7"


def test_dominant_seventh_chord_notes():
    # G7: major triad + minor 7th (G, B, D, F). Previously untested — only
    # maj7 and dim7 had note-content assertions.
    chord = JazzChord.build("G", "dom7")
    assert chord.notes == ("G", "B", "D", "F")
    assert chord.symbol == "G7"


def test_half_diminished_seventh_chord_notes():
    # A half-diminished: diminished triad + minor 7th (A, C, Eb/D#, G).
    chord = JazzChord.build("A", "m7b5")
    assert chord.notes == ("A", "C", "D#", "G")
    assert chord.symbol == "Aø7"


def test_jazz_chord_build_rejects_unknown_quality():
    with pytest.raises(ValueError, match="unknown jazz chord quality"):
        JazzChord.build("C", "made-up-quality")


def test_jazz_chord_glyphs_matches_the_notes():
    # Previously never accessed by any test.
    chord = JazzChord.build("C", "maj7")
    assert chord.glyphs == ("□", "♀", "↓", "△")


def test_polygon_with_fewer_than_three_vertices_is_never_regular():
    assert Polygon2D(vertices=()).is_regular is False
    assert Polygon2D(vertices=((0.0, 0.0),)).is_regular is False
    assert Polygon2D(vertices=((0.0, 0.0), (1.0, 0.0))).is_regular is False
