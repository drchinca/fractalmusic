"""Unit tests — the wheel-rotation, enharmonic, and fretboard tables baked
into web/public/data.json, so the FE never recomputes this math itself."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from fractalmusic.modes import CHROMATIC_ORDER  # noqa: E402

from build_gatople_data import (  # noqa: E402
    _build_enharmonic,
    _build_fretboard,
    _build_rotations,
    build_payload,
)


def test_rotations_at_a_tonic_is_the_identity():
    # tonicOffset=0 is A — spinning to A should reproduce CHROMATIC_ORDER
    # itself, since A already sits at its own default position.
    rotations = _build_rotations()
    assert rotations[0] == list(CHROMATIC_ORDER)


def test_rotations_matches_wheel_directly_for_every_tonic():
    from fractalmusic.wheel import Wheel

    rotations = _build_rotations()
    for tonic_idx, tonic in enumerate(CHROMATIC_ORDER):
        wheel = Wheel(tonic=tonic)
        for position in range(12):
            assert rotations[tonic_idx][position] == wheel.note_at_position(position)


def test_rotations_is_twelve_by_twelve():
    rotations = _build_rotations()
    assert len(rotations) == 12
    assert all(len(row) == 12 for row in rotations)


def test_enharmonic_covers_exactly_the_five_black_keys():
    enharmonic = _build_enharmonic()
    assert enharmonic == {
        "A#": "Bb",
        "C#": "Db",
        "D#": "Eb",
        "F#": "Gb",
        "G#": "Ab",
    }


def test_fretboard_matches_real_guitar_notes_for_standard_tuning():
    fretboard = _build_fretboard()
    # Standard tuning, low to high: E A D G B E.
    assert len(fretboard) == 6
    # Low E string: open E, 12 frets, octave E at fret 12.
    assert fretboard[0][0] == "E"
    assert fretboard[0][12] == "E"
    assert fretboard[0] == ["E", "F", "F#", "G", "G#", "A", "A#", "B", "C", "C#", "D", "D#", "E"]
    # A string: open A.
    assert fretboard[1][0] == "A"


def test_fretboard_reuses_svgs_own_tuning_constant():
    from fractalmusic.svg import _GUITAR_TUNING

    fretboard = _build_fretboard()
    assert [row[0] for row in fretboard] == list(_GUITAR_TUNING)


def test_build_payload_includes_all_three_new_keys():
    payload = build_payload()
    assert "rotations" in payload
    assert "enharmonic" in payload
    assert "fretboard" in payload
