import type { JSX } from "react";

interface StepControlsProps {
  readonly variant: "header" | "footer";
  readonly onStepBack: () => void;
  readonly onReset: () => void;
  readonly onStepForward: () => void;
}

export function StepControls({
  variant,
  onStepBack,
  onReset,
  onStepForward,
}: StepControlsProps): JSX.Element {
  const className =
    variant === "footer"
      ? "step-controls step-controls-footer"
      : "step-controls";
  const backLabel = variant === "footer" ? "◀ atrás" : "◀";
  const fwdLabel = variant === "footer" ? "adelante ▶" : "▶";

  return (
    <div className={className}>
      <button
        type="button"
        aria-label="Bajar un semitono"
        onClick={onStepBack}
      >
        {backLabel}
      </button>
      <button type="button" onClick={onReset}>
        Volver a A
      </button>
      <button
        type="button"
        aria-label="Subir un semitono"
        onClick={onStepForward}
      >
        {fwdLabel}
      </button>
    </div>
  );
}