"""Offline WAV rendering for fractalmusic Events.

Pipeline: Events → polyphonic synth → mix → reverb → normalize → WAV.

Three render backends, layered:

* numpy synth (always available) — multi-osc + ADSR + lowpass per voice;
* FluidSynth + SoundFont (optional) — only if pyfluidsynth + an .sf2 are present;
* convolution reverb (optional) — uses an IR file if found, else algorithmic.

Public API:

    render_wav(events, *, out_path, ...) -> Path
"""

from fractalmusic.render.engine import (
    DEFAULT_SAMPLE_RATE,
    RenderConfig,
    render_wav,
)

__all__ = [
    "DEFAULT_SAMPLE_RATE",
    "RenderConfig",
    "render_wav",
]
