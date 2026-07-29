# Developer Experience

This repo has two ways to generate music:

1. The core fractal loop generator in `fractalmusic.generate`.
2. Full arranged producer scripts under `scripts/`.

Use the core generator when you need book-shaped, validated fractal event
streams. Use a producer script when you want a complete rendered song with
separate instruments, sections, drums, bass, and MIDI tracks.

## Generate A Fractal Loop

The core generator turns a structured fractal request into:

- a `Pattern` of scale degrees and rhythm,
- realized `Event` objects with note, octave, beat, duration, frequency, role
  hour, and carta glyph,
- JSON for the web app,
- optional MIDI.

Example:

```bash
uv run python -m fractalmusic.generate.cli \
  --tonic A \
  --mode "Eólico" \
  --length 16 \
  --flavor penta-walk \
  --out web/public/generated
```

Outputs:

```text
web/public/generated/A-Eólico-penta-walk.json
web/public/generated/A-Eólico-penta-walk.mid
```

The browser/frontend should treat the JSON as inert playback data. It should
not recompute theory: `time_sec`, `freq_hz`, `role_hour`, `carta_glyph`, and
`key_label` are backend-owned fields.

## Generate Full Songs

The arranged producer scripts create complete original songs as WAV + MIDI +
metadata. They are intentionally outside the current `fractalmusic.generate`
contract because the contract currently models one event stream, while a song
needs sections and separate musical roles.

Render the flamenco-style piece:

```bash
uv run python scripts/produce_flamenco_song.py
```

Render the uplifting pop/trumpet piece:

```bash
uv run python scripts/produce_uplifting_pop_trumpets.py
```

Outputs are written to:

```text
web/public/generated/<slug>.wav
web/public/generated/<slug>.mid
web/public/generated/<slug>.json
```

Open a rendered WAV directly in a browser, for example:

```text
/Users/bado/iccha/fractalmusic/web/public/generated/uplifting-pop-trumpets.wav
```

## How Fractal Patterns Become Music

A fractal music request starts with a tonic, mode, length, and flavor:

```python
from pathlib import Path

from fractalmusic.generate import GenerationRequest, JsonCorpus, StubExpert, research_loop

request = GenerationRequest(
    tonic="A",
    mode="Eólico",
    length_events=16,
    flavor="penta-walk",
)

result = research_loop(
    request=request,
    expert=StubExpert(),
    corpus=JsonCorpus(Path("patterns")),
)
```

The loop:

- loads matching prior patterns from `patterns/`,
- asks the expert for candidates when the corpus is short,
- realizes scale degrees through the `Wheel`,
- scores mode membership, rhythmic coherence, and PHI-like shape,
- persists winners above the threshold.

The realized events are the bridge between theory and sound:

```python
event.note        # "A"
event.octave      # 4
event.beat        # absolute beat offset
event.duration    # beats
event.freq_hz     # precomputed playback frequency
event.role_hour   # Gatople clock role
event.carta_glyph # fractal card glyph
```

## Writing A New Song Producer

For a new style, copy one of the producer scripts and keep this structure:

1. Define musical constants: `BPM`, total bars/cycles, key/mode, output slug.
2. Define the fractal or modal material: scale, chord progression, accent map,
   carta/role logic if needed.
3. Render separate roles into a stereo buffer: lead, harmony, bass, drums,
   percussion, texture.
4. Schedule matching MIDI events while rendering audio.
5. Write `.wav`, `.mid`, and `.json` to `web/public/generated/`.
6. Verify duration, channels, peak level, and MIDI track count.

Minimum verification snippet:

```bash
uv run python - <<'PY'
from pathlib import Path
import numpy as np
import soundfile as sf

wav = Path("web/public/generated/uplifting-pop-trumpets.wav")
audio, sr = sf.read(wav, dtype="float32")
print("sample_rate", sr)
print("shape", audio.shape)
print("duration_s", round(audio.shape[0] / sr, 3))
print("peak", round(float(np.max(np.abs(audio))), 4))
PY
```

Expected for a valid render:

- `sample_rate` is `44100`,
- shape is `(samples, 2)` for stereo,
- duration is nonzero and matches the metadata,
- peak is below or equal to `0.95`.

## Current Limits

The core generator is a loop/cell generator, not yet a full song arranger. It
does not model sections, multi-track orchestration, velocities, articulations,
drums, chord voicings, or arrangement-level tension by itself.

Until that contract grows, use producer scripts for full songs and keep the
core generator as the source of truth for fractal note logic.
