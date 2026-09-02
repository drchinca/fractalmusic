"""Unit tests — the FluidSynth-free logic in render/soundfont.py.

render_with_soundfont() itself needs pyfluidsynth (not a project dependency
here) plus a real .sf2 file, so it stays untested — that's a real, honest
gap, not a mock. The schedule-building and timing math were extracted into
pure functions specifically so this logic doesn't have to share that fate.
"""

from fractalmusic.generate.types import Event
from fractalmusic.render.soundfont import _note_schedule, _total_samples, soundfont_available


def _event(note: str, *, octave: int = 4, beat: float = 0.0, duration: float = 1.0) -> Event:
    return Event(
        note=note,  # type: ignore[arg-type]
        octave=octave,
        beat=beat,
        duration=duration,
        time_sec=0.0,
        freq_hz=440.0,
        role_hour=9,
        carta_glyph="⋮",
    )


def test_soundfont_unavailable_when_file_does_not_exist(tmp_path):
    assert soundfont_available(tmp_path / "missing.sf2") is False


def test_soundfont_unavailable_when_fluidsynth_not_installed(tmp_path):
    # pyfluidsynth genuinely isn't installed in this environment, so this
    # exercises the real ImportError branch, not a simulated one.
    sf2 = tmp_path / "present.sf2"
    sf2.write_bytes(b"not a real soundfont")
    assert soundfont_available(sf2) is False


def test_total_samples_covers_every_event_plus_one_second_tail():
    events = (_event("A", beat=0.0, duration=1.0), _event("C", beat=1.0, duration=0.5))
    # last event ends at beat 1.5 -> 1.5s at 60bpm; +1s tail = 2.5s @ 1000Hz.
    assert _total_samples(events, sr=1000, bpm=60) == 2500


def test_note_schedule_is_sorted_by_sample_and_pairs_on_off():
    events = (
        _event("A", octave=4, beat=0.0, duration=1.0),
        _event("C", octave=4, beat=1.0, duration=0.5),
    )
    schedule = _note_schedule(events, sr=1000, bpm=60)
    assert schedule == [
        (0, "on", 69),  # A4
        (1000, "off", 69),
        (1000, "on", 60),  # C4
        (1500, "off", 60),
    ]
