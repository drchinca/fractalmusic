"""Unit tests — the canonical Gátople modes (Ch. 4 & 8 of the book)."""

import pytest
from fractalmusic.modes import (
    ALL_MODES,
    DIMINISHED,
    HEPTA,
    MAJOR,
    MINOR,
    PENTA,
    mode_for,
)


def test_twelve_modes_total():
    assert len(ALL_MODES) == 12


def test_seven_hepta_five_penta():
    hepta = [m for m in ALL_MODES if m.family == HEPTA]
    penta = [m for m in ALL_MODES if m.family == PENTA]
    assert len(hepta) == 7
    assert len(penta) == 5


# Clock hours follow the circle of fourths from A Eólico = 9 (Ch. 4, "Función
# Cuartal"). These hours match every value the book names in prose.
@pytest.mark.parametrize(
    "note,name,glyph,quality,hour",
    [
        ("A", "Eólico", "⋮", MINOR, 9),
        ("B", "Locrio", "△", DIMINISHED, 7),
        ("C", "Jónico", "□", MAJOR, 12),
        ("D", "Dórico", "+", MINOR, 10),
        ("E", "Frigio", "♀", MINOR, 8),
        ("F", "Lidio", "↑", MAJOR, 1),
        ("G", "Mixolidio", "↓", MAJOR, 11),
    ],
)
def test_natural_mode_bindings(note, name, glyph, quality, hour):
    mode = mode_for(note)
    assert mode.mode_name == name
    assert mode.glyph == glyph
    assert mode.quality == quality
    assert mode.clock_hour == hour


def test_clock_hours_are_a_bijection():
    # 12 distinct notes must occupy 12 distinct clock hours (no collisions).
    hours = {mode.clock_hour for mode in ALL_MODES}
    assert hours == set(range(1, 13))


@pytest.mark.parametrize(
    "note,hour",
    [("A", 9), ("C", 12), ("F", 1), ("G", 11), ("B", 7), ("F#", 6), ("C#", 5), ("E", 8)],
)
def test_clock_hours_match_book_anchors(note, hour):
    assert mode_for(note).clock_hour == hour


def test_penta_note_order_is_rotation_of_black_keys():
    from fractalmusic.dodecamundo import world

    for note in ("C#", "D#", "F#", "G#", "A#"):
        order = mode_for(note).note_order
        indices = [world(n).index for n in order]
        steps = [(b - a) % 12 for a, b in zip(indices, indices[1:] + indices[:1], strict=True)]
        assert sum(steps) == 12
        assert 1 not in steps  # pentatonic has no semitone
        assert order[0] == note  # rooted on its own note


def test_locrio_is_diminished():
    # The book: Locrio is "menor-menor (3,3), por lo tanto disminuida".
    assert mode_for("B").quality == DIMINISHED


def test_penta_modes_are_stars():
    for note in ("C#", "D#", "F#", "G#", "A#"):
        assert mode_for(note).family == PENTA
        assert mode_for(note).glyph == "★"


def test_eolico_scale_is_all_naturals():
    assert mode_for("A").note_order == ("A", "B", "C", "D", "E", "F", "G")


def test_mode_for_unknown_note_raises():
    with pytest.raises(ValueError):
        mode_for("H")
