"""Unit tests — the pure-numpy polyphonic synth.

Real presets (PIANO/STRINGS/PAD) are already exercised end-to-end by the
smoke test. This closes the one gap that isn't: synth_note's guard against
a degenerate preset whose partial gains sum to zero (would otherwise divide
by zero when normalizing the harmonic stack).
"""

import numpy as np
from fractalmusic.render.synth import PIANO, VoicePreset, synth_note


def test_synth_note_produces_finite_audio_for_a_real_preset():
    buf = synth_note(freq_hz=440.0, duration_s=0.2, sr=8000, preset=PIANO)
    assert buf.ndim == 1
    assert buf.dtype == np.float32
    assert np.all(np.isfinite(buf))


def test_synth_note_handles_a_zero_gain_preset_without_dividing_by_zero():
    silent_preset = VoicePreset(
        name="silent",
        partials=((1.0, 0.0),),
        detune_cents=0.0,
        attack_s=0.01,
        decay_s=0.1,
        sustain_level=0.5,
        release_s=0.1,
        lp_start_hz=5000.0,
        lp_end_hz=1000.0,
    )
    buf = synth_note(freq_hz=440.0, duration_s=0.1, sr=8000, preset=silent_preset)
    assert np.all(np.isfinite(buf))
    assert np.all(buf == 0.0)
