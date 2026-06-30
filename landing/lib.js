// El Gátople — shared rendering primitives.
//
// Pure geometry, note arithmetic, and Sistema Fractal role lookup. No DOM
// state, no app-specific layout. Both /docs/gatople/app.js (spinner) and
// /docs/gatople/flow/app.js (kinetic) import from this module.
//
// JSDoc types are TypeScript-compatible — `tsc --checkJs` reads them as the
// boundary contract for any future TS port.

// --- Type contracts (machine-checkable via JSDoc) -----------------------

/**
 * @typedef {"A"|"A#"|"B"|"C"|"C#"|"D"|"D#"|"E"|"F"|"F#"|"G"|"G#"} ChromaticNote
 *   Sharp-spelled chromatic note. Flats are accepted as input via
 *   `indexOfNote` and `displayNote` but never stored.
 */

/**
 * @typedef {readonly ChromaticNote[]} Chromatic
 *   12-element sharp-spelled chromatic ordering, A-rooted (matches data.json).
 */

/**
 * @typedef {Object} RoleEntry
 *   One row of `fractalmusic.wheel.ROLES`, serialized by
 *   scripts/build_gatople_data.py. The renderer treats this as opaque data
 *   — never re-derive musical meaning, only display it.
 * @property {number} position           Chromatic offset from tonic (0..11).
 * @property {ChromaticNote} note_default Note when tonic = A.
 * @property {string} mode_name          e.g. "Eólico", "Dórico".
 * @property {string} glyph              Source glyph from the carta.
 * @property {string} display_glyph      Pre-formatted glyph for SVG <text>.
 * @property {string} display_label      Short human label.
 * @property {string} family             "hepta" | "penta" | etc.
 * @property {string} quality            "major" | "minor" | etc.
 * @property {number} clock_hour         Layout hour 1..12 on the outer disc.
 * @property {readonly number[]} scale_steps Semitone deltas for the scale.
 * @property {string} wheel_color        Outer-segment fill.
 * @property {string} carta_color        Sticker tint for piano/fretboard.
 * @property {string} glyph_fg           Foreground color for the glyph.
 * @property {boolean} is_penta          Whether this is a pentatonic role.
 */

/**
 * @typedef {Object} Payload
 *   Shape of /docs/gatople/data.json.
 * @property {Chromatic} chromatic
 * @property {readonly RoleEntry[]} roles
 */

// --- Shared constants ---------------------------------------------------

export const SVG_NS = "http://www.w3.org/2000/svg";
export const SEG_DEG = 30;
export const RING_OUTER = 240;
export const NOTE_RADIUS = 130;
export const NOTE_DISC_R = 22;

export const GUITAR_TUNING = /** @type {const} */ (["E", "A", "D", "G", "B", "E"]);
export const FRET_COUNT = 12;
export const FRET_W = 60;
export const STRING_H = 36;
export const FRET_PAD_LEFT = 56;

/** Chromatic indices of white piano keys, A-rooted (one octave). */
export const WHITE_INDICES = /** @type {const} */ ([0, 2, 3, 5, 7, 8, 10]);
/** Chromatic indices of black piano keys, A-rooted (one octave). */
export const BLACK_INDICES = /** @type {const} */ ([1, 4, 6, 9, 11]);
/** For each black-key index, the white-key index immediately below it. */
export const BLACK_LOWER = /** @type {Readonly<Record<number, number>>} */ ({
  1: 0, 4: 3, 6: 5, 9: 8, 11: 10,
});

/** Sharp -> flat enharmonic spelling. */
export const ENHARMONIC_FLAT = /** @type {Readonly<Record<string, string>>} */ ({
  "A#": "Bb", "C#": "Db", "D#": "Eb", "F#": "Gb", "G#": "Ab",
});

// --- Geometry -----------------------------------------------------------

/**
 * Convert clock-degree + radius to Cartesian (SVG-y positive-down).
 * 0deg points up (12 o'clock); 90deg points right.
 * @param {number} deg
 * @param {number} radius
 * @returns {[number, number]}
 */
export function polar(deg, radius) {
  const rad = (deg - 90) * (Math.PI / 180);
  return [radius * Math.cos(rad), radius * Math.sin(rad)];
}

/**
 * Convert clock hour (1..12) to clock-degree (0..330).
 * @param {number} hour
 * @returns {number}
 */
export function clockAngle(hour) {
  return (hour % 12) * SEG_DEG;
}

/**
 * Build an SVG path `d` for an annular sector between two clock-degrees.
 * @param {number} startDeg
 * @param {number} endDeg
 * @param {number} rOuter
 * @param {number} rInner
 * @returns {string}
 */
export function arcPath(startDeg, endDeg, rOuter, rInner) {
  const [x1o, y1o] = polar(startDeg, rOuter);
  const [x2o, y2o] = polar(endDeg, rOuter);
  const [x1i, y1i] = polar(startDeg, rInner);
  const [x2i, y2i] = polar(endDeg, rInner);
  const large = endDeg - startDeg > 180 ? 1 : 0;
  return [
    "M", x1i, y1i,
    "L", x1o, y1o,
    "A", rOuter, rOuter, 0, large, 1, x2o, y2o,
    "L", x2i, y2i,
    "A", rInner, rInner, 0, large, 0, x1i, y1i,
    "Z",
  ].join(" ");
}

// --- Note arithmetic ----------------------------------------------------

/**
 * Locate a note in the chromatic ordering, accepting flat spellings.
 * @param {string} note
 * @param {Chromatic} chromatic
 * @returns {number} -1 if unknown
 */
export function indexOfNote(note, chromatic) {
  const i = chromatic.indexOf(/** @type {ChromaticNote} */ (note));
  if (i >= 0) return i;
  for (const [sharp, flat] of Object.entries(ENHARMONIC_FLAT)) {
    if (flat === note) return chromatic.indexOf(/** @type {ChromaticNote} */ (sharp));
  }
  return -1;
}

/**
 * Render a note as either the bare sharp or "sharp/flat" dual spelling.
 * @param {string} note
 * @returns {string}
 */
export function displayNote(note) {
  return ENHARMONIC_FLAT[note] ? `${note}/${ENHARMONIC_FLAT[note]}` : note;
}

/**
 * Resolve which note sits at a given role position for a given tonic.
 * @param {number} rolePosition
 * @param {number} tonicOffset
 * @param {Chromatic} chromatic
 * @returns {ChromaticNote}
 */
export function noteAtRolePosition(rolePosition, tonicOffset, chromatic) {
  return chromatic[(rolePosition + tonicOffset) % 12];
}

/**
 * Resolve the role currently bound to a physical note (for piano/fretboard
 * sticker overlays). Returns `null` when the note is not in the chromatic.
 * @param {string} note
 * @param {readonly RoleEntry[]} roles
 * @param {number} tonicOffset
 * @param {Chromatic} chromatic
 * @returns {RoleEntry | null}
 */
export function roleAtNote(note, roles, tonicOffset, chromatic) {
  const noteIdx = indexOfNote(note, chromatic);
  if (noteIdx < 0) return null;
  const position = ((noteIdx - tonicOffset) % 12 + 12) % 12;
  return roles.find((r) => r.position === position) ?? null;
}
