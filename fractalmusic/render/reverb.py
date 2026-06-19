"""Reverb: convolution with an IR file if available, else a Schroeder-style
algorithmic hall built from numpy primitives. Both return a stereo pair
(or mono if input is mono)."""

from pathlib import Path

import numpy as np
from scipy.signal import fftconvolve


def _algorithmic_hall_ir(sr: int, *, length_s: float = 2.2, decay_s: float = 1.6) -> np.ndarray:
    """Synthetic hall impulse response: dense exponential noise + early reflections."""
    n = int(length_s * sr)
    rng = np.random.default_rng(seed=0xFEED)
    noise = rng.standard_normal(n).astype(np.float32)
    decay = np.exp(-np.arange(n) / (decay_s * sr)).astype(np.float32)
    ir = noise * decay

    # Early reflections (a few discrete taps) for spatial cue
    early_taps_ms = (13.0, 27.0, 41.0, 67.0, 95.0)
    early_gains = (0.35, 0.28, 0.22, 0.18, 0.12)
    for ms, g in zip(early_taps_ms, early_gains, strict=True):
        idx = int(ms * sr / 1000.0)
        if idx < n:
            ir[idx] += g

    # Smooth attack so the reverb tail doesn't click
    pre_delay = int(0.012 * sr)
    fade = np.linspace(0.0, 1.0, max(1, int(0.005 * sr)), dtype=np.float32)
    ir[:pre_delay] = 0.0
    fade_end = pre_delay + fade.shape[0]
    if fade_end <= ir.shape[0]:
        ir[pre_delay:fade_end] *= fade
    return ir / (np.max(np.abs(ir)) + 1e-9)


def apply_reverb(
    dry: np.ndarray,
    *,
    sr: int,
    wet_gain: float = 0.30,
    ir_path: Path | None = None,
) -> np.ndarray:
    """Convolve dry signal with an IR. Returns dry + wet at given gain.

    The IR is peak-normalized at load (or at synthesis); the convolution
    output is NOT renormalized. That keeps `wet_gain` as a meaningful
    wet/dry ratio across renders — otherwise loud-vs-quiet IR content
    would silently rescale the wet bus per-render.
    """
    if ir_path is not None and ir_path.exists():
        import soundfile as sf

        ir, ir_sr = sf.read(str(ir_path), dtype="float32")
        if ir.ndim > 1:
            ir = ir.mean(axis=1)
        if ir_sr != sr:
            # Cheap linear resample — IRs are typically OK at this fidelity.
            ratio = sr / ir_sr
            new_len = int(ir.shape[0] * ratio)
            xp = np.linspace(0, ir.shape[0] - 1, new_len)
            ir = np.interp(xp, np.arange(ir.shape[0]), ir).astype(np.float32)
        # Normalize loaded IR once so wet_gain has a stable meaning.
        ir_peak = float(np.max(np.abs(ir))) + 1e-9
        ir = ir / ir_peak
    else:
        ir = _algorithmic_hall_ir(sr=sr)  # already peak-normalized

    # Convolve full-length: keep the reverb tail (length dry + ir - 1).
    # Do NOT renormalize the result — the IR is already at unit peak, so
    # `wet_gain` directly sets the wet contribution relative to dry.
    full_wet = fftconvolve(dry, ir).astype(np.float32)

    out = np.zeros_like(full_wet)
    out[: dry.shape[0]] = dry
    out += full_wet * wet_gain
    return out
