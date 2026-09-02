import type { JSX } from "react";

interface WheelSpinToggleProps {
  readonly outerLocked: boolean;
  readonly onChange: (outerLocked: boolean) => void;
}

export function WheelSpinToggle({ outerLocked, onChange }: WheelSpinToggleProps): JSX.Element {
  return (
    <div className="wheel-spin-toggle">
      <span>Giro de la rueda:</span>
      <button
        type="button"
        className={outerLocked ? undefined : "active"}
        onClick={() => onChange(false)}
      >
        Todo junto
      </button>
      <button
        type="button"
        className={outerLocked ? "active" : undefined}
        onClick={() => onChange(true)}
      >
        Anillo fijo
      </button>
    </div>
  );
}
