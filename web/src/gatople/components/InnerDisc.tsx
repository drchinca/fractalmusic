import { NOTE_DISC_R, NOTE_RADIUS } from "../constants";
import { clockAngle, displayNote, polar } from "../geometry";
import type { Role } from "../types";

interface InnerDiscProps {
  readonly roles: readonly Role[];
  readonly rotationDeg: number;
  readonly dragging: boolean;
  readonly onNoteClick: (note: string) => void;
}

export function InnerDisc({
  roles,
  rotationDeg,
  dragging,
  onNoteClick,
}: InnerDiscProps): JSX.Element {
  const className = dragging ? "dragging" : undefined;
  return (
    <g
      id="inner-disc"
      className={className}
      transform={`rotate(${rotationDeg})`}
    >
      {roles.map((role) => {
        const angle = clockAngle(role.clock_hour);
        const [x, y] = polar(angle, NOTE_RADIUS);
        const note = role.note_default;
        // Counter-rotate each note so labels stay upright while the disc spins.
        const transform = `translate(${x} ${y}) rotate(${-rotationDeg})`;
        return (
          <g
            key={role.position}
            className="note-item"
            transform={transform}
            onClick={() => onNoteClick(note)}
          >
            <circle className="note-disc" r={NOTE_DISC_R} />
            <text
              className="note-label"
              textAnchor="middle"
              dominantBaseline="central"
            >
              {displayNote(note)}
            </text>
          </g>
        );
      })}
    </g>
  );
}
