"""Produce an original flamenco-style fractal song as WAV + MIDI + JSON.

This is intentionally a producer script, not part of the current
fractalmusic.generate contract. The existing generator produces one event
stream; this script makes a small arranged piece with separate musical roles.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

try:
    import mido
except ImportError:  # pragma: no cover - mido is optional in the package
    mido = None


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "web" / "public" / "generated"
TITLE = "Fractal Flamenco - E Phrygian"
SLUG = "fractal-flamenco-e-phrygian"

SR = 44_100
BPM = 180
PULSE_S = 60.0 / BPM
CYCLE_PULSES = 12
CYCLES = 16
TAIL_S = 3.0
TOTAL_S = CYCLES * CYCLE_PULSES * PULSE_S + TAIL_S
TOTAL_SAMPLES = int(TOTAL_S * SR)

RNG = np.random.default_rng(0xF1A6E)

NOTE_INDEX = {
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

CHORDS: dict[str, tuple[str, ...]] = {
    "Am": ("A2", "E3", "A3", "C4", "E4", "A4"),
    "G": ("G2", "D3", "G3", "B3", "D4", "G4"),
    "F": ("F2", "C3", "F3", "A3", "C4", "F4"),
    "E": ("E2", "B2", "E3", "G#3", "B3", "E4"),
}

PROGRESSION = (("Am", 0), ("G", 3), ("F", 6), ("E", 9))
ACCENTS = {0: 1.0, 3: 0.82, 6: 0.95, 8: 0.72, 10: 0.88}


@dataclass(frozen=True)
class MidiNote:
    track: str
    channel: int
    note: int
    start_s: float
    duration_s: float
    velocity: int


midi_notes: list[MidiNote] = []
percussion_hits: list[tuple[float, int, int, float]] = []


def note_to_midi(note: str) -> int:
    if len(note) == 2:
        name = note[0]
        octave = int(note[1])
    else:
        name = note[:2]
        octave = int(note[2])
    return 12 * (octave + 1) + NOTE_INDEX[name]


def note_to_freq(note: str) -> float:
    return float(440.0 * (2.0 ** ((note_to_midi(note) - 69) / 12.0)))


def add_stereo(buf: np.ndarray, mono: np.ndarray, start_s: float, gain: float, pan: float) -> None:
    start = int(start_s * SR)
    if start >= buf.shape[0]:
        return
    end = min(start + mono.shape[0], buf.shape[0])
    if end <= start:
        return
    chunk = mono[: end - start] * gain
    left = math.cos(pan * math.pi * 0.5)
    right = math.sin(pan * math.pi * 0.5)
    buf[start:end, 0] += chunk * left
    buf[start:end, 1] += chunk * right


def env_curve(length: int, attack_s: float, release_s: float) -> np.ndarray:
    env = np.ones(length, dtype=np.float32)
    attack = min(length, max(1, int(attack_s * SR)))
    release = min(length, max(1, int(release_s * SR)))
    env[:attack] *= np.linspace(0.0, 1.0, attack, dtype=np.float32)
    env[-release:] *= np.linspace(1.0, 0.0, release, dtype=np.float32)
    return env


def plucked_note(
    note: str,
    duration_s: float,
    *,
    brightness: float = 0.72,
    decay: float = 8.0,
) -> np.ndarray:
    freq = note_to_freq(note)
    length = max(1, int((duration_s + 0.45) * SR))
    t = np.arange(length, dtype=np.float32) / SR
    partials = np.zeros(length, dtype=np.float32)
    for harmonic in range(1, 9):
        gain = (brightness**harmonic) / harmonic
        partial_decay = np.exp(-t * decay * (0.45 + harmonic * 0.12))
        phase = RNG.uniform(0, math.tau)
        partials += gain * np.sin(math.tau * freq * harmonic * t + phase) * partial_decay
    pick = RNG.normal(0.0, 0.05, length).astype(np.float32) * np.exp(-t * 55.0)
    body = partials + pick
    body *= env_curve(length, attack_s=0.002, release_s=0.28)
    peak = float(np.max(np.abs(body)))
    if peak > 0:
        body /= peak
    return body.astype(np.float32)


def bass_note(note: str, duration_s: float) -> np.ndarray:
    freq = note_to_freq(note)
    length = max(1, int((duration_s + 0.12) * SR))
    t = np.arange(length, dtype=np.float32) / SR
    wave = 0.75 * np.sin(math.tau * freq * t)
    wave += 0.22 * np.sin(math.tau * freq * 2.0 * t)
    wave += 0.08 * np.sin(math.tau * freq * 3.0 * t)
    wave *= np.exp(-t * 1.8)
    wave *= env_curve(length, attack_s=0.006, release_s=0.09)
    return wave.astype(np.float32)


def clap(length_s: float = 0.11) -> np.ndarray:
    length = max(1, int(length_s * SR))
    t = np.arange(length, dtype=np.float32) / SR
    noise = RNG.normal(0.0, 1.0, length).astype(np.float32)
    env = np.exp(-t * 33.0)
    flam = np.zeros(length, dtype=np.float32)
    for offset_ms, gain in ((0.0, 1.0), (13.0, 0.72), (27.0, 0.46)):
        offset = int(offset_ms * SR / 1000.0)
        if offset < length:
            flam[offset:] += noise[: length - offset] * gain
    return (flam * env * env_curve(length, 0.001, 0.035)).astype(np.float32)


def cajon_low() -> np.ndarray:
    length = int(0.22 * SR)
    t = np.arange(length, dtype=np.float32) / SR
    tone = np.sin(math.tau * 82.0 * t) * np.exp(-t * 18.0)
    click = RNG.normal(0.0, 0.28, length).astype(np.float32) * np.exp(-t * 80.0)
    return (tone + click).astype(np.float32)


def cajon_slap() -> np.ndarray:
    length = int(0.12 * SR)
    t = np.arange(length, dtype=np.float32) / SR
    noise = RNG.normal(0.0, 1.0, length).astype(np.float32)
    tone = np.sin(math.tau * 190.0 * t) * 0.22
    return ((noise + tone) * np.exp(-t * 42.0)).astype(np.float32)


def foot_tap() -> np.ndarray:
    length = int(0.055 * SR)
    t = np.arange(length, dtype=np.float32) / SR
    tap = RNG.normal(0.0, 0.5, length).astype(np.float32) * np.exp(-t * 95.0)
    tap += np.sin(math.tau * 135.0 * t) * np.exp(-t * 70.0)
    return tap.astype(np.float32)


def schedule_note(
    track: str,
    note: str,
    start_s: float,
    duration_s: float,
    velocity: int,
    channel: int,
) -> None:
    midi_notes.append(
        MidiNote(
            track=track,
            channel=channel,
            note=note_to_midi(note),
            start_s=start_s,
            duration_s=duration_s,
            velocity=velocity,
        )
    )


def cycle_time(cycle: int, pulse: float) -> float:
    return (cycle * CYCLE_PULSES + pulse) * PULSE_S


def section_gain(cycle: int) -> float:
    if cycle < 2:
        return 0.55
    if cycle < 6:
        return 0.78
    if cycle < 10:
        return 0.9
    if cycle < 14:
        return 1.05
    return 0.82


def render_rhythm_guitar(buf: np.ndarray) -> None:
    for cycle in range(CYCLES):
        gain = section_gain(cycle)
        for chord_name, base_pulse in PROGRESSION:
            chord = CHORDS[chord_name]
            pulses = (base_pulse, base_pulse + 1, base_pulse + 2)
            for local_idx, pulse in enumerate(pulses):
                accent = ACCENTS.get(int(pulse) % CYCLE_PULSES, 0.36)
                if cycle < 2 and local_idx == 1:
                    accent *= 0.45
                start = cycle_time(cycle, pulse)
                direction = -1 if int(pulse) in (3, 8, 10) else 1
                notes = chord if direction > 0 else tuple(reversed(chord))
                for string_idx, note in enumerate(notes):
                    delay = string_idx * 0.009
                    add_stereo(
                        buf,
                        plucked_note(note, 0.72, brightness=0.64, decay=7.5),
                        start + delay,
                        0.075 * accent * gain,
                        0.36 + string_idx * 0.055,
                    )
                    schedule_note(
                        "Rhythm Guitar",
                        note,
                        start + delay,
                        0.42,
                        int(52 + accent * 38),
                        0,
                    )
                if cycle >= 10 and int(pulse) in (8, 10):
                    for burst in range(1, 4):
                        burst_start = start + burst * 0.035
                        for string_idx, note in enumerate(reversed(chord[1:])):
                            add_stereo(
                                buf,
                                plucked_note(note, 0.36, brightness=0.58, decay=10.0),
                                burst_start + string_idx * 0.004,
                                0.04 * accent * gain,
                                0.43,
                            )


def render_bass(buf: np.ndarray) -> None:
    roots = {"Am": "A1", "G": "G1", "F": "F1", "E": "E1"}
    for cycle in range(2, CYCLES):
        gain = 0.62 if cycle < 10 else 0.78
        if cycle >= 14:
            gain *= 0.72
        for chord_name, pulse in PROGRESSION:
            start = cycle_time(cycle, pulse)
            root = roots[chord_name]
            add_stereo(buf, bass_note(root, 1.0), start, 0.21 * gain, 0.5)
            schedule_note("Bass", root, start, 0.94, 72, 1)
            if chord_name == "E" and cycle >= 6:
                pickup = cycle_time(cycle, pulse + 2.25)
                add_stereo(buf, bass_note("B1", 0.28), pickup, 0.12 * gain, 0.5)
                schedule_note("Bass", "B1", pickup, 0.25, 58, 1)


FALSETAS: tuple[tuple[tuple[str, float], ...], ...] = (
    (
        ("E5", 0.75),
        ("F5", 0.25),
        ("G5", 0.5),
        ("F5", 0.5),
        ("E5", 0.5),
        ("D5", 0.5),
        ("C5", 0.5),
        ("B4", 0.5),
        ("A4", 0.75),
        ("B4", 0.25),
        ("C5", 0.5),
        ("B4", 0.5),
        ("G#4", 1.0),
        ("E4", 1.0),
        ("F4", 0.5),
        ("E4", 0.5),
    ),
    (
        ("A4", 0.5),
        ("C5", 0.5),
        ("D5", 0.5),
        ("E5", 0.5),
        ("F5", 0.75),
        ("E5", 0.25),
        ("D5", 0.5),
        ("C5", 0.5),
        ("B4", 0.5),
        ("G#4", 0.5),
        ("A4", 0.5),
        ("B4", 0.5),
        ("C5", 0.5),
        ("B4", 0.5),
        ("G#4", 1.0),
        ("E4", 1.0),
    ),
)


def render_lead(buf: np.ndarray) -> None:
    for cycle in range(2, 15):
        motif = FALSETAS[cycle % len(FALSETAS)]
        cursor = 0.0
        gain = 0.09 if cycle < 6 else 0.13
        if cycle >= 10:
            gain = 0.16
        if cycle >= 14:
            gain *= 0.74
        for note, pulses in motif:
            start = cycle_time(cycle, cursor)
            duration = max(0.11, pulses * PULSE_S * 0.9)
            add_stereo(
                buf,
                plucked_note(note, duration, brightness=0.82, decay=9.5),
                start,
                gain,
                0.68,
            )
            schedule_note("Lead Guitar", note, start, duration, 75, 2)
            if pulses >= 0.75 and cycle >= 6:
                grace = start + duration * 0.58
                grace_note = "F5" if note == "E5" else note
                add_stereo(
                    buf,
                    plucked_note(grace_note, 0.16, brightness=0.9, decay=15.0),
                    grace,
                    gain * 0.38,
                    0.72,
                )
            cursor += pulses
            if cursor >= CYCLE_PULSES:
                break


def render_percussion(buf: np.ndarray) -> None:
    for cycle in range(CYCLES):
        gain = section_gain(cycle)
        for pulse in range(CYCLE_PULSES):
            start = cycle_time(cycle, pulse)
            if cycle >= 2:
                add_stereo(buf, foot_tap(), start, 0.045 * gain, 0.18)
                percussion_hits.append((start, 44, 38, 0.04))
            accent = ACCENTS.get(pulse, 0.0)
            if accent > 0:
                if cycle >= 1:
                    add_stereo(buf, clap(), start + 0.012, 0.15 * accent * gain, 0.78)
                    percussion_hits.append((start + 0.012, 39, int(54 + 40 * accent), 0.05))
                if cycle >= 2 and pulse in (0, 6, 10):
                    add_stereo(buf, cajon_low(), start, 0.24 * accent * gain, 0.48)
                    percussion_hits.append((start, 36, int(70 + 24 * accent), 0.08))
                if cycle >= 2 and pulse in (3, 8):
                    add_stereo(buf, cajon_slap(), start + 0.006, 0.16 * accent * gain, 0.54)
                    percussion_hits.append((start + 0.006, 38, int(62 + 28 * accent), 0.06))
        if 10 <= cycle <= 13:
            for offset in (10.0, 10.33, 10.66, 11.0):
                start = cycle_time(cycle, offset)
                add_stereo(buf, cajon_slap(), start, 0.09 * gain, 0.58)
                percussion_hits.append((start, 38, 58, 0.04))


def add_room(buf: np.ndarray) -> np.ndarray:
    wet = np.zeros_like(buf)
    taps = (
        (0.031, 0.22, -0.08),
        (0.067, 0.16, 0.06),
        (0.119, 0.11, -0.04),
        (0.191, 0.08, 0.05),
        (0.283, 0.05, -0.02),
    )
    for delay_s, gain, cross in taps:
        delay = int(delay_s * SR)
        wet[delay:] += buf[:-delay] * gain
        wet[delay:, 0] += buf[:-delay, 1] * cross
        wet[delay:, 1] += buf[:-delay, 0] * cross
    return buf + wet


def write_midi(path: Path) -> None:
    if mido is None:
        return
    ticks_per_beat = 480
    mid = mido.MidiFile(type=1, ticks_per_beat=ticks_per_beat)
    tempo = mido.bpm2tempo(BPM)

    track_specs = {
        "Rhythm Guitar": (0, 24),
        "Bass": (1, 32),
        "Lead Guitar": (2, 24),
    }

    for name, (channel, program) in track_specs.items():
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage("track_name", name=name, time=0))
        track.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))
        track.append(mido.Message("program_change", channel=channel, program=program, time=0))
        events: list[tuple[int, int, mido.Message]] = []
        for item in midi_notes:
            if item.track != name:
                continue
            start_tick = int((item.start_s / PULSE_S) * ticks_per_beat)
            end_tick = int(((item.start_s + item.duration_s) / PULSE_S) * ticks_per_beat)
            events.append(
                (
                    start_tick,
                    0,
                    mido.Message(
                        "note_on",
                        channel=channel,
                        note=item.note,
                        velocity=item.velocity,
                        time=0,
                    ),
                )
            )
            events.append(
                (
                    end_tick,
                    1,
                    mido.Message("note_off", channel=channel, note=item.note, velocity=0, time=0),
                )
            )
        events.sort(key=lambda x: (x[0], x[1]))
        cursor = 0
        for tick, _order, msg in events:
            msg.time = max(0, tick - cursor)
            track.append(msg)
            cursor = tick

    drum = mido.MidiTrack()
    mid.tracks.append(drum)
    drum.append(mido.MetaMessage("track_name", name="Cajon Palmas Foot", time=0))
    drum.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))
    drum_events: list[tuple[int, int, mido.Message]] = []
    for start_s, note, velocity, dur_s in percussion_hits:
        start_tick = int((start_s / PULSE_S) * ticks_per_beat)
        end_tick = int(((start_s + dur_s) / PULSE_S) * ticks_per_beat)
        drum_events.append(
            (
                start_tick,
                0,
                mido.Message("note_on", channel=9, note=note, velocity=velocity, time=0),
            )
        )
        drum_events.append(
            (
                end_tick,
                1,
                mido.Message("note_off", channel=9, note=note, velocity=0, time=0),
            )
        )
    drum_events.sort(key=lambda x: (x[0], x[1]))
    cursor = 0
    for tick, _order, msg in drum_events:
        msg.time = max(0, tick - cursor)
        drum.append(msg)
        cursor = tick

    mid.save(path)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mix = np.zeros((TOTAL_SAMPLES, 2), dtype=np.float32)

    render_rhythm_guitar(mix)
    render_bass(mix)
    render_lead(mix)
    render_percussion(mix)

    mix = add_room(mix)
    peak = float(np.max(np.abs(mix)))
    if peak > 0:
        mix *= 0.92 / peak
    mix = np.tanh(mix * 1.08).astype(np.float32)
    peak = float(np.max(np.abs(mix)))
    if peak > 0:
        mix *= 0.95 / peak

    wav_path = OUT_DIR / f"{SLUG}.wav"
    midi_path = OUT_DIR / f"{SLUG}.mid"
    meta_path = OUT_DIR / f"{SLUG}.json"

    sf.write(wav_path, mix, SR, subtype="PCM_16")
    write_midi(midi_path)

    metadata = {
        "title": TITLE,
        "style": "original flamenco-style instrumental",
        "key_center": "E",
        "mode": "E Phrygian with E major cadential color",
        "bpm": BPM,
        "compas": "12-pulse cycle, accents on 12, 3, 6, 8, 10",
        "duration_seconds": round(TOTAL_S, 3),
        "sections": [
            {"cycles": "1-2", "name": "intro", "layers": ["guitar", "soft palmas"]},
            {"cycles": "3-6", "name": "entrada", "layers": ["guitar", "bass", "cajon"]},
            {"cycles": "7-10", "name": "falseta", "layers": ["lead guitar", "palmas"]},
            {"cycles": "11-14", "name": "build", "layers": ["rasgueado", "percussion fills"]},
            {"cycles": "15-16", "name": "cierre", "layers": ["cadence", "outro"]},
        ],
        "tracks": ["Rhythm Guitar", "Lead Guitar", "Bass", "Cajon", "Palmas", "Foot Taps"],
        "files": {
            "wav": str(wav_path.relative_to(ROOT)),
            "midi": str(midi_path.relative_to(ROOT)) if midi_path.exists() else None,
        },
        "midi_note_counts": {
            track: sum(1 for note in midi_notes if note.track == track)
            for track in sorted({note.track for note in midi_notes})
        },
        "percussion_hits": len(percussion_hits),
    }
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {**metadata, "absolute_wav": str(wav_path), "absolute_midi": str(midi_path)}, indent=2
        )
    )


if __name__ == "__main__":
    main()
