"""Produce an original uplifting pop song with trumpet hooks.

Outputs:
  web/public/generated/uplifting-pop-trumpets.wav
  web/public/generated/uplifting-pop-trumpets.mid
  web/public/generated/uplifting-pop-trumpets.json
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
except ImportError:  # pragma: no cover - optional dependency
    mido = None


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "web" / "public" / "generated"
TITLE = "Sunrise Parade"
SLUG = "uplifting-pop-trumpets"

SR = 44_100
BPM = 126
BEAT_S = 60.0 / BPM
BARS = 56
BEATS_PER_BAR = 4
TAIL_S = 4.0
TOTAL_S = BARS * BEATS_PER_BAR * BEAT_S + TAIL_S
TOTAL_SAMPLES = int(TOTAL_S * SR)

RNG = np.random.default_rng(0x50A7)

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
    "C": ("C3", "G3", "C4", "E4", "G4"),
    "G": ("G2", "D3", "G3", "B3", "D4"),
    "Am": ("A2", "E3", "A3", "C4", "E4"),
    "F": ("F2", "C3", "F3", "A3", "C4"),
    "Dm": ("D3", "A3", "D4", "F4", "A4"),
    "Em": ("E3", "B3", "E4", "G4", "B4"),
}

PROGRESSION = ("C", "G", "Am", "F")
PRECHORUS = ("Dm", "F", "C", "G")
BRIDGE = ("Am", "F", "C", "G")


@dataclass(frozen=True)
class MidiNote:
    track: str
    channel: int
    note: int
    start_s: float
    duration_s: float
    velocity: int


midi_notes: list[MidiNote] = []
drum_hits: list[tuple[float, int, int, float]] = []


def note_to_midi(note: str) -> int:
    if len(note) == 2:
        name = note[0]
        octave = int(note[1])
    else:
        name = note[:2]
        octave = int(note[2])
    return 12 * (octave + 1) + NOTE_INDEX[name]


def note_to_freq(note: str) -> float:
    return 440.0 * (2.0 ** ((note_to_midi(note) - 69) / 12.0))


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


def env_adsr(length: int, attack_s: float, decay_s: float, sustain: float, release_s: float) -> np.ndarray:
    attack = max(1, int(attack_s * SR))
    decay = max(1, int(decay_s * SR))
    release = max(1, int(release_s * SR))
    body = max(1, length - release)
    if attack + decay > body:
        attack = max(1, body // 2)
        decay = max(1, body - attack)
    sustain_len = max(0, body - attack - decay)
    parts = [
        np.linspace(0.0, 1.0, attack, dtype=np.float32),
        np.linspace(1.0, sustain, decay, dtype=np.float32),
        np.full(sustain_len, sustain, dtype=np.float32),
        np.linspace(sustain, 0.0, release, dtype=np.float32),
    ]
    env = np.concatenate(parts)
    if env.shape[0] < length:
        env = np.pad(env, (0, length - env.shape[0]))
    return env[:length]


def schedule_note(track: str, note: str, start_s: float, duration_s: float, velocity: int, channel: int) -> None:
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


def bar_time(bar: int, beat: float = 0.0) -> float:
    return (bar * BEATS_PER_BAR + beat) * BEAT_S


def section_for_bar(bar: int) -> str:
    if bar < 4:
        return "intro"
    if bar < 16:
        return "verse"
    if bar < 24:
        return "prechorus"
    if bar < 40:
        return "chorus"
    if bar < 48:
        return "bridge"
    if bar < 56:
        return "final_chorus"
    return "outro"


def section_gain(bar: int) -> float:
    section = section_for_bar(bar)
    return {
        "intro": 0.52,
        "verse": 0.7,
        "prechorus": 0.82,
        "chorus": 1.02,
        "bridge": 0.76,
        "final_chorus": 1.12,
    }[section]


def chord_for_bar(bar: int) -> str:
    section = section_for_bar(bar)
    if section == "prechorus":
        return PRECHORUS[(bar - 16) % len(PRECHORUS)]
    if section == "bridge":
        return BRIDGE[(bar - 40) % len(BRIDGE)]
    return PROGRESSION[bar % len(PROGRESSION)]


def pulse_note(freq_hz: float, duration_s: float, *, kind: str, velocity: float = 1.0) -> np.ndarray:
    length = max(1, int((duration_s + 0.04) * SR))
    t = np.arange(length, dtype=np.float32) / SR
    if kind == "piano":
        wave = np.zeros(length, dtype=np.float32)
        for harmonic, gain in ((1, 1.0), (2, 0.32), (3, 0.18), (4, 0.08)):
            wave += gain * np.sin(math.tau * freq_hz * harmonic * t + RNG.uniform(0, math.tau))
        wave *= np.exp(-t * 2.8)
        env = env_adsr(length, 0.004, 0.18, 0.28, 0.16)
    elif kind == "pad":
        detune = 2.0 ** (7.0 / 1200.0)
        wave = 0.45 * np.sin(math.tau * freq_hz * t)
        wave += 0.35 * np.sin(math.tau * freq_hz * detune * t)
        wave += 0.18 * np.sin(math.tau * freq_hz * 2.0 * t)
        env = env_adsr(length, 0.18, 0.4, 0.75, 0.8)
    elif kind == "bass":
        wave = 0.8 * np.sin(math.tau * freq_hz * t)
        wave += 0.25 * np.sin(math.tau * freq_hz * 2.0 * t)
        wave += 0.1 * np.sign(np.sin(math.tau * freq_hz * t))
        env = env_adsr(length, 0.006, 0.1, 0.6, 0.08)
    else:
        raise ValueError(kind)
    peak = float(np.max(np.abs(wave)))
    if peak > 0:
        wave /= peak
    return (wave * env * velocity).astype(np.float32)


def trumpet_note(note: str, duration_s: float, *, brightness: float = 1.0) -> np.ndarray:
    freq = note_to_freq(note)
    length = max(1, int((duration_s + 0.11) * SR))
    t = np.arange(length, dtype=np.float32) / SR
    vibrato = 1.0 + 0.004 * np.sin(math.tau * 5.8 * t)
    phase = np.cumsum(freq * vibrato) / SR
    saw = np.zeros(length, dtype=np.float32)
    for harmonic in range(1, 13):
        gain = (brightness / harmonic) * (1.0 if harmonic < 7 else 0.45)
        saw += gain * np.sin(math.tau * harmonic * phase + RNG.uniform(-0.04, 0.04))
    buzz = 0.08 * np.sign(np.sin(math.tau * freq * t))
    breath = RNG.normal(0.0, 0.015, length).astype(np.float32)
    wave = saw + buzz + breath
    env = env_adsr(length, 0.035, 0.09, 0.86, 0.14)
    # A gentle moving low-pass approximation by mixing with a delayed copy.
    smoothed = wave.copy()
    for _ in range(3):
        smoothed[1:] = 0.72 * smoothed[1:] + 0.28 * smoothed[:-1]
    wave = 0.72 * wave + 0.28 * smoothed
    peak = float(np.max(np.abs(wave)))
    if peak > 0:
        wave /= peak
    return (wave * env).astype(np.float32)


def kick() -> np.ndarray:
    length = int(0.32 * SR)
    t = np.arange(length, dtype=np.float32) / SR
    freq = 52.0 + 68.0 * np.exp(-t * 34.0)
    phase = np.cumsum(freq) / SR
    tone = np.sin(math.tau * phase) * np.exp(-t * 12.0)
    click = RNG.normal(0.0, 0.18, length).astype(np.float32) * np.exp(-t * 90.0)
    return (tone + click).astype(np.float32)


def snare() -> np.ndarray:
    length = int(0.22 * SR)
    t = np.arange(length, dtype=np.float32) / SR
    noise = RNG.normal(0.0, 1.0, length).astype(np.float32) * np.exp(-t * 24.0)
    tone = np.sin(math.tau * 190.0 * t) * np.exp(-t * 18.0) * 0.32
    return (noise + tone).astype(np.float32)


def hat(open_hat: bool = False) -> np.ndarray:
    length = int((0.22 if open_hat else 0.07) * SR)
    t = np.arange(length, dtype=np.float32) / SR
    noise = RNG.normal(0.0, 1.0, length).astype(np.float32)
    shimmer = np.sin(math.tau * 7800.0 * t) * 0.18
    return ((noise + shimmer) * np.exp(-t * (16.0 if open_hat else 72.0))).astype(np.float32)


def clap() -> np.ndarray:
    length = int(0.18 * SR)
    t = np.arange(length, dtype=np.float32) / SR
    out = np.zeros(length, dtype=np.float32)
    for offset_ms, gain in ((0.0, 0.8), (11.0, 1.0), (23.0, 0.62)):
        offset = int(offset_ms * SR / 1000.0)
        noise = RNG.normal(0.0, 1.0, length - offset).astype(np.float32)
        out[offset:] += noise * gain
    return (out * np.exp(-t * 28.0)).astype(np.float32)


def render_harmony(buf: np.ndarray) -> None:
    for bar in range(BARS):
        chord_name = chord_for_bar(bar)
        chord = CHORDS[chord_name]
        gain = section_gain(bar)
        section = section_for_bar(bar)
        rhythm = (0.0, 1.5, 2.0, 3.0) if section in {"chorus", "final_chorus"} else (0.0, 2.0, 3.0)
        for beat in rhythm:
            dur = 0.62 if beat != 0.0 else 0.9
            for idx, note in enumerate(chord[1:]):
                start = bar_time(bar, beat) + idx * 0.008
                add_stereo(
                    buf,
                    pulse_note(note_to_freq(note), dur, kind="piano", velocity=0.9),
                    start,
                    0.09 * gain,
                    0.34 + idx * 0.055,
                )
                schedule_note("Piano", note, start, dur, int(50 + gain * 35), 0)
        if section not in {"intro"}:
            for idx, note in enumerate(chord[1:]):
                start = bar_time(bar, 0.0) + idx * 0.012
                add_stereo(
                    buf,
                    pulse_note(note_to_freq(note), 3.8 * BEAT_S, kind="pad", velocity=0.6),
                    start,
                    0.035 * gain,
                    0.24 + idx * 0.1,
                )
                schedule_note("Synth Pad", note, start, 3.6 * BEAT_S, 42, 3)


def render_bass(buf: np.ndarray) -> None:
    roots = {"C": "C2", "G": "G1", "Am": "A1", "F": "F1", "Dm": "D2", "Em": "E2"}
    fifths = {"C": "G2", "G": "D2", "Am": "E2", "F": "C2", "Dm": "A2", "Em": "B2"}
    for bar in range(4, BARS):
        chord = chord_for_bar(bar)
        gain = section_gain(bar)
        pattern = (0.0, 1.0, 2.0, 2.5, 3.0) if section_for_bar(bar) in {"chorus", "final_chorus"} else (0.0, 2.0, 3.0)
        for beat in pattern:
            note = roots[chord] if beat in (0.0, 2.0, 3.0) else fifths[chord]
            dur = 0.45 if beat in (2.5, 3.0) else 0.72
            start = bar_time(bar, beat)
            add_stereo(buf, pulse_note(note_to_freq(note), dur, kind="bass", velocity=0.9), start, 0.19 * gain, 0.5)
            schedule_note("Bass", note, start, dur, int(58 + gain * 25), 1)


HOOK_A: tuple[tuple[str, float, float], ...] = (
    ("E5", 0.0, 0.5),
    ("G5", 0.5, 0.5),
    ("A5", 1.0, 0.75),
    ("G5", 1.75, 0.25),
    ("E5", 2.0, 0.5),
    ("D5", 2.5, 0.5),
    ("C5", 3.0, 1.0),
)

HOOK_B: tuple[tuple[str, float, float], ...] = (
    ("G5", 0.0, 0.5),
    ("A5", 0.5, 0.5),
    ("C6", 1.0, 0.75),
    ("A5", 1.75, 0.25),
    ("G5", 2.0, 0.5),
    ("E5", 2.5, 0.5),
    ("D5", 3.0, 1.0),
)

VERSE_RIFF: tuple[tuple[str, float, float], ...] = (
    ("C5", 0.0, 0.35),
    ("E5", 0.5, 0.35),
    ("G5", 1.0, 0.35),
    ("E5", 1.5, 0.35),
    ("D5", 2.5, 0.35),
    ("E5", 3.0, 0.5),
)


def add_trumpet_phrase(
    buf: np.ndarray,
    bar: int,
    phrase: tuple[tuple[str, float, float], ...],
    *,
    gain: float,
    harmony: bool,
) -> None:
    for note, beat, dur_beats in phrase:
        start = bar_time(bar, beat)
        dur = dur_beats * BEAT_S * 0.92
        add_stereo(buf, trumpet_note(note, dur, brightness=1.0), start, gain, 0.64)
        schedule_note("Trumpet Lead", note, start, dur, 88, 2)
        if harmony:
            harmony_note = {
                "C5": "E5",
                "D5": "F5",
                "E5": "G5",
                "G5": "B5",
                "A5": "C6",
                "C6": "E6",
            }.get(note)
            if harmony_note is not None:
                add_stereo(buf, trumpet_note(harmony_note, dur, brightness=0.92), start + 0.012, gain * 0.56, 0.78)
                schedule_note("Trumpet Harmony", harmony_note, start + 0.012, dur, 78, 4)


def render_trumpets(buf: np.ndarray) -> None:
    for bar in range(BARS):
        section = section_for_bar(bar)
        if section == "verse" and bar % 4 in (1, 3):
            add_trumpet_phrase(buf, bar, VERSE_RIFF, gain=0.065, harmony=False)
        elif section == "prechorus" and bar % 2 == 1:
            phrase = HOOK_A if bar % 4 == 1 else HOOK_B
            add_trumpet_phrase(buf, bar, phrase, gain=0.09, harmony=False)
        elif section in {"chorus", "final_chorus"}:
            phrase = HOOK_A if bar % 2 == 0 else HOOK_B
            add_trumpet_phrase(buf, bar, phrase, gain=0.14 if section == "chorus" else 0.16, harmony=True)
        elif section == "bridge" and bar in (42, 46):
            add_trumpet_phrase(buf, bar, HOOK_B, gain=0.075, harmony=False)


def render_drums(buf: np.ndarray) -> None:
    for bar in range(BARS):
        section = section_for_bar(bar)
        if section == "intro":
            if bar >= 2:
                for beat in (1.0, 3.0):
                    start = bar_time(bar, beat)
                    add_stereo(buf, clap(), start, 0.08, 0.56)
                    drum_hits.append((start, 39, 46, 0.06))
            continue
        gain = section_gain(bar)
        kick_beats = (0.0, 2.0) if section in {"verse", "bridge"} else (0.0, 1.5, 2.0, 3.0)
        for beat in kick_beats:
            start = bar_time(bar, beat)
            add_stereo(buf, kick(), start, 0.23 * gain, 0.5)
            drum_hits.append((start, 36, int(72 + 20 * gain), 0.08))
        for beat in (1.0, 3.0):
            start = bar_time(bar, beat)
            add_stereo(buf, snare(), start, 0.13 * gain, 0.5)
            add_stereo(buf, clap(), start + 0.014, 0.075 * gain, 0.62)
            drum_hits.append((start, 38, int(68 + 16 * gain), 0.08))
            drum_hits.append((start + 0.014, 39, int(58 + 14 * gain), 0.06))
        hat_step = 0.5 if section in {"verse", "bridge"} else 0.25
        beat = 0.0
        while beat < 4.0:
            start = bar_time(bar, beat)
            open_hat = section in {"chorus", "final_chorus"} and abs(beat - 3.5) < 0.001
            add_stereo(buf, hat(open_hat=open_hat), start, (0.032 if not open_hat else 0.055) * gain, 0.72)
            drum_hits.append((start, 46 if open_hat else 42, 36 if not open_hat else 48, 0.04))
            beat += hat_step
        if section in {"prechorus", "final_chorus"} and bar % 4 == 3:
            for i in range(6):
                start = bar_time(bar, 3.0 + i / 6.0)
                add_stereo(buf, snare(), start, 0.055 * gain, 0.51)
                drum_hits.append((start, 38, 48 + i * 4, 0.04))


def add_room(buf: np.ndarray) -> np.ndarray:
    wet = np.zeros_like(buf)
    taps = (
        (0.042, 0.2, 0.06),
        (0.087, 0.13, -0.04),
        (0.151, 0.1, 0.05),
        (0.229, 0.07, -0.03),
        (0.337, 0.045, 0.02),
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
        "Piano": (0, 0),
        "Bass": (1, 34),
        "Trumpet Lead": (2, 56),
        "Synth Pad": (3, 89),
        "Trumpet Harmony": (4, 56),
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
            start_tick = int((item.start_s / BEAT_S) * ticks_per_beat)
            end_tick = int(((item.start_s + item.duration_s) / BEAT_S) * ticks_per_beat)
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
    drums = mido.MidiTrack()
    mid.tracks.append(drums)
    drums.append(mido.MetaMessage("track_name", name="Pop Drums", time=0))
    drums.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))
    drum_events: list[tuple[int, int, mido.Message]] = []
    for start_s, note, velocity, dur_s in drum_hits:
        start_tick = int((start_s / BEAT_S) * ticks_per_beat)
        end_tick = int(((start_s + dur_s) / BEAT_S) * ticks_per_beat)
        drum_events.append((start_tick, 0, mido.Message("note_on", channel=9, note=note, velocity=velocity, time=0)))
        drum_events.append((end_tick, 1, mido.Message("note_off", channel=9, note=note, velocity=0, time=0)))
    drum_events.sort(key=lambda x: (x[0], x[1]))
    cursor = 0
    for tick, _order, msg in drum_events:
        msg.time = max(0, tick - cursor)
        drums.append(msg)
        cursor = tick
    mid.save(path)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mix = np.zeros((TOTAL_SAMPLES, 2), dtype=np.float32)

    render_harmony(mix)
    render_bass(mix)
    render_drums(mix)
    render_trumpets(mix)

    mix = add_room(mix)
    peak = float(np.max(np.abs(mix)))
    if peak > 0:
        mix *= 0.9 / peak
    mix = np.tanh(mix * 1.12).astype(np.float32)
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
        "style": "original uplifting pop instrumental with trumpet hooks",
        "key": "C major",
        "bpm": BPM,
        "duration_seconds": round(TOTAL_S, 3),
        "form": [
            {"bars": "1-4", "section": "intro"},
            {"bars": "5-16", "section": "verse"},
            {"bars": "17-24", "section": "prechorus"},
            {"bars": "25-40", "section": "chorus"},
            {"bars": "41-48", "section": "bridge"},
            {"bars": "49-56", "section": "final chorus"},
        ],
        "tracks": ["Piano", "Synth Pad", "Bass", "Pop Drums", "Trumpet Lead", "Trumpet Harmony"],
        "files": {
            "wav": str(wav_path.relative_to(ROOT)),
            "midi": str(midi_path.relative_to(ROOT)) if midi_path.exists() else None,
        },
        "midi_note_counts": {
            track: sum(1 for note in midi_notes if note.track == track)
            for track in sorted({note.track for note in midi_notes})
        },
        "drum_hits": len(drum_hits),
    }
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({**metadata, "absolute_wav": str(wav_path), "absolute_midi": str(midi_path)}, indent=2))


if __name__ == "__main__":
    main()
