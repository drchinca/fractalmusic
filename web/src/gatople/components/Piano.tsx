import type { JSX } from "react";

import {
  BLACK_INDICES,
  BLACK_LOWER,
  PIANO_H,
  PIANO_W,
  WHITE_INDICES,
} from "../constants";
import { displayNote, roleAtNote } from "../geometry";
import type { Chromatic, Palette, Role } from "../types";

interface PianoProps {
  readonly roles: readonly Role[];
  readonly chromatic: Chromatic;
  readonly tonicOffset: number;
  readonly palette: Palette;
}

interface KeyVisual {
  readonly note: string;
  readonly tintFill: string;
  readonly glyphText: string;
  readonly noteText: string;
}

function keyVisual(
  note: string,
  roles: readonly Role[],
  tonicOffset: number,
  chromatic: Chromatic,
  palette: Palette,
): KeyVisual {
  const role = roleAtNote(note, roles, tonicOffset, chromatic);
  if (!role) {
    return { note, tintFill: "#ffffff", glyphText: "", noteText: displayNote(note) };
  }
  const tintFill = palette === "mono" ? "#ffffff" : role.carta_color;
  return {
    note,
    tintFill,
    glyphText: role.display_glyph,
    noteText: displayNote(note),
  };
}

export function Piano({
  roles,
  chromatic,
  tonicOffset,
  palette,
}: PianoProps): JSX.Element {
  const whiteW = PIANO_W / WHITE_INDICES.length;
  const blackW = whiteW * 0.62;
  const blackH = PIANO_H * 0.6;
  const whiteCol: Record<number, number> = {};
  WHITE_INDICES.forEach((idx, col) => {
    whiteCol[idx] = col;
  });

  return (
    <svg
      id="piano"
      viewBox={`0 0 ${PIANO_W} ${PIANO_H}`}
      aria-label="Stickers sobre el piano"
    >
      {WHITE_INDICES.map((idx) => {
        const x = whiteCol[idx] * whiteW;
        const note = chromatic[idx];
        const v = keyVisual(note, roles, tonicOffset, chromatic, palette);
        return (
          <g key={`white-${idx}`} className="piano-key piano-white" data-note={note}>
            <rect
              x={x}
              y={0}
              width={whiteW}
              height={PIANO_H}
              fill="#fff"
              stroke="#1a1a1a"
              strokeWidth={1.5}
            />
            <rect
              className="piano-tint"
              x={x + 4}
              y={PIANO_H - 70}
              width={whiteW - 8}
              height={60}
              rx={3}
              stroke="#1a1a1a"
              strokeWidth={1}
              fill={v.tintFill}
            />
            <text
              className="piano-glyph"
              x={x + whiteW / 2}
              y={PIANO_H - 50}
              textAnchor="middle"
              dominantBaseline="central"
              fontSize={20}
              fontWeight={700}
            >
              {v.glyphText}
            </text>
            <text
              className="piano-note"
              x={x + whiteW / 2}
              y={PIANO_H - 22}
              textAnchor="middle"
              fontSize={13}
            >
              {v.noteText}
            </text>
          </g>
        );
      })}
      {BLACK_INDICES.map((idx) => {
        const x = whiteCol[BLACK_LOWER[idx]] * whiteW + whiteW - blackW / 2;
        const note = chromatic[idx];
        const v = keyVisual(note, roles, tonicOffset, chromatic, palette);
        return (
          <g key={`black-${idx}`} className="piano-key piano-black" data-note={note}>
            <rect x={x} y={0} width={blackW} height={blackH} fill="#0a0a0a" />
            <rect
              className="piano-tint"
              x={x + 3}
              y={blackH - 50}
              width={blackW - 6}
              height={42}
              rx={3}
              stroke="#fff"
              strokeWidth={1}
              fill={v.tintFill}
            />
            <text
              className="piano-glyph"
              x={x + blackW / 2}
              y={blackH - 32}
              textAnchor="middle"
              dominantBaseline="central"
              fontSize={16}
              fontWeight={700}
              fill="#fff"
            >
              {v.glyphText}
            </text>
            <text
              className="piano-note"
              x={x + blackW / 2}
              y={blackH - 13}
              textAnchor="middle"
              fontSize={11}
              fill="#fff"
            >
              {v.noteText}
            </text>
          </g>
        );
      })}
    </svg>
  );
}