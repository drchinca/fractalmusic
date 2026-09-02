"""Unit tests — reverb convolution, real IR loading, and the algorithmic hall.

apply_reverb's ir_path branch (load, resample, downmix, normalize a real IR
file) had zero direct coverage — only exercised incidentally through the
smoke test, which never passes an ir_path. Unlike soundfont.py, `soundfile`
is a genuine installed project dependency, so this gets a real WAV file,
not a mock.
"""

import numpy as np
import soundfile as sf
from fractalmusic.render.reverb import _algorithmic_hall_ir, apply_reverb


def test_algorithmic_hall_ir_is_peak_normalized():
    ir = _algorithmic_hall_ir(sr=8000)
    assert np.isclose(np.max(np.abs(ir)), 1.0, atol=1e-5)


def test_algorithmic_hall_ir_is_deterministic():
    # Fixed seed (0xFEED) — same sample rate must reproduce byte-identical IR.
    assert np.array_equal(_algorithmic_hall_ir(sr=8000), _algorithmic_hall_ir(sr=8000))


def test_algorithmic_hall_ir_handles_a_length_shorter_than_its_own_taps_and_fade():
    # length_s=0.01 @ sr=1000 -> n=10 samples, shorter than the 95ms early-
    # reflection tap and the fade-in window — must skip both gracefully
    # rather than raise or write out of bounds.
    ir = _algorithmic_hall_ir(sr=1000, length_s=0.01, decay_s=0.01)
    assert len(ir) == 10
    assert np.all(np.isfinite(ir))


def test_apply_reverb_without_ir_path_uses_algorithmic_hall():
    dry = np.zeros(4000, dtype=np.float32)
    dry[0] = 1.0
    out = apply_reverb(dry, sr=8000, wet_gain=0.3, ir_path=None)
    assert out.ndim == 1
    assert out.dtype == np.float32
    # dry sample is preserved at the front (dry + wet, not just wet).
    assert out[0] >= 1.0


def test_apply_reverb_loads_resamples_downmixes_and_normalizes_a_real_ir(tmp_path):
    # A tiny stereo IR at a different sample rate than the render, so this
    # exercises resample (8000 -> 16000) and stereo-to-mono downmix together.
    ir_sr = 8000
    ir_stereo = np.zeros((100, 2), dtype=np.float32)
    ir_stereo[0] = (1.0, 0.5)  # mono-downmixed peak = 0.75, then re-normalized to 1.0
    ir_path = tmp_path / "ir.wav"
    sf.write(str(ir_path), ir_stereo, ir_sr)

    dry = np.zeros(1000, dtype=np.float32)
    dry[0] = 1.0
    out = apply_reverb(dry, sr=16000, wet_gain=0.5, ir_path=ir_path)

    assert out.ndim == 1
    # resampled IR length = int(100 * 16000/8000) = 200; full convolution
    # length = len(dry) + len(ir) - 1.
    assert out.shape[0] == 1000 + 200 - 1
    # out[0] = dry[0] + (dry[0] * normalized_ir[0]) * wet_gain = 1.0 + 1.0*0.5.
    assert np.isclose(out[0], 1.5)
    # the reverb tail extends past the dry signal's own length.
    assert np.any(out[dry.shape[0] :] != 0)


def test_apply_reverb_downmixes_stereo_by_averaging_channels(tmp_path):
    # Two taps that split unevenly across channels (1,0) then (0,1) — mean-
    # downmix and "just take one channel" produce different, distinguishable
    # results here, unlike a single-nonzero-sample IR where re-normalization
    # can hide the difference (both end up peak=1.0 at the same index).
    ir_stereo = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]], dtype=np.float32)
    ir_path = tmp_path / "ir_stereo.wav"
    sf.write(str(ir_path), ir_stereo, 8000)

    dry = np.zeros(5, dtype=np.float32)
    dry[0] = 1.0
    out = apply_reverb(dry, sr=8000, wet_gain=1.0, ir_path=ir_path)

    # mean([1,0])=0.5, mean([0,1])=0.5 -> both peak-normalize to 1.0.
    assert np.isclose(out[0], 2.0)
    assert np.isclose(out[1], 1.0)


def test_apply_reverb_with_mono_ir_at_matching_sample_rate_skips_downmix_and_resample(tmp_path):
    ir_mono = np.zeros(50, dtype=np.float32)
    ir_mono[0] = 2.0  # deliberately off-peak-1 to prove normalization still runs
    ir_path = tmp_path / "ir_mono.wav"
    sf.write(str(ir_path), ir_mono, 8000)

    dry = np.zeros(200, dtype=np.float32)
    dry[0] = 1.0
    out = apply_reverb(dry, sr=8000, wet_gain=1.0, ir_path=ir_path)

    assert out.ndim == 1
    # no resample: convolution length = len(dry) + len(ir) - 1, unchanged.
    assert out.shape[0] == 200 + 50 - 1
    # normalized ir[0] = 2.0 / 2.0 = 1.0, so out[0] = dry[0] + dry[0]*1.0*wet_gain.
    assert np.isclose(out[0], 2.0)
