---
title: fractal-strudel-studio
status: Draft
author: drchinca
created: 2026-06-19
---

# SPEC-fractal-strudel-studio

## 1. Context

Fractal Music and Strudel can become one product, but they should not become one
theory engine.

Fractal Music already owns the Sistema Fractal domain model: tonic, mode,
Gatople role, carta glyph, generated degree/rhythm patterns, realized notes,
timing, frequency, provenance, confidence, MIDI export, and WAV rendering.
The current HTTP contract is `POST /api/generate`, which returns a typed
`WebPayload` for the browser.

Strudel is a browser live-coding and pattern runtime. The official docs expose
three embed paths: iframe, `@strudel/embed`, and direct `@strudel/repl`; they
also expose `@strudel/web` when the host app wants its own UI instead of the
built-in CodeMirror REPL. The Strudel REPL flow is: user code is transpiled and
evaluated into a Pattern, the scheduler queries that Pattern for events, and
the output triggers those events.

Reference docs:

- https://strudel.cc/technical-manual/project-start/
- https://strudel.cc/technical-manual/packages/
- https://strudel.cc/technical-manual/repl/

## 2. Decision

Merge at the app and playback-contract boundary:

```text
Fractal Music Python engine
  -> Pattern
  -> Event tuple
  -> WebPayload
  -> StrudelPayload / generated Strudel code
  -> React Studio
  -> Strudel editor or Strudel browser runtime
```

Do not copy Strudel internals into Fractal Music. Do not reimplement Fractal
Music's scale/mode/wheel/carta logic in TypeScript. The backend remains the
source of truth for musical facts; Strudel becomes the interactive browser
runtime that can play, mutate, and live-code the generated material.

## 3. Current Local Surface

### Backend

- `fractalmusic/generate/types.py`
  - `GenerationRequest`: tonic, mode, event length, flavor.
  - `Pattern`: degree/rhythm/provenance source material.
  - `Event`: realized note, octave, beat, duration, seconds, frequency,
    Gatople role hour, carta glyph.
  - `WebPayload`: browser contract with bpm, key, total beats, confidence,
    events, provenance, and optional audio URL.
- `fractalmusic/generate/adapters.py`
  - `to_midi`
  - `to_web_payload`
  - Missing: `to_strudel_code` or `to_strudel_payload`.
- `chat_bff/src/chat_bff/routes/generate.py`
  - `GET /api/generate/options`
  - `POST /api/generate`
  - Currently renders WAV and returns `WebPayload`.

### Frontend

- `web/src/shell/AppShell.tsx`
  - Separate tabs: Gatople, Componer, Strudel, chat.
- `web/src/strudel/StrudelPanel.tsx`
  - Embeds a `strudel-editor` web component with hardcoded starter code.
  - Missing: generation controls, API loading, provenance display, and
    conversion from `WebPayload` to Strudel code.
- `web/src/composer/ComposerPanel.tsx`
  - Hosts the older static composer through an iframe.

### Host Ports

The unified app should stay on the existing allocation:

- Fractal Music web: `127.0.0.1:5174`
- Fractal Music BFF: `127.0.0.1:8002`
- `5173` remains intentionally unassigned.

Keep `/Users/bado/iccha/PORTS.md` as the host-level registry for new apps.

## 4. Merge Options

### Option A - Strudel iframe

Use `strudel.cc` or `@strudel/embed` inside an iframe.

Pros:

- Fastest to ship.
- Small local bundle.
- Strongest separation from Strudel internals and AGPL coupling.

Cons:

- Least integrated.
- Harder to synchronize transport, state, provenance, and generated patterns.
- Share links depend on Strudel URL/code encoding behavior.

Use this only as a legal/sandbox fallback.

### Option B - Direct `@strudel/repl`

Use the `strudel-editor` web component directly inside the React app.

Pros:

- Already installed and partially wired.
- Gives a real live-coding editor inside Fractal Music.
- External JS can call `editor.setCode`, `editor.start`, `editor.stop`, and
  `editor.evaluate`.

Cons:

- Ships the full REPL bundle, including CodeMirror and output extras.
- Current build emits a direct `eval` warning from Strudel's evaluator.
- Creates a stronger AGPL compliance question for the distributed web app.
- The editor can execute arbitrary Strudel code, so generated code must be
  controlled and user text must not be interpolated unsafely.

This is the best short-term integration path.

### Option C - Custom UI with `@strudel/web`

Use Strudel's browser library without the built-in REPL UI.

Pros:

- Best product integration.
- Fractal Music can own transport controls, visualization, and provenance.
- Smaller and cleaner than embedding the whole REPL once the UI is mature.

Cons:

- More implementation work.
- Requires building custom editing/playback affordances.
- Still requires license compliance because Strudel packages are AGPL.

