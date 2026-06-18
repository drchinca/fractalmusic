"""Unit tests — the Gátople clock geometry."""

import math

import pytest
from fractalmusic.gatople import (
    cero_pitagoras,
    clock_hour,
    interval_angle,
    polygon,
    position,
    rotate,
)


def test_unison_angle_is_zero():
    assert interval_angle("A", "A") == 0.0


@pytest.mark.parametrize(
    "a,b,degrees",
    [("A", "C", 90.0), ("A", "E", 210.0), ("A", "A#", 30.0), ("C", "A", 270.0)],
)
def test_interval_angles(a, b, degrees):
    assert interval_angle(a, b) == degrees


def test_octave_wraps_to_zero():
    # 12 semitones = full circle = 0°.
    assert interval_angle("A", "A") == 0.0
    assert interval_angle("C", "C") == 0.0


def test_a_sits_at_top_of_clock():
    x, y = position("A").xy
    assert math.isclose(x, 0.0, abs_tol=1e-6)
    assert math.isclose(y, 1.0, abs_tol=1e-6)


def test_clock_hours_from_book():
    assert clock_hour("A") == 9  # Eólico, the stable horizon
    assert clock_hour("C") == 12  # Jónico, verticality
    assert clock_hour("F#") == 6  # Penta 3, casa de Gátople


def test_cero_pitagoras_is_five_black_keys_seed():
    seed = cero_pitagoras("A")
    assert len(seed) == 5
    assert seed == ["A", "B", "D", "E", "F#"]  # A minor pentatonic shape


def test_polygon_has_one_vertex_per_note():
    verts = polygon(["A", "C", "E"])
    assert len(verts) == 3
    assert all(math.isclose(x * x + y * y, 1.0, abs_tol=1e-6) for x, y in verts)


def test_rotate_transposes_by_semitones():
    assert rotate(["A", "C", "E"], steps=3) == ["C", "D#", "G"]


def test_rotate_full_circle_is_identity():
    notes = ["A", "C", "E"]
    assert rotate(notes, steps=12) == notes
