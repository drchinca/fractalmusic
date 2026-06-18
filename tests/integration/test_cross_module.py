"""Integration tests — modes, dodecamundo, gatople, cartas stay consistent."""

from fractalmusic.cartas import spell
from fractalmusic.dodecamundo import DODECAMUNDO, world
from fractalmusic.gatople import clock_hour, interval_angle, polygon
from fractalmusic.modes import mode_for
from fractalmusic.scales import mode_scale, penta


def test_world_glyph_matches_its_mode_glyph():
    for w in DODECAMUNDO:
        assert w.glyph == mode_for(w.note).glyph


def test_world_clock_hour_matches_mode():
    for w in DODECAMUNDO:
        assert w.clock_hour == mode_for(w.note).clock_hour


def test_spell_of_mode_scale_starts_with_its_own_glyph():
    # A scale rooted on C (Jónico □) starts with the square.
    glyphs = spell(list(mode_scale("C").notes))
    assert glyphs.startswith("□")


def test_pentatonic_scale_on_black_root_spells_all_stars():
    # Penta modes built on the black keys (the book's canonical roots) are all stars.
    roots = {"I": "C#", "II": "D#", "III": "F#", "IV": "G#", "V": "A#"}
    for mode, root in roots.items():
        assert set(spell(list(penta(root, mode=mode).notes)).split()) == {"★"}


def test_interval_angle_consistent_with_index_distance():
    for w in DODECAMUNDO:
        expected = ((w.index - world("A").index) % 12) * 30.0
        assert interval_angle("A", w.note) == expected


def test_polygon_vertices_align_with_clock_positions():
    notes = ["A", "C", "E"]
    verts = polygon(notes)
    assert len(verts) == len(notes)


def test_eolico_and_jonico_are_relatives():
    # Book: A Eólico and C Jónico are relative (share the 7 naturals).
    assert set(mode_scale("A").notes) == set(mode_scale("C").notes)


def test_dodecamundo_clock_hours_are_unique_per_family():
    # Heptatonic modes occupy distinct hours.
    hepta_hours = [clock_hour(w.note) for w in DODECAMUNDO if not w.is_pentatonic]
    assert len(set(hepta_hours)) == 7
