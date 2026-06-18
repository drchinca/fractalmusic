"""Unit tests — the terminal showcase renders without error."""

from fractalmusic.showcase import (
    show_color_wheel,
    show_combinations,
    show_dodecamundo,
    show_gatople_clock,
    show_heptatonic_modes,
    show_pentatonic_modes,
    show_stats,
)


def test_dodecamundo_lists_all_modes():
    out = show_dodecamundo()
    for name in ("Eólico", "Jónico", "Penta 3"):
        assert name in out


def test_color_wheel_contains_ansi():
    assert "\033[" in show_color_wheel()


def test_heptatonic_section_has_seven_modes():
    mode_names = ("Eólico", "Locrio", "Jónico", "Dórico", "Frigio", "Lidio", "Mixolidio")
    out = show_heptatonic_modes()
    assert all(name in out for name in mode_names)


def test_pentatonic_section_reports_no_semitone():
    assert "no-semitone=True" in show_pentatonic_modes()


def test_gatople_clock_shows_angles():
    assert "90°" in show_gatople_clock()


def test_combinations_spell_triads():
    assert "⋮ □ ♀" in show_combinations()  # A minor triad in glyphs


def test_stats_report_sixty():
    assert "60 microstructures" in show_stats()
