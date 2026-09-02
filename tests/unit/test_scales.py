"""Unit tests — pentatonic-first scales and the 60 microstructures."""

import pytest
from fractalmusic.dodecamundo import world
from fractalmusic.scales import (
    ORIGIN_NOTE,
    PENTA_MODES,
    FractalScale,
    _steps_of,
    microstructures,
    mode_scale,
    penta,
)


def test_origin_is_a():
    assert ORIGIN_NOTE == "A"


def test_five_penta_modes_defined():
    assert set(PENTA_MODES) == {"I", "II", "III", "IV", "V"}


@pytest.mark.parametrize("mode", ["I", "II", "III", "IV", "V"])
def test_penta_has_five_notes(mode):
    assert len(penta("C#", mode=mode).worlds) == 5


@pytest.mark.parametrize("mode", ["I", "II", "III", "IV", "V"])
def test_penta_has_no_semitones(mode):
    # Ch. 9: the pentatonic is "resistente a los errores" — no semitone steps.
    assert penta("A", mode=mode).has_semitone is False


def test_penta_steps_sum_to_octave():
    for steps in PENTA_MODES.values():
        assert sum(steps) == 12


def test_sixty_microstructures():
    structures = microstructures()
    assert len(structures) == 60  # 5 modes × 12 roots


def test_microstructures_cover_all_roots():
    roots = {s.root for s in microstructures()}
    assert len(roots) == 12


def test_penta_one_on_csharp_matches_book():
    assert penta("C#", mode="I").notes == ("C#", "D#", "F#", "G#", "A#")


def test_mode_scale_eolico():
    scale = mode_scale("A")
    assert scale.family == "hepta"
    assert scale.notes == ("A", "B", "C", "D", "E", "F", "G")


def test_unknown_penta_mode_raises():
    with pytest.raises(ValueError):
        penta("A", mode="VI")


def test_scale_glyphs_property():
    # A-Eólico scale glyphs follow the mode glyph order A B C D E F G.
    assert mode_scale("A").glyphs == ("⋮", "△", "□", "+", "♀", "↑", "↓")


def test_steps_of_wraps_last_note_back_to_first():
    # A -> B is 2 semitones, B -> G# is 9, and the *wraparound* G# -> A is the
    # only semitone in the triplet. Isolates that _steps_of includes the
    # last-to-first step, not just the internal consecutive pairs — every
    # book-canonical scale happens to have a non-wrap semitone too, so this
    # needs a synthetic worlds tuple to pin the wraparound specifically.
    worlds = (world("A"), world("B"), world("G#"))
    assert _steps_of(worlds) == [2, 9, 1]


def test_has_semitone_true_only_from_the_wraparound_step():
    worlds = (world("A"), world("B"), world("G#"))
    scale = FractalScale(name="synthetic", root="A", family="hepta", worlds=worlds)
    assert scale.has_semitone is True
