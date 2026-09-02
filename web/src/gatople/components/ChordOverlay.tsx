import type { JSX } from "react";

import { clockAngle, polar, roleAtNote } from "../geometry";
import type { Role, RotationTable } from "../types";

const OVERLAY_RADIUS = 130; // matches NOTE_RADIUS — sits exactly on the note markers

interface ChordOverlayProps {
  readonly notes: readonly string[];
  readonly symbol: string;
  readonly isRegular: boolean;
  readonly roles: readonly Role[];
  readonly tonicOffset: number;
  readonly rotations: RotationTable;
}

export function ChordOverlay({
  notes,
  symbol,
  isRegular,
  roles,
  tonicOffset,
  rotations,
}: ChordOverlayProps): JSX.Element | null {
  const points: (readonly [number, number])[] = [];
  for (const note of notes) {
    const role = roleAtNote(note, roles, tonicOffset, rotations);
    if (role === null) return null; // BE and FE payload disagree — render nothing, not a wrong shape
    points.push(polar(clockAngle(role.clock_hour), OVERLAY_RADIUS));
  }
  if (points.length < 3) return null;

  const pointsAttr = points.map(([x, y]) => `${x},${y}`).join(" ");

  return (
    <g className="chord-overlay" aria-label={`Geometría del acorde ${symbol}`}>
      <polygon
        points={pointsAttr}
        className={`chord-overlay-shape ${isRegular ? "is-regular" : ""}`}
      />
      {points.map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r={6} className="chord-overlay-vertex" />
      ))}
    </g>
  );
}
