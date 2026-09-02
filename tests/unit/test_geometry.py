"""Unit tests — deterministic Gátople 2D polygons and 3D dodecahedron coordinates."""

import math

import pytest
from fractalmusic.geometry import (
    CHORD_QUALITIES,
    PHI,
    Chord,
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


def test_augmented_triad_via_chord_build_forms_equilateral_triangle():
    # Same shape as test_augmented_triad_forms_equilateral_triangle_on_gatople_wheel,
    # but through the Chord.build() convenience API instead of raw notes —
    # this is the API the wheel's chord picker actually calls.
    chord = Chord.build("C", "augmented")
    assert chord.notes == ("C", "E", "G#")
    assert chord.symbol == "Caug"
    assert chord.polygon_2d().is_regular is True


def test_diminished_seventh_via_chord_build_forms_a_square():
    chord = Chord.build("A", "dim7")
    assert chord.notes == ("A", "C", "D#", "F#")
    assert chord.polygon_2d().is_regular is True


def test_major_triad_notes_and_symbol():
    chord = Chord.build("C", "major")
    assert chord.notes == ("C", "E", "G")
    assert chord.symbol == "C"


def test_minor_triad_notes_and_symbol():
    chord = Chord.build("A", "minor")
    assert chord.notes == ("A", "C", "E")
    assert chord.symbol == "Am"


def test_diminished_triad_notes_and_symbol():
    chord = Chord.build("B", "diminished")
    assert chord.notes == ("B", "D", "F")
    assert chord.symbol == "Bdim"


def test_chord_qualities_is_the_closed_set_every_build_call_accepts():
    assert set(CHORD_QUALITIES) == {
        "major",
        "minor",
        "augmented",
        "diminished",
        "maj7",
        "min7",
        "dom7",
        "m7b5",
        "dim7",
    }
    for quality in CHORD_QUALITIES:
        chord = Chord.build("A", quality)
        assert chord.root == "A"
        assert chord.quality == quality


def test_augmented_triad_has_uniform_edge_consonance():
    # Its geometric regularity (equilateral triangle) has a harmonic
    # mirror: every edge is the same interval (a major third), so every
    # edge's Pythagorean-ratio consonance must be identical too.
    chord = Chord.build("A", "augmented")
    consonances = chord.edge_consonance()
    assert len(consonances) == 3
    assert len(set(consonances)) == 1


def test_maj7_edge_consonance_is_not_uniform():
    # Unlike the augmented triad, a maj7's edges are different interval
    # sizes (major third, minor third, major third, minor second back to
    # root) — real harmonic tension, not just a classical label.
    chord = Chord.build("C", "maj7")
    consonances = chord.edge_consonance()
    assert len(consonances) == 4
    assert len(set(consonances)) > 1
    assert all(0.0 < c <= 1.0 for c in consonances)


def test_from_degree_resolves_through_the_wheel_not_a_bare_note():
    # Degree I of Eólico under tonic A is A itself (Cardinal Invariant #1),
    # so the augmented triad built from it is the same as Chord.build("A",
    # "augmented") — but from_degree() is what the chord picker actually
    # calls, and a note letter never appears in its own arguments.
    from_degree = Chord.from_degree(tonic="A", mode="Eólico", degree=1, quality="augmented")
    assert from_degree.notes == Chord.build("A", "augmented").notes
    assert from_degree.root == "A"


def test_from_degree_rotates_with_tonic():
    # The exact same (mode, degree, quality) under two different tonics
    # must resolve to different notes — a degree has no fixed identity
    # independent of the tonic it's read against.
    at_a = Chord.from_degree(tonic="A", mode="Dórico", degree=3, quality="minor")
    at_d = Chord.from_degree(tonic="D", mode="Dórico", degree=3, quality="minor")
    assert at_a.notes != at_d.notes


def test_from_degree_rejects_out_of_range_degree():
    with pytest.raises(ValueError, match="out of range"):
        Chord.from_degree(tonic="A", mode="Eólico", degree=8, quality="major")
    with pytest.raises(ValueError, match="out of range"):
        Chord.from_degree(tonic="A", mode="PentaI", degree=6, quality="major")


def test_from_degree_on_penta_mode_resolves_the_fifth_degree():
    # PentaI under tonic A is (C#, D#, F#, G#, A#) — degree 5 is A#.
    chord = Chord.from_degree(tonic="A", mode="PentaI", degree=5, quality="minor")
    assert chord.root == "A#"
    assert chord.notes == ("A#", "C#", "F")


def test_jazz_seventh_chord_construction_and_geometry():
    # Build C Major 7th (C, E, G, B)
    chord = Chord.build("C", "maj7")
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
    chord = Chord.build("A", "dim7")
    assert chord.notes == ("A", "C", "D#", "F#")
    assert chord.symbol == "Adim7"


def test_dominant_seventh_chord_notes():
    # G7: major triad + minor 7th (G, B, D, F). Previously untested — only
    # maj7 and dim7 had note-content assertions.
    chord = Chord.build("G", "dom7")
    assert chord.notes == ("G", "B", "D", "F")
    assert chord.symbol == "G7"


def test_half_diminished_seventh_chord_notes():
    # A half-diminished: diminished triad + minor 7th (A, C, Eb/D#, G).
    chord = Chord.build("A", "m7b5")
    assert chord.notes == ("A", "C", "D#", "G")
    assert chord.symbol == "Aø7"


def test_jazz_chord_build_rejects_unknown_quality():
    with pytest.raises(ValueError, match="unknown chord quality"):
        Chord.build("C", "made-up-quality")


def test_jazz_chord_glyphs_matches_the_notes():
    # Previously never accessed by any test.
    chord = Chord.build("C", "maj7")
    assert chord.glyphs == ("□", "♀", "↓", "△")


def test_polygon_with_fewer_than_three_vertices_is_never_regular():
    assert Polygon2D(vertices=()).is_regular is False
    assert Polygon2D(vertices=((0.0, 0.0),)).is_regular is False
    assert Polygon2D(vertices=((0.0, 0.0), (1.0, 0.0))).is_regular is False
