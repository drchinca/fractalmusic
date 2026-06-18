"""Unit tests — the spinning Gátople (two-disc model).

Covers the role registry, ``Wheel(tonic)`` rotations, the ``generate_scale`` /
``generate_twelve_outputs`` helpers ported from the original prototype, and the
back-compat property that ``Wheel('A')`` reproduces the book's defaults.
"""

import pytest
from fractalmusic.modes import CHROMATIC_ORDER, mode_for
from fractalmusic.wheel import (
    ROLES,
    Wheel,
    WheelMode,
    clock_hour_for,
    generate_scale,
    generate_twelve_outputs,
    is_valid_pattern,
    spin,
)


def test_twelve_roles():
    assert len(ROLES) == 12
    assert all(0 <= r.position <= 11 for r in ROLES)
    assert {r.position for r in ROLES} == set(range(12))


def test_default_tonic_matches_book_modes():
    # Wheel('A') reproduces the canonical bindings: A↔Eólico, C↔Jónico, F#↔Penta3.
    wheel = Wheel()
    for note in ("A", "C", "F#", "G", "B"):
        assert wheel.mode_for(note).mode_name == mode_for(note).mode_name
        assert wheel.mode_for(note).clock_hour == mode_for(note).clock_hour


def test_spin_to_f_puts_f_under_eolico():
    wheel = spin("F")
    bound = wheel.mode_for("F")
    assert bound.mode_name == "Eólico"
    assert bound.glyph == "⋮"


def test_spin_rotates_every_role():
    # Rotating to F shifts every note's role by the same offset (8 semitones).
    a_wheel = Wheel("A")
    f_wheel = Wheel("F")
    # Under F-tonic, the note that gets Jónico (□) is F+3 = G#/Ab.
    assert f_wheel.mode_for("G#").mode_name == "Jónico"
    # And the note that A used to occupy (Eólico) is now occupied by F.
    assert f_wheel.mode_for("F").mode_name == a_wheel.mode_for("A").mode_name


def test_eolico_scale_under_f_tonic():
    # F Eólico should yield F G G# A# C C# D# (F natural minor).
    wheel = Wheel("F")
    f_eolico = wheel.mode_for("F").scale_notes()
    assert f_eolico == ("F", "G", "G#", "A#", "C", "C#", "D#")


def test_all_modes_returns_twelve_distinct_bindings():
    wheel = Wheel("D")
    bindings = wheel.all_modes()
    assert len(bindings) == 12
    assert len({b.note for b in bindings}) == 12


def test_penta_under_default_tonic():
    wheel = Wheel("A")
    assert wheel.penta("I") == ("C#", "D#", "F#", "G#", "A#")


def test_penta_under_f_tonic_transposes():
    # Under F-tonic, Penta-I rotates by F-A = 8 semitones from C#.
    wheel = Wheel("F")
    rotated = wheel.penta("I")
    expected_root_idx = (CHROMATIC_ORDER.index("C#") + 8) % 12
    assert rotated[0] == CHROMATIC_ORDER[expected_root_idx]


def test_penta_unknown_roman_raises():
    with pytest.raises(ValueError):
        Wheel("A").penta("VI")


def test_clock_hour_for_default_matches_book():
    # With the default tonic, clock_hour_for matches the book's circle of fourths.
    assert clock_hour_for("A") == 9
    assert clock_hour_for("C") == 12
    assert clock_hour_for("F") == 1


def test_clock_hour_for_under_spun_tonic():
    # Under tonic=F, F is at hour 9 (it now plays the Eólico role).
    assert clock_hour_for("F", tonic="F") == 9


def test_enharmonic_resolves_to_canonical():
    # Bb (flat) resolves to the same role as A# (sharp); generate_scale
    # normalizes the spelling to the canonical sharp name in its output.
    assert Wheel("A").mode_for("Bb").mode_name == Wheel("A").mode_for("A#").mode_name
    assert generate_scale([3, 2, 2, 3, 2], "Bb")[0] == "A#"


def test_is_valid_pattern_rejects_non_string_note():
    with pytest.raises(ValueError):
        is_valid_pattern([2, 2, 1, 2, 2], 5)  # type: ignore[arg-type]


# --- generate_scale / generate_twelve_outputs (ported prototype) ---


def test_is_valid_pattern_accepts_valid():
    assert is_valid_pattern([2, 2, 1, 2, 2, 2, 1], "A")


@pytest.mark.parametrize(
    "pattern,note,reason",
    [
        ([2, 2, 1, 2], "A", "fewer than 5 steps"),
        ([2, 2, 1, 2, 5], "A", "step out of 1..4"),
        ([2, 2, 1, 2, 2], "H", "unknown note"),
        ("not a list", "A", "wrong type"),
    ],
)
def test_is_valid_pattern_rejects(pattern, note, reason):
    with pytest.raises(ValueError):
        is_valid_pattern(pattern, note)  # type: ignore[arg-type]


def test_generate_scale_a_eolico():
    # Aeolian (natural minor) steps: 2 1 2 2 1 2 2 → A B C D E F G A.
    notes = generate_scale([2, 1, 2, 2, 1, 2, 2], "A")
    assert notes == ["A", "B", "C", "D", "E", "F", "G", "A"]


def test_generate_scale_pentatonic():
    # A minor pentatonic: 3 2 2 3 2 → A C D E G A.
    notes = generate_scale([3, 2, 2, 3, 2], "A")
    assert notes == ["A", "C", "D", "E", "G", "A"]


def test_generate_twelve_outputs_returns_twelve_scales():
    # Stack of 12 minor-pentatonic patterns over the chromatic ring from A.
    underlying = [[3, 2, 2, 3, 2]] * 12
    out = generate_twelve_outputs(underlying, list(CHROMATIC_ORDER), "A")
    assert len(out) == 12
    assert out[0] == ["A", "C", "D", "E", "G", "A"]
    # Second rotation starts on A# (index after A in chromatic order).
    assert out[1][0] == "A#"


def test_generate_twelve_outputs_rejects_bad_inputs():
    with pytest.raises(ValueError):
        generate_twelve_outputs([[2, 2, 1, 2, 2]] * 11, list(CHROMATIC_ORDER), "A")
    with pytest.raises(ValueError):
        generate_twelve_outputs(
            [[2, 2, 1, 2, 2]] * 12, list(CHROMATIC_ORDER)[:11], "A"
        )
    with pytest.raises(ValueError):
        generate_twelve_outputs(
            [[2, 2, 1, 2, 2]] * 12, list(CHROMATIC_ORDER), "H"
        )


def test_wheelmode_properties():
    # WheelMode exposes glyph/family/quality/clock_hour from its role.
    bound = Wheel("A").mode_for("C")
    assert isinstance(bound, WheelMode)
    assert bound.glyph == "□"
    assert bound.family == "hepta"
    assert bound.quality == "major"
    assert bound.clock_hour == 12
