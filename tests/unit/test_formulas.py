"""Unit tests — etno-matemática formulas (Fibonacci, Pythagoras, potenciación)."""

import pytest
from fractalmusic.formulas import (
    PHI,
    chessboard_grains,
    consonance,
    fibonacci,
    fibonacci_chord,
    interval_ratio,
)


def test_phi_value():
    assert round(PHI, 5) == 1.61803


def test_fibonacci_book_form():
    # Book's series starts 1, 2, 3, 5, 8, 13 ...
    assert fibonacci(6) == [1, 2, 3, 5, 8, 13]


def test_fibonacci_chord_offsets():
    chord = fibonacci_chord("A", voices=4)
    # offsets 1,2,3,5 → +0,+1,+2,+4 semitones from A.
    assert [w.note for w in chord] == ["A", "A#", "B", "C#"]


def test_chessboard_doubling():
    assert chessboard_grains(1) == 1
    assert chessboard_grains(2) == 2
    assert chessboard_grains(8) == 128
    assert chessboard_grains(64) == 2**63  # ruinous wager


def test_chessboard_out_of_range():
    with pytest.raises(ValueError):
        chessboard_grains(65)


def test_unison_ratio_is_one_to_one():
    assert interval_ratio("A", "A") == (1, 1)


def test_perfect_fifth_ratio():
    # 7 semitones A→E = 3:2.
    assert interval_ratio("A", "E") == (3, 2)


def test_octave_more_consonant_than_tritone():
    assert consonance("A", "A") > consonance("A", "D#")
