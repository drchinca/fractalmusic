"""Optional FluidSynth + SoundFont rendering. Used only if pyfluidsynth and
an .sf2 file are both present. Otherwise the engine falls back to numpy synth."""

from pathlib import Path

import numpy as np

from fractalmusic.generate.types import Event


def soundfont_available(sf2_path: Path) -> bool:
    """True if pyfluidsynth and the soundfont are both reachable."""
    if not sf2_path.exists():
        return False
    try:
        import fluidsynth  # noqa: F401
    except ImportError:
        return False
    return True


def render_with_soundfont(
    *,
    events: tuple[Event, ...],
    sr: int,
    sf2_path: Path,
    program: int = 0,  # 0 = Acoustic Grand Piano in GM
    bpm: int,
) -> np.ndarray:
    """Render Events through FluidSynth. Returns float32 mono buffer."""
    import fluidsynth

    fs = fluidsynth.Synth(samplerate=float(sr), gain=0.6)
    sfid = fs.sfload(str(sf2_path))
    fs.program_select(0, sfid, 0, program)

    sec_per_beat = 60.0 / bpm
    total_samples = int(max((e.beat + e.duration) * sec_per_beat for e in events) * sr + sr)
    buf = np.zeros(total_samples, dtype=np.float32)
    cursor = 0

    schedule: list[tuple[int, str, int]] = []
    # action: ("on" or "off", midi_note)
    for e in events:
        midi_num = _note_octave_to_midi(e.note, e.octave)
        on_sample = int(e.beat * sec_per_beat * sr)
        off_sample = int((e.beat + e.duration) * sec_per_beat * sr)
        schedule.append((on_sample, "on", midi_num))
        schedule.append((off_sample, "off", midi_num))
    schedule.sort(key=lambda x: x[0])

    for sample_idx, action, note in schedule:
        delta = sample_idx - cursor
        if delta > 0:
            block = fs.get_samples(delta)  # float32 stereo, length = 2*delta
            stereo = np.frombuffer(block, dtype=np.float32).reshape(-1, 2)
            mono = stereo.mean(axis=1)
            end = cursor + mono.shape[0]
            if end > buf.shape[0]:
                end = buf.shape[0]
                mono = mono[: end - cursor]
            buf[cursor:end] = mono
            cursor = end
        if action == "on":
            fs.noteon(0, note, 96)
        else:
            fs.noteoff(0, note)

    # Tail
    if cursor < total_samples:
        delta = total_samples - cursor
        block = fs.get_samples(delta)
        stereo = np.frombuffer(block, dtype=np.float32).reshape(-1, 2)
        mono = stereo.mean(axis=1)[:delta]
        buf[cursor : cursor + mono.shape[0]] = mono

    fs.delete()
    return buf


_PITCH_CLASS: dict[str, int] = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}


def _note_octave_to_midi(note: str, octave: int) -> int:
    """A4 = 69. C-1 = 0."""
    return 12 * (octave + 1) + _PITCH_CLASS[note]