This is the best target architecture after the first bridge is working.

## 5. Target Product Shape

Replace the separate "Gatople", "Componer", and "Strudel" mental model with a
single Studio route:

- Left: tonic, mode, flavor, length, generate controls.
- Center: Gatople wheel, generated path, timeline, event/provenance readout.
- Right or bottom: Strudel live area.
- Actions: Generate, Load to Strudel, Play WAV, Export MIDI, Ask books about
  this pattern.

The chat panel can remain a secondary tab, but it should accept pattern context
later: key, mode, glyph path, provenance, and current Strudel code.

## 6. Playback Contract

Add one of these backend shapes:

### Minimal additive field

Extend generation output through a new endpoint:

```json
{
  "web_payload": { "...": "existing WebPayload" },
  "strudel_code": "setcps(...)\nstack(...)"
}
```

### Richer future shape

```python
class StrudelPayload(TypedDict):
    schema_version: int
    pattern_name: str
    bpm: int
    total_beats: float
    code: str
    generated_from: WebPayload
    warnings: list[str]
```

Avoid changing the existing `POST /api/generate -> WebPayload` response until
the React caller is migrated. Prefer `POST /api/generate/strudel` or a wrapper
response for the Studio.

## 7. First Adapter Rules

For v1, generate conservative Strudel code from realized events:

- One cycle equals `total_beats`.
- `setcps(bpm / 60 / total_beats)` aligns Strudel cycles with Fractal beats.
- Notes are emitted as lower-case note names plus octave, for example `a5`.
- Metadata appears as comments: key, mode, confidence, provenance, glyph path.
- Do not interpolate arbitrary user free text into executable code.
- If rhythm is all one-beat durations, emit a simple `note("...")` sequence.
- If varied durations appear, preserve them in metadata first; improve rhythmic
  encoding in v2.

Example target code:

```js
// Fractal Music: free:A-Eolico
// key: A Eolico
// confidence: strong 0.9616
// glyphs: ... square + venus ...
// source: El Sistema Fractal
setcps(96 / 60 / 16)

stack(
  note("a5 c5 d4 e4 g3 a5 b5 d4 e5 f4 a3 b4 c3 e4 f4 g4")
    .sound("triangle")
    .gain(.22),
  note("a2")
    .sound("sine")
    .slow(16)
    .gain(.08)
)
```

## 8. Risks

### License

The local app currently has an MIT license, while Strudel packages report
AGPL-3.0-or-later and the official docs state that distributed integrations
must be compatible and publish source. Before distributing this as one bundled
web app, choose one posture:

- Make the web app AGPL-compatible and publish complete source.
- Keep Strudel isolated behind an iframe/embed boundary for demos.
- Get legal confirmation before combining AGPL packages with differently
  licensed proprietary or incompatible code.

### Bundle and build

`@strudel/repl` is heavy because it ships the editor and output extras. The
current Vite build succeeds but warns about direct `eval` in the Strudel bundle
and large chunks. This is acceptable for a local prototype, but not the final
product path.

### Runtime

Browser audio requires a user gesture. The existing `WebPayload` already models
that fact with `requires_user_gesture`, so the Studio should reuse the same
interaction pattern for WAV playback and Strudel playback.

### Source of truth

Do not let the React app generate notes by mode. It may validate shapes and
display events, but musical truth comes from the Python engine.

## 9. Implementation Sequence

1. Add a tested pure adapter in `fractalmusic/generate/adapters.py`:
   `to_strudel_code(pattern, events, score, bpm=DEFAULT_BPM) -> str`.
2. Add unit tests in `tests/unit/test_generate.py` for note formatting, cps,
   metadata comments, and no unsafe free-text interpolation.
3. Add `POST /api/generate/strudel` returning the existing payload plus code,
   leaving `POST /api/generate` stable.
4. Add a typed frontend client mirroring `web/src/chat/api.ts`.
5. Replace the hardcoded `STARTER_CODE` in `StrudelPanel.tsx` with generated
   code loaded from the BFF.
6. Fold Gatople, composer, and Strudel into a single Studio route once the
   bridge works.
7. Later, evaluate replacing direct `@strudel/repl` with `@strudel/web` for a
   custom Fractal Music transport/runtime surface.

## 10. Recommendation

Proceed with Option B now and Option C later:

- Short term: direct `@strudel/repl`, backend-generated Strudel code, fixed
  local ports `5174` and `8002`.
- Medium term: one Studio route that unifies generation, wheel visualization,
  WAV/MIDI export, Strudel live coding, and book chat context.
- Long term: migrate to `@strudel/web` if the app needs a custom professional
  live-performance surface instead of the stock REPL.
