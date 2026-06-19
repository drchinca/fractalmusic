import type { JSX } from "react";

import { displayNote, noteAtRolePosition } from "../geometry";
import type { Chromatic, Role } from "../types";

interface BindingsTableProps {
  readonly roles: readonly Role[];
  readonly chromatic: Chromatic;
  readonly tonicOffset: number;
}

export function BindingsTable({
  roles,
  chromatic,
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
          const note = noteAtRolePosition(role.position, tonicOffset, chromatic);
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
              <td>{displayNote(note)}</td>
              <td>{role.clock_hour}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}