// Pure geometry / data helpers — no DOM, no React.

import { ENHARMONIC_FLAT, SEG_DEG } from "./constants";
import type { Chromatic, Role } from "./types";

export function polar(deg: number, radius: number): readonly [number, number] {
  const rad = (deg - 90) * (Math.PI / 180);
  return [radius * Math.cos(rad), radius * Math.sin(rad)];
}

export function clockAngle(hour: number): number {
  return (hour % 12) * SEG_DEG;
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
  const i = chromatic.indexOf(note);
  if (i >= 0) return i;
  for (const sharp of Object.keys(ENHARMONIC_FLAT)) {
    const flat = ENHARMONIC_FLAT[sharp];
    if (flat === note) return chromatic.indexOf(sharp);
  }
  return -1;
}

export function displayNote(note: string): string {
  const flat = ENHARMONIC_FLAT[note];
  return flat ? `${note}/${flat}` : note;
}

export function noteAtRolePosition(
  rolePosition: number,
  tonicOffset: number,
  chromatic: Chromatic,
): string {
  return chromatic[(rolePosition + tonicOffset) % 12];
}

export function roleAtNote(
  note: string,
  roles: readonly Role[],
  tonicOffset: number,
  chromatic: Chromatic,
): Role | null {
  const noteIdx = indexOfNote(note, chromatic);
  if (noteIdx < 0) return null;
  const position = (noteIdx - tonicOffset + 12) % 12;
  return roles.find((r) => r.position === position) ?? null;
}
