import type { JSX } from "react";

import { FRET_PAD_LEFT, FRET_W, STRING_H } from "../constants";
import { displayNote, roleAtNote } from "../geometry";
import type { FretboardTable, Palette, Role, RotationTable } from "../types";

interface FretboardProps {
  readonly roles: readonly Role[];
  readonly fretboard: FretboardTable;
  readonly rotations: RotationTable;
  readonly enharmonic: Readonly<Record<string, string>>;
  readonly tonicOffset: number;
  readonly palette: Palette;
}

export function Fretboard({
  roles,
  fretboard,
  rotations,
  enharmonic,
  tonicOffset,
  palette,
}: FretboardProps): JSX.Element {
  const rows = fretboard.length;
  const fretCount = fretboard[0].length - 1;
  const totalW = FRET_PAD_LEFT + fretCount * FRET_W;
  const totalH = rows * STRING_H + 22;
  const strings = [...fretboard].reverse();

  return (
    <svg
      id="fretboard"
      viewBox={`0 0 ${totalW} ${totalH}`}
      aria-label="Stickers sobre el diapasón"
    >
      <rect x={0} y={0} width={totalW} height={totalH} fill="#f3e3c0" />

      {Array.from({ length: fretCount + 1 }, (_, f) => {
        const x = FRET_PAD_LEFT + f * FRET_W;
        return (
          <g key={`wire-${f}`}>
            <line
              x1={x}
              x2={x}
              y1={0}
              y2={rows * STRING_H}
              stroke="#1a1a1a"
              strokeWidth={f === 0 ? 3 : 1.5}
            />
            {f > 0 && (
              <text
                x={x - FRET_W / 2}
                y={rows * STRING_H + 16}
                textAnchor="middle"
                fontSize={12}
                fill="#444"
              >
                {f}
              </text>
            )}
          </g>
        );
      })}

      {strings.map((stringNotes, s) => {
        return (
          <g key={`string-${s}`}>
            {stringNotes.map((note, f) => {
              const x = f === 0 ? 0 : FRET_PAD_LEFT + (f - 1) * FRET_W;
              const w = f === 0 ? FRET_PAD_LEFT : FRET_W;
              const y = s * STRING_H;
              const role = roleAtNote(note, roles, tonicOffset, rotations);
              const tintFill =
                role === null
                  ? "#ffffff"
                  : palette === "mono"
                    ? "#ffffff"
                    : role.carta_color;
              const glyphText = role?.display_glyph ?? "";
              return (
                <g
                  key={`cell-${s}-${f}`}
                  className="fret-cell"
                  data-note={note}
                >
                  <rect
                    className="fret-tint"
                    x={x + 4}
                    y={y + 4}
                    width={w - 8}
                    height={STRING_H - 8}
                    rx={3}
                    stroke="#1a1a1a"
                    strokeWidth={1}
                    fill={tintFill}
                  />
                  <text
                    className="fret-glyph"
                    x={x + w / 2}
                    y={y + STRING_H / 2 - 4}
                    textAnchor="middle"
                    dominantBaseline="central"
                    fontSize={14}
                    fontWeight={700}
                  >
                    {glyphText}
                  </text>
                  <text
                    className="fret-label"
                    x={x + w / 2}
                    y={y + STRING_H - 8}
                    textAnchor="middle"
                    fontSize={10}
                    fill="#444"
                  >
                    {displayNote(note, enharmonic)}
                  </text>
                </g>
              );
            })}
          </g>
        );
      })}
    </svg>
  );
}
