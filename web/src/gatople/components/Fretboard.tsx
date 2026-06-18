import {
  FRET_COUNT,
  FRET_PAD_LEFT,
  FRET_W,
  GUITAR_TUNING,
  STRING_H,
} from "../constants";
import { displayNote, roleAtNote } from "../geometry";
import type { Chromatic, Palette, Role } from "../types";

interface FretboardProps {
  readonly roles: readonly Role[];
  readonly chromatic: Chromatic;
  readonly tonicOffset: number;
  readonly palette: Palette;
}

export function Fretboard({
  roles,
  chromatic,
  tonicOffset,
  palette,
}: FretboardProps): JSX.Element {
  const rows = GUITAR_TUNING.length;
  const totalW = FRET_PAD_LEFT + FRET_COUNT * FRET_W;
  const totalH = rows * STRING_H + 22;
  const strings = [...GUITAR_TUNING].reverse();

  return (
    <svg
      id="fretboard"
      viewBox={`0 0 ${totalW} ${totalH}`}
      aria-label="Guitar fretboard sticker overlay"
    >
      <rect x={0} y={0} width={totalW} height={totalH} fill="#f3e3c0" />

      {Array.from({ length: FRET_COUNT + 1 }, (_, f) => {
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

      {strings.map((stringNote, s) => {
        const baseIdx = chromatic.indexOf(stringNote);
        return (
          <g key={`string-${s}`}>
            {Array.from({ length: FRET_COUNT + 1 }, (_, f) => {
              const chromIdx = (baseIdx + f) % 12;
              const note = chromatic[chromIdx];
              const x = f === 0 ? 0 : FRET_PAD_LEFT + (f - 1) * FRET_W;
              const w = f === 0 ? FRET_PAD_LEFT : FRET_W;
              const y = s * STRING_H;
              const role = roleAtNote(note, roles, tonicOffset, chromatic);
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
                    {displayNote(note)}
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
