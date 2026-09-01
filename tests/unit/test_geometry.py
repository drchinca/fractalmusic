"""Unit tests — deterministic Gátople 2D polygons and 3D dodecahedron coordinates via formulas."""

import math

from fractalmusic.dodecamundo import world
from fractalmusic.geometry import (
    AUGMENTED_TRIAD,
    DIMINISHED_7TH,
    MAJOR_7TH,
    MINOR_TRIAD,
    PHI,
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


def test_augmented_triad_formula_forms_equilateral_triangle_from_any_world():
    # An augmented triad projected from C (C, E, G#) sits at 12, 8, and 4 o'clock on the Gátople clock face.
    # This forms a perfect equilateral triangle under A-origin!
    root = world("C")
    poly = AUGMENTED_TRIAD.polygon_2d(root)

    assert len(poly.vertices) == 3
    # Check that centroid is exactly at the circle center (0, 0)
    cx, cy = poly.centroid
    assert math.isclose(cx, 0.0, abs_tol=1e-6)
    assert math.isclose(cy, 0.0, abs_tol=1e-6)

    # Check that it is recognized as mathematically regular
    assert poly.is_regular is True


def test_jazz_seventh_chord_formula_projections():
    # Project MAJOR_7TH from G (G, B, D, F#)
    root = world("G")
    notes = tuple(w.note for w in MAJOR_7TH.project(root))
    assert notes == ("G", "B", "D", "F#")

    # Verify its 2D polygon properties on the wheel
    poly = MAJOR_7TH.polygon_2d(root)
    assert len(poly.vertices) == 4
    assert poly.is_regular is False  # A maj7 is not a regular square
    assert poly.perimeter > 0.0

    # Verify its 3D coordinates on the dodecahedron/icosahedron
    coords = MAJOR_7TH.coordinates_3d(root)
    assert len(coords) == 4
    for x, y, z in coords:
        # Check that coordinates are bounded by icosahedron geometry
        assert abs(x) in (0.0, 1.0, PHI)
        assert abs(y) in (0.0, 1.0, PHI)
        assert abs(z) in (0.0, 1.0, PHI)


def test_diminished_seventh_chord_projections():
    # Project DIMINISHED_7TH from A (A, C, D#, F#)
    root = world("A")
    notes = tuple(w.note for w in DIMINISHED_7TH.project(root))
    assert notes == ("A", "C", "D#", "F#")


def test_minor_triad_projection():
    # Project MINOR_TRIAD from E (E, G, B)
    root = world("E")
    notes = tuple(w.note for w in MINOR_TRIAD.project(root))
    assert notes == ("E", "G", "B")
