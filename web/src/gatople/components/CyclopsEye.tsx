import type { JSX } from "react";

export function CyclopsEye(): JSX.Element {
  return (
    <g id="cyclops-eye">
      <circle r={36} fill="#fff" stroke="#000" strokeWidth={3} />
      <ellipse cx={0} cy={0} rx={14} ry={32} fill="#0a3d2e" />
      <ellipse cx={0} cy={-6} rx={4} ry={6} fill="#fff" opacity={0.5} />
    </g>
  );
}