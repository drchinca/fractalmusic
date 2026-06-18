"""Integration tests — fractalmusic scales/triads round-trip into pytheory."""

import pytest
from pytheory import Tone

from fractalmusic import Wheel, mode_scale, penta, triad_for


def test_eolico_scale_yields_seven_ascending_tones() -> None:
    tones = mode_scale("A").to_pytheory()
    assert len(tones) == 7
    assert all(isinstance(t, Tone) for t in tones)
    # Ascending across whatever octaves the wrap produced.
    freqs = [t.frequency for t in tones]
    assert freqs == sorted(freqs)


def test_penta_scale_yields_five_ascending_tones() -> None:
    tones = penta("C#", mode="I").to_pytheory()
    assert len(tones) == 5
    freqs = [t.frequency for t in tones]
    assert freqs == sorted(freqs)


def test_triad_yields_three_tones_in_order() -> None:
    tones = triad_for("A").to_pytheory()
    assert len(tones) == 3
    # A C E — minor triad, ascending root.
    assert [t.full_name for t in tones] == ["A4", "C5", "E5"]


def test_wheel_scale_via_default_tonic_matches_mode_scale() -> None:
    # Sanity: book-default Wheel('A').mode_for('C').scale_notes() must agree
    # with the canonical mode_scale path used by to_pytheory.
    wheel = Wheel("A")
    bound = wheel.mode_for("C")
    assert bound.scale_notes() == mode_scale("C").notes


def test_octave_argument_anchors_starting_pitch() -> None:
    tones = mode_scale("A").to_pytheory(octave=3)
    assert tones[0].full_name == "A3"


@pytest.mark.parametrize("note,expected_root", [("A", "A4"), ("D", "D4"), ("F", "F4")])
def test_triad_root_matches_requested_note(note: str, expected_root: str) -> None:
    tones = triad_for(note).to_pytheory()
    assert tones[0].full_name == expected_root
