"""Pattern → Event sequence. Pre-bakes time_sec, freq_hz, role_hour, carta_glyph."""

import random
from typing import Final

from fractalmusic.generate.types import (
    NOTE_NAMES,
    PENTA_MODES,
    Event,
    Pattern,
)
from fractalmusic.modes import MODE_BY_NOTE
from fractalmusic.wheel import ROLES, Wheel, _note_index

A4_FREQ_HZ: Final[float] = 440.0
A4_MIDI: Final[int] = 69
DEFAULT_BPM: Final[int] = 96
DEFAULT_OCTAVE: Final[int] = 4
DEFAULT_VELOCITY_MIDI: Final[int] = 96


def _midi_number(note: str, octave: int) -> int:
    """MIDI number from sharp note name + octave (C4=60, A4=69)."""
    pc_order = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    if note not in pc_order:
        raise ValueError(f"unknown note: {note!r}")
    return 12 * (octave + 1) + pc_order.index(note)


def _freq_hz(note: str, octave: int) -> float:
    """Equal-temperament frequency in Hz for a note + octave."""
    midi = _midi_number(note, octave)
    return A4_FREQ_HZ * (2.0 ** ((midi - A4_MIDI) / 12.0))


def freq_for(note: str, octave: int) -> float:
    """Public wrapper around the equal-temperament freq formula.

    Anything outside this module that needs the freq of a (note, octave)
    pair should use this instead of re-deriving the math.
    """
    return _freq_hz(note=note, octave=octave)


def _scale_for_mode(wheel: Wheel, mode: str) -> tuple[str, ...]:
    """Scale notes for `mode` rooted at the wheel's tonic.

    For heptatonic modes the tonic itself sits at the matching role; for penta
    modes we look up the canonical penta root and read the scale from there.
    """
    if mode in PENTA_MODES:
        penta_index = int(mode.split()[1])  # "Penta 3" → 3
        roman = ["I", "II", "III", "IV", "V"][penta_index - 1]
        return wheel.penta(roman)
    canonical_note = next(n for n, m in MODE_BY_NOTE.items() if m.mode_name == mode)
    position_at_default = _note_index(canonical_note)
    note_under_role = wheel.note_at_position(position_at_default)
    return wheel.mode_for(note_under_role).scale_notes()


def realize(pattern: Pattern, *, seed: int = 0, bpm: int = DEFAULT_BPM) -> tuple[Event, ...]:
    """Realize a Pattern into pre-baked Events.

    Each degree (1-indexed) selects the corresponding scale note. role_hour and
    carta_glyph are read off the Wheel so the FE can highlight cartas as the
    music plays.
    """
    rng = random.Random(seed)
    wheel = Wheel(tonic=pattern.tonic)
    scale = _scale_for_mode(wheel=wheel, mode=pattern.mode)
    seconds_per_beat = 60.0 / bpm

    events: list[Event] = []
    beat_cursor = 0.0
    for degree, dur_beats in zip(pattern.degrees, pattern.rhythm, strict=True):
        idx = (degree - 1) % len(scale)
        note = scale[idx]
        if note not in NOTE_NAMES:
            raise ValueError(f"realize produced non-canonical note: {note!r}")
        octave = DEFAULT_OCTAVE + rng.choice([0, 0, 0, 1, -1])
        position = (_note_index(note) - wheel.tonic_index) % 12
        role = ROLES[position]
        events.append(
            Event(
                note=note,  # type: ignore[arg-type]
                octave=octave,
                beat=beat_cursor,
                duration=dur_beats,
                time_sec=beat_cursor * seconds_per_beat,
                freq_hz=round(_freq_hz(note=note, octave=octave), 4),
                role_hour=role.clock_hour,
                carta_glyph=role.glyph,
            )
        )
        beat_cursor += dur_beats
    return tuple(events)
