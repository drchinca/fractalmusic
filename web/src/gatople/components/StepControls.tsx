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
  const backLabel = variant === "footer" ? "◀ back" : "◀";
  const fwdLabel = variant === "footer" ? "forward ▶" : "▶";

  return (
    <div className={className}>
      <button
        type="button"
        aria-label="Step back one semitone"
        onClick={onStepBack}
      >
        {backLabel}
      </button>
      <button type="button" onClick={onReset}>
        Reset to A
      </button>
      <button
        type="button"
        aria-label="Step forward one semitone"
        onClick={onStepForward}
      >
        {fwdLabel}
      </button>
    </div>
  );
}