// Web Audio synth + QWERTY keyboard mapping for the Gátople apps.
//
// Zero dependencies, no samples — uses an OscillatorNode per voice with a
// short ADSR envelope. Latency is negligible; cold-start instantiates the
// AudioContext on first user gesture (per Chrome autoplay policy).
//
// Keyboard convention (the standard C-rooted layout every piano-typing app
// uses — what your fingers expect when they hit the home row):
//
//     w e   t y u                  ← black keys (C# D# F# G# A#)
//    a s d f g h j k               ← white keys (C D E F G A B C)
//
//    z / x  → octave down / up
//    Shift + key → set that note as tonic (move ⋮ Eólico to it)
//
// Note: the keyboard is C-rooted *as an input device* because that's the
// universal piano-typing convention. The Gátople wheel itself stays A-origin
// (matriarchal Eólico). The two are separate concerns — pressing 'a' plays
// middle-C; Shift+'a' sets C as the tonic, which spins the wheel.

const A4_FREQ = 440.0;
const A4_INDEX_FROM_A = 0; // chromatic index 0 = A
const SEMITONES_PER_OCTAVE = 12;

// Chromatic A-order (must match the Python CHROMATIC_ORDER + data.json).
const CHROMATIC = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"];

// QWERTY → note. Uses the C-rooted Synthtopia layout (universal piano-
// typing convention). The home row plays C D E F G A B C; the row above
// plays the black keys C# D# F# G# A#.
export const KEY_TO_NOTE = Object.freeze({
  a: "C",
  w: "C#",
  s: "D",
  e: "D#",
  d: "E",
  f: "F",
  t: "F#",
  g: "G",
  y: "G#",
  h: "A",
  u: "A#",
  j: "B",
  k: "C_OCT",  // top of the played range — C one octave up
});

/**
 * Convert (note, octave) into a frequency in Hz, A4 = 440 Hz reference.
 * Octaves change at C (scientific pitch notation) — the same convention
 * pytheory and the `to_pytheory()` bridge use, so audio matches MIDI export.
 *
 * @param {string} note — chromatic-A name, e.g. "A", "C#"
 * @param {number} octave — scientific octave number (A4 = octave 4)
 * @returns {number}
 */
export function frequencyFor(note, octave) {
  // Sci pitch class: C=0, …, A=9, …, B=11. Distance from A4 in semitones.
  const sciIndex = { C: 0, "C#": 1, D: 2, "D#": 3, E: 4, F: 5, "F#": 6,
                     G: 7, "G#": 8, A: 9, "A#": 10, B: 11 };
  const idx = sciIndex[note];
  if (idx === undefined) throw new Error(`unknown note: ${note}`);
  const semitonesFromA4 = (octave - 4) * SEMITONES_PER_OCTAVE + (idx - 9);
  return A4_FREQ * Math.pow(2, semitonesFromA4 / SEMITONES_PER_OCTAVE);
}

/**
 * Lazily create / resume the AudioContext. Browsers require a user gesture
 * before the context can produce sound, so this MUST be called from within
 * an event handler (keydown, click).
 */
function ensureContext(state) {
  if (!state.ctx) {
    state.ctx = new (window.AudioContext || window.webkitAudioContext)();
  } else if (state.ctx.state === "suspended") {
    state.ctx.resume();
  }
  return state.ctx;
}

/**
 * Play one note. Returns the OscillatorNode so the caller can stop it on
 * keyup if they want sustained-press behavior; for a quick blip just ignore.
 *
 * @param {{ctx: AudioContext|null, octave: number}} state
 * @param {string} note
 * @param {{durationMs?: number, gain?: number}} [opts]
 */
export function playNote(state, note, opts = {}) {
  const ctx = ensureContext(state);
  const { durationMs = 380, gain = 0.18 } = opts;

  const osc = ctx.createOscillator();
  const env = ctx.createGain();
  osc.type = "triangle";  // soft, harmonics-light — easier on the ears than 'sine' for piano-style play
  osc.frequency.value = frequencyFor(note, state.octave);
  osc.connect(env);
  env.connect(ctx.destination);

  // Short ADSR envelope so the note doesn't click on/off.
  const now = ctx.currentTime;
  const attackS = 0.012;
  const releaseS = 0.18;
  env.gain.setValueAtTime(0.0001, now);
  env.gain.exponentialRampToValueAtTime(gain, now + attackS);
  env.gain.exponentialRampToValueAtTime(0.0001, now + durationMs / 1000 + releaseS);

  osc.start(now);
  osc.stop(now + durationMs / 1000 + releaseS + 0.05);
  return osc;
}

