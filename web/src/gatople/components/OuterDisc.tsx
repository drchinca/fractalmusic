import type { JSX } from "react";

import { RING_INNER, RING_MID, RING_OUTER, SEG_DEG } from "../constants";
import { arcPath, clockAngle, polar } from "../geometry";
import type { Role } from "../types";

interface OuterDiscProps {
  readonly roles: readonly Role[];
  // The rotation this disc's own parent <g> is currently applying (0 when the
  // outer ring is locked). Each glyph counter-rotates by the same amount —
  // exactly how InnerDisc keeps its note labels upright — so spinning the
  // ring never turns a "+" into an "×" or a "↓" into a checkmark.
  readonly rotationDeg: number;
}

export function OuterDisc({ roles, rotationDeg }: OuterDiscProps): JSX.Element {
  return (
    <g id="outer-disc">
      {roles.map((role) => {
        const angle = clockAngle(role.clock_hour);
        const start = angle - SEG_DEG / 2;
        const end = angle + SEG_DEG / 2;
        const [gx, gy] = polar(angle, RING_MID);
        const tooltip =
          `${role.carta_name} · ${role.mode_name} · ${role.quality} · ${role.clock_hour} o'clock`;

        return (
          <g key={role.position}>
            <path
              d={arcPath(start, end, RING_OUTER, RING_INNER)}
              fill={role.wheel_color}
              className="role-segment"
            >
              <title>{tooltip}</title>
            </path>
            <g transform={`translate(${gx} ${gy}) rotate(${-rotationDeg})`}>
              <text className="role-glyph" fill={role.glyph_fg}>
                {role.display_glyph}
              </text>
            </g>
          </g>
        );
      })}
    </g>
  );
}
