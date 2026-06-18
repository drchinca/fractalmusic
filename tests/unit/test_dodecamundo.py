"""Unit tests — the Dodecamundo data model and the 5 + 7 = 12 invariant."""

import pytest
from fractalmusic.dodecamundo import (
    BLACK_KEY_INDICES,
    DODECAMUNDO,
    heptatonic_worlds,
    pentatonic_worlds,
    world,
    world_by_glyph,
)


def test_twelve_worlds():
    assert len(DODECAMUNDO) == 12


def test_a_origin_matriarchal():
    # The system measures from La (A), not Do (C).
    assert DODECAMUNDO[0].note == "A"
    assert DODECAMUNDO[0].mode.mode_name == "Eólico"
    assert DODECAMUNDO[3].note == "C"


def test_five_plus_seven_equals_twelve():
    assert len(pentatonic_worlds()) == 5
    assert len(heptatonic_worlds()) == 7
    assert len(pentatonic_worlds()) + len(heptatonic_worlds()) == 12


def test_black_keys_are_the_five_stars():
    stars = {w.note for w in pentatonic_worlds()}
    assert stars == {"A#", "C#", "D#", "F#", "G#"}
    assert all(DODECAMUNDO[i].is_pentatonic for i in BLACK_KEY_INDICES)


def test_numbers_are_one_based():
    assert [w.number for w in DODECAMUNDO] == list(range(1, 13))


def test_enharmonic_lookup_is_identity():
    assert world("Bb") is world("A#")
    assert world("Gb") is world("F#")


def test_unknown_note_raises():
    with pytest.raises(ValueError):
        world("H")


def test_world_by_glyph_natural():
    assert world_by_glyph("□").note == "C"  # Jónico square


def test_world_by_glyph_star_needs_roman():
    assert world_by_glyph("★", roman="III").note == "F#"  # Penta 3


def test_world_by_glyph_unknown_raises():
    with pytest.raises(ValueError):
        world_by_glyph("✦", roman=None)


@pytest.mark.parametrize(
    "note,octave,expected",
    [("A", 4, "A4"), ("C", 3, "C3"), ("F#", 5, "F#5")],
)
def test_world_materializes_pytheory_tone(note, octave, expected):
    assert world(note).tone(octave=octave).full_name == expected