/**
 * Build a shared audio engine. One AudioContext for the whole page.
 * All UI surfaces (keyboard, click-to-play, Cero Pitágoras button, geometry
 * arpeggiator) borrow the same engine so they don't fight over playback.
 *
 * @returns {{
 *   playNote: (note: string, octave?: number, opts?: object) => OscillatorNode,
 *   playSequence: (notes: Array<[string, number]>, opts?: object) => void,
 *   getOctave: () => number,
 *   setOctave: (octave: number) => void,
 * }}
 */
export function createAudioEngine() {
  const state = { ctx: null, octave: 4 };

  /** @param {string} note @param {number} [octave] */
  function trigger(note, octave, opts = {}) {
    return playNote({ ctx: state.ctx, octave: octave ?? state.octave }, note, opts);
  }

  /**
   * Arpeggiate a list of [note, octave] pairs at fixed spacing.
   * @param {Array<[string, number]>} notes
   * @param {{stepMs?: number, durationMs?: number, gain?: number}} [opts]
   */
  function playSequence(notes, opts = {}) {
    const stepMs = opts.stepMs ?? 220;
    const durationMs = opts.durationMs ?? 380;
    const gain = opts.gain ?? 0.18;
    notes.forEach(([note, octave], i) => {
      window.setTimeout(() => {
        trigger(note, octave, { durationMs, gain });
      }, i * stepMs);
    });
  }

  return {
    playNote: trigger,
    playSequence,
    getOctave: () => state.octave,
    setOctave: (oct) => { state.octave = Math.max(1, Math.min(7, oct)); },
  };
}

/**
 * Wire keyboard listeners. Returns a cleanup function.
 *
 * Behavior:
 *   - lower-case letter → play that note in the current octave
 *   - 'k' → A in (current octave + 1)
 *   - 'z' / 'x' → octave down / up (clamped 1..7)
 *   - Shift+letter → set that note as tonic via ``onSetTonic(note)``
 *
 * @param {{onSetTonic: (note: string) => void, engine?: ReturnType<typeof createAudioEngine>}} hooks
 * @returns {() => void}
 */
export function bindKeyboard(hooks) {
  const engine = hooks.engine ?? createAudioEngine();
  const state = { ctx: null, octave: engine.getOctave() };
  const held = new Set();

  function handler(event) {
    if (event.target.matches("input, textarea, select")) return;
    const key = event.key;

    // Octave shift — keys 'z' / 'x' (no shift).
    if (!event.shiftKey && (key === "z" || key === "Z")) {
      event.preventDefault();
      state.octave = Math.max(1, state.octave - 1);
      engine.setOctave(state.octave);
      announceOctave(state.octave);
      return;
    }
    if (!event.shiftKey && (key === "x" || key === "X")) {
      event.preventDefault();
      state.octave = Math.min(7, state.octave + 1);
      engine.setOctave(state.octave);
      announceOctave(state.octave);
      return;
    }

    const lower = key.toLowerCase();
    const noteOrSentinel = KEY_TO_NOTE[lower];
    if (!noteOrSentinel) return;

    event.preventDefault();
    const note = noteOrSentinel === "C_OCT" ? "C" : noteOrSentinel;
    const octave = noteOrSentinel === "C_OCT" ? state.octave + 1 : state.octave;

    if (event.shiftKey) {
      hooks.onSetTonic(note);
      return;
    }

    // Auto-repeat from holding a key would re-trigger; debounce on first hit.
    if (held.has(lower)) return;
    held.add(lower);
    engine.playNote(note, octave);
  }

  function release(event) {
    held.delete(event.key.toLowerCase());
  }

  function announceOctave(octave) {
    const el = document.getElementById("octave-readout");
    if (el) el.textContent = `Octave ${octave}`;
  }
  announceOctave(state.octave);

  document.addEventListener("keydown", handler);
  document.addEventListener("keyup", release);
  return () => {
    document.removeEventListener("keydown", handler);
    document.removeEventListener("keyup", release);
  };
}
