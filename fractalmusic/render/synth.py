"""Pure-numpy polyphonic synth. One Event → one note rendered into a buffer."""

from dataclasses import dataclass
from typing import Final

import numpy as np


# Per-timbre voice spec.
@dataclass(frozen=True, slots=True)
class VoicePreset:
    name: str
    partials: tuple[tuple[float, float], ...]  # (harmonic_ratio, gain) pairs
    detune_cents: float
    attack_s: float
    decay_s: float
    sustain_level: float
    release_s: float
    lp_start_hz: float
    lp_end_hz: float


PIANO: Final[VoicePreset] = VoicePreset(
    name="piano",
    partials=((1.0, 1.0), (2.0, 0.45), (3.0, 0.22), (4.0, 0.12), (6.0, 0.05)),
    detune_cents=0.0,
    attack_s=0.005,
    decay_s=0.5,
    sustain_level=0.35,
    release_s=0.4,
    lp_start_hz=5000.0,
    lp_end_hz=900.0,
)
STRINGS: Final[VoicePreset] = VoicePreset(
    name="strings",
    partials=((1.0, 0.7), (1.0, 0.5), (2.0, 0.25), (3.0, 0.12)),  # second 1.0 = detuned unison
    detune_cents=8.0,
    attack_s=0.18,
    decay_s=0.4,
    sustain_level=0.85,
    release_s=0.6,
    lp_start_hz=3500.0,
    lp_end_hz=1500.0,
)
PAD: Final[VoicePreset] = VoicePreset(
    name="pad",
    partials=((1.0, 0.6), (1.0, 0.5), (2.0, 0.3), (3.0, 0.18), (5.0, 0.08)),
    detune_cents=12.0,
    attack_s=0.25,
    decay_s=0.6,
    sustain_level=0.9,
    release_s=1.2,
    lp_start_hz=2200.0,
    lp_end_hz=1200.0,
)


def _adsr(n_samples: int, sr: int, preset: VoicePreset) -> np.ndarray:
    """Continuous piecewise-linear ADSR over n_samples + a release tail.

    Built via np.interp over breakpoint times, so segment boundaries are
    sample-accurate and free of stair-step discontinuities (no zipper buzz
    on short notes). AD compress proportionally if the requested note is
    shorter than attack+decay.
    """
    a = max(1, int(preset.attack_s * sr))
    d = max(1, int(preset.decay_s * sr))
    r = max(1, int(preset.release_s * sr))
    s_level = preset.sustain_level

    if a + d > n_samples:
        ratio = n_samples / (a + d)
        a = max(1, int(a * ratio))
        d = max(1, n_samples - a)

    note_off = a + d + max(0, n_samples - a - d)  # = n_samples
    total = note_off + r

    # Breakpoints in sample index → amplitude. np.interp connects them
    # linearly, with each segment ending exactly where the next begins.
    breakpoints_idx = np.array([0, a, a + d, note_off, total], dtype=np.float32)
    breakpoints_val = np.array([0.0, 1.0, s_level, s_level, 0.0], dtype=np.float32)
    samples = np.arange(total, dtype=np.float32)
    return np.interp(samples, breakpoints_idx, breakpoints_val).astype(np.float32)


def _one_pole_lowpass(buf: np.ndarray, cutoff_curve_hz: np.ndarray, sr: int) -> np.ndarray:
    """Time-varying one-pole lowpass. cutoff_curve_hz length must match buf."""
    out = np.empty_like(buf)
    y = 0.0
    two_pi_over_sr = 2.0 * np.pi / sr
    for i, x in enumerate(buf):
        # alpha = dt / (RC + dt), RC = 1/(2*pi*fc)
        rc = 1.0 / (two_pi_over_sr * max(cutoff_curve_hz[i], 60.0))
        alpha = (1.0 / sr) / (rc + (1.0 / sr))
        y = y + alpha * (x - y)
        out[i] = y
    return out


def synth_note(
    *,
    freq_hz: float,
    duration_s: float,
    sr: int,
    preset: VoicePreset,
    velocity: float = 0.8,
) -> np.ndarray:
    """Render a single note at freq_hz for duration_s seconds, return float32 mono buffer.

    Output length includes the release tail past duration_s, so the caller
    overlap-adds when scheduling.
    """
    n_main = max(1, int(duration_s * sr))
    env = _adsr(n_main, sr, preset)
    total = env.shape[0]
    t = np.arange(total, dtype=np.float32) / sr

    # Build the harmonic stack: each partial = sin(2π · h · f0 · t)
    osc_buf = np.zeros(total, dtype=np.float32)
    detune_factor = 2.0 ** (preset.detune_cents / 1200.0)
    for idx, (harmonic, gain) in enumerate(preset.partials):
        # Apply detune to every other partial (gives unison shimmer for strings/pad)
        f = freq_hz * harmonic * (detune_factor if idx % 2 == 1 else 1.0)
        osc_buf += gain * np.sin(2.0 * np.pi * f * t).astype(np.float32)
    # Normalize partial sum so peak ~ 1.0
    partial_sum = sum(g for _, g in preset.partials)
    if partial_sum > 0:
        osc_buf /= partial_sum

    voiced = osc_buf * env

    # Time-varying lowpass: bright at attack, mellow as it sustains.
    cutoff = np.linspace(preset.lp_start_hz, preset.lp_end_hz, total).astype(np.float32)
    voiced = _one_pole_lowpass(voiced, cutoff, sr)

    return voiced * velocity
