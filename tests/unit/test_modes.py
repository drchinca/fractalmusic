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


@pytest.mark.parametrize(
    "note,name,glyph,quality,hour",
    [
        ("A", "Eólico", "⋮", MINOR, 9),
        ("B", "Locrio", "△", DIMINISHED, 7),
        ("C", "Jónico", "□", MAJOR, 12),
        ("D", "Dórico", "+", MINOR, 2),
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
