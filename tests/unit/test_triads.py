"""Unit tests — diatonic triads on the wheel (image 9 invariant)."""

import pytest
from fractalmusic.scales import Triad, triad_for


@pytest.mark.parametrize(
    "root,notes,glyphs,quality,symbol",
    [
        ("A", ("A", "C", "E"), ("⋮", "□", "♀"), "minor", "Am"),
        ("B", ("B", "D", "F"), ("△", "+", "↑"), "diminished", "B°"),
        ("C", ("C", "E", "G"), ("□", "♀", "↓"), "major", "C"),
        ("D", ("D", "F", "A"), ("+", "↑", "⋮"), "minor", "Dm"),
        ("E", ("E", "G", "B"), ("♀", "↓", "△"), "minor", "Em"),
        ("F", ("F", "A", "C"), ("↑", "⋮", "□"), "major", "F"),
        ("G", ("G", "B", "D"), ("↓", "△", "+"), "major", "G"),
    ],
)
def test_triad_for_matches_book_image_9(root, notes, glyphs, quality, symbol):
    triad = triad_for(root)
    assert isinstance(triad, Triad)
    assert triad.notes == notes
    assert triad.glyphs == glyphs
    assert triad.quality == quality
    assert triad.symbol == symbol


def test_triad_invariant_holds_for_all_seven_natural_notes():
    # The 1-3-5 pick on note_order is the diatonic-triad invariant the book
    # diagrams in image 9. Verify we compute exactly seven triads, all distinct.
    triads = [triad_for(n) for n in "ABCDEFG"]
    assert len({t.symbol for t in triads}) == 7


def test_triad_for_pentatonic_root_raises():
    with pytest.raises(ValueError, match="pentatonic"):
        triad_for("C#")
