"""Top-level render pipeline: Events → polyphonic synth → drone → reverb → WAV."""

from dataclasses import dataclass
from pathlib import Path
from typing import Final

import numpy as np
import soundfile as sf

from fractalmusic.generate.types import Event
from fractalmusic.render.reverb import apply_reverb
from fractalmusic.render.soundfont import render_with_soundfont, soundfont_available
from fractalmusic.render.synth import PAD, PIANO, STRINGS, VoicePreset, synth_note

DEFAULT_SAMPLE_RATE: Final[int] = 44100


@dataclass(frozen=True, slots=True)
class RenderConfig:
    sample_rate: int = DEFAULT_SAMPLE_RATE
    bpm: int = 96
    melody_voice: VoicePreset = PIANO
    pad_voice: VoicePreset = PAD
    drone_voice: VoicePreset = STRINGS
    drone_gain: float = 0.18
    pad_gain: float = 0.22
    melody_gain: float = 0.85
    reverb_wet: float = 0.32
    sf2_path: Path | None = None
    sf2_program: int = 0  # GM Acoustic Grand
    ir_path: Path | None = None


def render_wav(
    events: tuple[Event, ...],
    *,
    out_path: Path,
    config: RenderConfig | None = None,
    tonic_freq_hz: float | None = None,
    tonic_midi_octave: int = 3,
) -> Path:
    """Render Events into a 44.1k mono WAV at out_path. Returns out_path.

    The drone is rooted on `tonic_freq_hz` if given (the request's tonic
    frequency, the only source-of-truth). Without it, the drone falls back
    to the *earliest* event by beat — not by list order — to avoid a wrong
    drone when events arrive unsorted.
    """
    cfg = config or RenderConfig()
    if not events:
        raise ValueError("render_wav requires at least one Event")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    sec_per_beat = 60.0 / cfg.bpm
    total_seconds = (
        max(e.beat + e.duration for e in events) * sec_per_beat + 2.5  # tail
    )
    total_samples = int(total_seconds * cfg.sample_rate)
    mix = np.zeros(total_samples, dtype=np.float32)

    # 1. Melody — soundfont if possible, numpy otherwise.
    if cfg.sf2_path is not None and soundfont_available(cfg.sf2_path):
        melody_buf = render_with_soundfont(
            events=events,
            sr=cfg.sample_rate,
            sf2_path=cfg.sf2_path,
            program=cfg.sf2_program,
            bpm=cfg.bpm,
        )
        # Pad/truncate to total length
        if melody_buf.shape[0] < mix.shape[0]:
            mix[: melody_buf.shape[0]] += melody_buf * cfg.melody_gain
        else:
            mix += melody_buf[: mix.shape[0]] * cfg.melody_gain
    else:
        for e in events:
            duration_s = e.duration * sec_per_beat
            note_buf = synth_note(
                freq_hz=e.freq_hz,
                duration_s=duration_s,
                sr=cfg.sample_rate,
                preset=cfg.melody_voice,
                velocity=0.85,
            )
            on_sample = int(e.beat * sec_per_beat * cfg.sample_rate)
            end = min(on_sample + note_buf.shape[0], mix.shape[0])
            mix[on_sample:end] += note_buf[: end - on_sample] * cfg.melody_gain

    # 2. Pad layer — same notes, soft pad voice, half velocity (always numpy).
    for e in events:
        duration_s = e.duration * sec_per_beat
        pad_buf = synth_note(
            freq_hz=e.freq_hz * 0.5,  # one octave below for warmth
            duration_s=duration_s,
            sr=cfg.sample_rate,
            preset=cfg.pad_voice,
            velocity=0.5,
        )
        on_sample = int(e.beat * sec_per_beat * cfg.sample_rate)
        end = min(on_sample + pad_buf.shape[0], mix.shape[0])
        mix[on_sample:end] += pad_buf[: end - on_sample] * cfg.pad_gain

    # 3. Drone — sustained tonic across the full piece.
    # Tonic must come from the request (the only source of truth). Guessing
    # from `events[0]` lands on the wrong pitch class whenever the first
    # event isn't the tonic.
    if tonic_freq_hz is None:
        raise ValueError(
            "render_wav requires tonic_freq_hz — derive it from the request "
            "tonic via fractalmusic.generate.realize.freq_for(...)"
        )
    tonic_freq = tonic_freq_hz
    _ = tonic_midi_octave  # kept for callers that want to compute it themselves
    drone_buf = synth_note(
        freq_hz=tonic_freq,
        duration_s=total_seconds - 0.5,
        sr=cfg.sample_rate,
        preset=cfg.drone_voice,
        velocity=0.65,
    )
    end = min(drone_buf.shape[0], mix.shape[0])
    mix[:end] += drone_buf[:end] * cfg.drone_gain

    # 4. Reverb
    mix = apply_reverb(mix, sr=cfg.sample_rate, wet_gain=cfg.reverb_wet, ir_path=cfg.ir_path)

    # 5. Gain stage:
    #    a) pre-attenuate so the typical mix peak lands near 0.9 — keeps
    #       low-level content out of the tanh curve where it would compress.
    #    b) tanh as a soft-clip safety net for genuine over-1.0 peaks only.
    #    c) normalize the post-clip peak to 0.95 to leave a touch of headroom.
    raw_peak = float(np.max(np.abs(mix)))
    if raw_peak > 0:
        mix = mix * (0.9 / raw_peak)
    mix = np.tanh(mix).astype(np.float32)
    final_peak = float(np.max(np.abs(mix)))
    if final_peak > 0:
        mix = (mix / final_peak) * 0.95

    sf.write(str(out_path), mix, cfg.sample_rate, subtype="PCM_16")
    return out_path
