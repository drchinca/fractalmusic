"""Unit tests — carta rendering and glyph spelling."""

from fractalmusic.cartas import carta, deck, piano_stickers, spell
from fractalmusic.dodecamundo import world


def test_deck_has_twelve_lines():
    assert len(deck().splitlines()) == 12


def test_carta_contains_glyph_and_resets_ansi():
    line = carta(world("C"))
    assert "□" in line
    assert line.endswith("\033[0m")


def test_piano_stickers_label_black_and_white():
    lines = piano_stickers().splitlines()
    assert len(lines) == 12
    assert sum("black" in line for line in lines) == 5
    assert sum("white" in line for line in lines) == 7


def test_spell_a_minor_triad():
    # A C E → Eólico, Jónico, Frigio glyphs.
    assert spell(["A", "C", "E"]) == "⋮ □ ♀"


def test_spell_pentatonic_is_all_stars():
    assert spell(["C#", "D#", "F#", "G#", "A#"]) == "★ ★ ★ ★ ★"
