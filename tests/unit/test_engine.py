"""Unit tests — render_wav's fail-fast guards and the gain-stage math.

The full pipeline (synth -> reverb -> WAV) is already exercised end-to-end
by the smoke test. This covers what that test doesn't: the two ValueError
contracts, and the tanh soft-clip / normalize logic, which needs a mix that
genuinely exceeds 1.0 peak — not naturally reachable through the smoke
test's real render, so it's tested directly against the extracted function.
"""

import numpy as np
import pytest
from fractalmusic.generate.types import Event
from fractalmusic.render.engine import _stage_gain, render_wav


def _event() -> Event:
    return Event(
        note="A",
        octave=4,
        beat=0.0,
        duration=1.0,
        time_sec=0.0,
        freq_hz=440.0,
        role_hour=9,
        carta_glyph="⋮",
    )


def test_render_wav_rejects_empty_events(tmp_path):
    with pytest.raises(ValueError, match="at least one Event"):
        render_wav((), out_path=tmp_path / "out.wav", tonic_freq_hz=440.0)


def test_render_wav_requires_tonic_freq_hz(tmp_path):
    with pytest.raises(ValueError, match="tonic_freq_hz"):
        render_wav((_event(),), out_path=tmp_path / "out.wav", tonic_freq_hz=None)


def test_stage_gain_soft_clips_peaks_over_one():
    loud = np.array([1.5, -1.5, 0.5], dtype=np.float32)
    out = _stage_gain(loud)
    assert np.isclose(np.max(np.abs(out)), 0.95)
    # tanh compresses large values relatively more than small ones, so the
    # ratio between samples shifts (0.5106) — plain linear normalization
    # would preserve the original 0.5/1.5 = 0.3333 ratio exactly. A weaker
    # assertion (e.g. "out[2] < 0.5") can't tell the two apart, since
    # normalization alone already shrinks everything.
    assert np.isclose(abs(out[2] / out[0]), 0.5105, atol=1e-3)


def test_stage_gain_normalizes_quiet_mixes_without_clipping():
    quiet = np.array([0.2, -0.1], dtype=np.float32)
    out = _stage_gain(quiet)
    assert np.isclose(np.max(np.abs(out)), 0.95)
    # ratio between samples is preserved by plain normalization (no tanh).
    assert np.isclose(out[1] / out[0], -0.5)


def test_stage_gain_leaves_silence_silent():
    silent = np.zeros(5, dtype=np.float32)
    out = _stage_gain(silent)
    assert np.array_equal(out, silent)
