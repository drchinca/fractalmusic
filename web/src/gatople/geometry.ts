// Pure geometry helpers (coordinate math, no DOM, no React) and pure lookups
// over BE-baked data. No wheel-rotation or enharmonic-spelling arithmetic
// lives here — every one of those is precomputed by
// scripts/build_gatople_data.py and shipped in the JSON payload; this file
// only reads it.

import { SEG_DEG } from "./constants";
import type { Chromatic, Role, RotationTable } from "./types";

export function polar(deg: number, radius: number): readonly [number, number] {
  const rad = (deg - 90) * (Math.PI / 180);
  return [radius * Math.cos(rad), radius * Math.sin(rad)];
}

export function clockAngle(hour: number): number {
  return (hour % 12) * SEG_DEG;
}

// The outer disc is a circle-of-fourths clock (fractalmusic.modes._clock_hour):
// each physical hour-step is a perfect fourth (5 semitones), not a semitone.
// So spinning the note ring to a given tonic offset (or reading a physical
// hour-step back into a tonic offset) both go through the same conversion —
// multiplying by -5 mod 12 is its own inverse (5 * 5 = 25 ≡ 1 mod 12), so one
// function covers both directions.
const HOUR_STEP_SEMITONES = 5;

export function noteRingRotationHours(value: number): number {
  const wrapped = ((value % 12) + 12) % 12;
  return ((-HOUR_STEP_SEMITONES * wrapped) % 12 + 12) % 12;
}

export function noteRingRotationDeg(tonicOffset: number): number {
  return noteRingRotationHours(tonicOffset) * SEG_DEG;
}

export function arcPath(
  startDeg: number,
  endDeg: number,
  rOuter: number,
  rInner: number,
): string {
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

export function indexOfNote(note: string, chromatic: Chromatic): number {
  return chromatic.indexOf(note);
}

export function displayNote(note: string, enharmonic: Readonly<Record<string, string>>): string {
  const flat = enharmonic[note];
  return flat ? `${note}/${flat}` : note;
}

export function noteAtRolePosition(
  rolePosition: number,
  tonicOffset: number,
  rotations: RotationTable,
): string {
  return rotations[tonicOffset][rolePosition];
}

export function roleAtNote(
  note: string,
  roles: readonly Role[],
  tonicOffset: number,
  rotations: RotationTable,
): Role | null {
  const position = rotations[tonicOffset].indexOf(note);
  if (position < 0) return null;
  return roles.find((r) => r.position === position) ?? null;
}
