import type { JSX } from "react";

import { displayNote, noteAtRolePosition } from "../geometry";
import type { Role, RotationTable } from "../types";

interface BindingsTableProps {
  readonly roles: readonly Role[];
  readonly rotations: RotationTable;
  readonly enharmonic: Readonly<Record<string, string>>;
  readonly tonicOffset: number;
}

export function BindingsTable({
  roles,
  rotations,
  enharmonic,
  tonicOffset,
}: BindingsTableProps): JSX.Element {
  const sorted = [...roles].sort((a, b) => a.clock_hour - b.clock_hour);
  return (
    <table id="bindings">
      <thead>
        <tr>
          <th>Rol</th>
          <th>Glifo</th>
          <th>Nota</th>
          <th>Hora</th>
        </tr>
      </thead>
      <tbody>
        {sorted.map((role) => {
          const note = noteAtRolePosition(role.position, tonicOffset, rotations);
          const label = role.is_penta ? role.display_glyph : role.mode_name;
          return (
            <tr key={role.position}>
              <td>
                <span
                  className="swatch"
                  style={{ background: role.wheel_color }}
                />
                {label}
              </td>
              <td className="glyph-cell" style={{ color: role.glyph_fg }}>
                {role.display_glyph}
              </td>
              <td>{displayNote(note, enharmonic)}</td>
              <td>{role.clock_hour}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
