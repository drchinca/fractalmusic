# ADR-0001: Bridge Fractal Music's generator into Strudel via direct `@strudel/repl`, not an iframe or a custom `@strudel/web` UI

**Date:** 2026-06-19 (decided) / 2026-09-01 (status updated — implemented)
**Status:** Accepted
**Who:** @drchinca

## The Problem

Fractal Music already owns the Sistema Fractal domain model (tonic, mode, Gátople role, carta glyph, generated degree/rhythm patterns, timing, frequency, provenance, MIDI/WAV export) behind `POST /api/generate`. Strudel is a separate browser live-coding pattern runtime with its own scheduler and its own embed surface. The two needed to become one product surface without becoming one theory engine — reimplementing scale/mode/wheel/carta logic in TypeScript would violate this project's BE-owns-logic cardinal invariant, and copying Strudel internals into this repo would create an unmaintainable fork.

## Our Decision

Merge at the app and playback-contract boundary only. The backend stays the sole source of musical truth; a new adapter turns its `Pattern`/`Event` output into Strudel code; a new endpoint (`POST /api/generate/strudel`) serves that code alongside the existing `WebPayload`; the React app loads it into a directly-embedded `@strudel/repl` web component (`strudel-editor`), not an iframe and not a hand-built player.

```text
Fractal Music Python engine -> Pattern -> Event tuple -> WebPayload
  -> StrudelPayload / generated Strudel code -> React Studio -> Strudel editor
```

## Why This Choice

Of the three options considered (below), direct `@strudel/repl` was the only one that gave a real live-coding editor inside the app without requiring the larger custom-UI investment a `@strudel/web` integration would need. It was already partially wired (`StrudelPanel.tsx` existed with a hardcoded starter), so it was the fastest path to a real bridge — and unlike the iframe option, it lets the app synchronize transport, state, and provenance display with the generated pattern.

## The Cost

- Ships the full REPL bundle (CodeMirror + output extras); the Vite build emits a direct-`eval` warning from Strudel's own evaluator — accepted for a local/prototype deploy, flagged as not the final production bundle shape.
- Strudel packages (`@strudel/repl` et al., confirmed in `web/package.json`) are AGPL-3.0-or-later; this repo is MIT-licensed (`LICENSE`). That license mismatch was never formally resolved — no explicit AGPL-compliance posture was adopted (the original three options were: make the web app AGPL-compatible and publish complete source, keep Strudel behind an iframe/embed boundary, or get legal confirmation). **This is still an open risk**, not closed by shipping Option B.
- The editor can execute arbitrary Strudel code; generated code must stay controlled and user free-text must never be interpolated into it unsafely (enforced in `to_strudel_code`, see Appendix).

## Alternatives We Considered

- **Strudel iframe** (`strudel.cc` or `@strudel/embed`): fastest to ship, smallest bundle, strongest separation from AGPL coupling — but least integrated (no shared transport/state/provenance, share links depend on Strudel's own URL encoding). Rejected as a first bridge; kept as the fallback if the license question above is ever decided against direct embedding.
- **Custom UI on `@strudel/web`** (no built-in REPL UI): best long-term product integration — Fractal Music would own transport, visualization, and provenance display outright, and the bundle would be smaller once mature. Rejected *for now* only because of the added implementation work; still AGPL either way. This is the intended target architecture once the direct-`@strudel/repl` bridge proves the concept (tracked as future work, not this ADR's decision).

---

## Appendix — implementation detail (informational, not part of the decision)

**2026-09-01 audit: this ADR's decision (Option B) has shipped.** Verified directly against the code:

- `fractalmusic/generate/adapters.py::to_strudel_code` / `to_strudel_payload` exist and are tested (`tests/unit/test_generate.py::test_to_strudel_code_*`).
- `POST /api/generate/strudel` is live in `gatople_api/src/gatople_api/routes/generate.py`.
- `web/src/strudel/StrudelPanel.tsx` calls the real endpoint (`generateStrudel`) rather than only rendering the old hardcoded `STARTER_CODE`.
- `web/src/shell/AppShell.tsx` still exposes Gatople / Componer / Strudel / chat as separate tabs — the "single Studio route" consolidation from the original plan has **not** shipped yet.

### Adapter rules (v1, as implemented)

- One cycle equals `total_beats`; `setcps(bpm / 60 / total_beats)` aligns Strudel cycles with Fractal beats.
- Notes are emitted as lower-case note names plus octave (e.g. `a5`).
- Metadata appears as comments: key, mode, confidence, provenance, glyph path.
- User free text is never interpolated into executable code.
- Uniform one-beat rhythms emit a simple `note("...")` sequence; varied durations are preserved in metadata first (richer rhythmic encoding is future work).

### Playback contract (shipped shape)

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

### Known gaps (tracked, not blocking)

- License posture (see Cost, above) — still open.
- Single unified "Studio" route merging Gátople / composer / Strudel / chat — not yet built.
- Migration to `@strudel/web` for a custom transport surface — future work per the Alternatives section.
