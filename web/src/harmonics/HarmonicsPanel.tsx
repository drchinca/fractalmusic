import type { JSX } from "react";

import type { Role } from "../gatople/types";

// Categorical palette, first three slots (validated all-pairs, both CVD and
// normal-vision floors clear) — one hue per icosahedron axis.
const AXIS_COLORS: Readonly<Record<"x" | "y" | "z", string>> = {
  x: "#2a78d6",
  y: "#eb6834",
  z: "#1baf7a",
};

const CHART_WIDTH = 640;
const CHART_HEIGHT = 320;
const MARGIN = { top: 20, right: 20, bottom: 40, left: 40 };
const PLOT_WIDTH = CHART_WIDTH - MARGIN.left - MARGIN.right;
const PLOT_HEIGHT = CHART_HEIGHT - MARGIN.top - MARGIN.bottom;

function xForSlot(slot: number): number {
  return MARGIN.left + (slot / 11) * PLOT_WIDTH;
}

function yForValue(value: number, range: number): number {
  // range covers [-range, range]; value=0 sits at the vertical midline.
  return MARGIN.top + PLOT_HEIGHT / 2 - (value / range) * (PLOT_HEIGHT / 2);
}

interface OrderedRole {
  readonly role: Role;
  readonly slot: number; // 0..11, distance in semitones from the current tonic
}

function orderByDistanceFromTonic(roles: readonly Role[], tonicNote: string): readonly OrderedRole[] {
  const tonicRole = roles.find((r) => r.note_default === tonicNote);
  const tonicPosition = tonicRole?.position ?? 0;
  return roles
    .map((role) => ({ role, slot: (role.position - tonicPosition + 12) % 12 }))
    .sort((a, b) => a.slot - b.slot);
}

function polylinePoints(ordered: readonly OrderedRole[], axis: 0 | 1 | 2, range: number): string {
  return ordered.map(({ role, slot }) => `${xForSlot(slot)},${yForValue(role.coordinates_3d[axis], range)}`).join(" ");
}

interface GridLine {
  readonly value: number;
  readonly label: string;
}

interface HarmonicsPanelProps {
  readonly roles: readonly Role[];
  readonly phi: number;
  readonly tonicNote: string;
  readonly displayTonicNote: string;
}

export function HarmonicsPanel({ roles, phi, tonicNote, displayTonicNote }: HarmonicsPanelProps): JSX.Element {
  const ordered = orderByDistanceFromTonic(roles, tonicNote);
  const range = phi * 1.12;

  const gridLines: readonly GridLine[] = [
    { value: phi, label: "φ" },
    { value: 1, label: "1" },
    { value: 0, label: "0" },
    { value: -1, label: "-1" },
    { value: -phi, label: "-φ" },
  ];

  return (
    <section className="harmonics-panel" aria-label="Armónicos de la proporción áurea">
      <header className="harmonics-header">
        <h2>Armónicos φ</h2>
        <p className="harmonics-sub">
          Cada una de las 12 notas es un vértice de un icosaedro construido con la
          proporción áurea (φ = {phi.toFixed(6)}…). El gráfico arranca en la
          tónica actual — <strong>{displayTonicNote}</strong> — y ordena el resto
          por distancia en semitonos: girá la rueda y las 12 columnas se
          reacomodan. Los valores de cada nota nunca cambian; lo que cambia es
          desde dónde empezás a leerlos.
        </p>
      </header>

      <div className="harmonics-chart-wrap">
        <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} className="harmonics-chart" role="img" aria-label="Ondas de las coordenadas X, Y, Z de las 12 notas, ordenadas desde la tónica">
          <rect
            x={MARGIN.left}
            y={MARGIN.top}
            width={PLOT_WIDTH / 11 / 2}
            height={PLOT_HEIGHT}
            className="harmonics-tonic-band"
          />

          {gridLines.map((line) => (
            <g key={line.label}>
              <line
                x1={MARGIN.left}
                x2={CHART_WIDTH - MARGIN.right}
                y1={yForValue(line.value, range)}
                y2={yForValue(line.value, range)}
                className="harmonics-gridline"
              />
              <text x={MARGIN.left - 8} y={yForValue(line.value, range)} className="harmonics-gridlabel" textAnchor="end" dominantBaseline="central">
                {line.label}
              </text>
            </g>
          ))}

          {(["x", "y", "z"] as const).map((axis, axisIndex) => (
            <polyline
              key={axis}
              points={polylinePoints(ordered, axisIndex as 0 | 1 | 2, range)}
              className="harmonics-line"
              stroke={AXIS_COLORS[axis]}
              fill="none"
            />
          ))}

          {(["x", "y", "z"] as const).map((axis, axisIndex) =>
            ordered.map(({ role, slot }) => {
              const cx = xForSlot(slot);
              const cy = yForValue(role.coordinates_3d[axisIndex], range);
              return (
                <circle
                  key={`${axis}-${role.position}`}
                  cx={cx}
                  cy={cy}
                  r={slot === 0 ? 6 : 4}
                  className="harmonics-point"
                  fill={AXIS_COLORS[axis]}
                >
                  <title>
                    {role.note_default} · eje {axis.toUpperCase()} = {role.coordinates_3d[axisIndex].toFixed(4)}
                  </title>
                </circle>
              );
            }),
          )}

          {ordered.map(({ role, slot }) => (
            <text
              key={role.position}
              x={xForSlot(slot)}
              y={CHART_HEIGHT - MARGIN.bottom + 18}
              className={`harmonics-notelabel ${slot === 0 ? "is-tonic" : ""}`}
              textAnchor="middle"
            >
              {role.note_default}
            </text>
          ))}
        </svg>

        <div className="harmonics-legend">
          {(["x", "y", "z"] as const).map((axis) => (
            <span key={axis} className="harmonics-legend-item">
              <span className="harmonics-legend-swatch" style={{ background: AXIS_COLORS[axis] }} />
              Eje {axis.toUpperCase()}
            </span>
          ))}
        </div>
      </div>

      <footer className="harmonics-footnote">
        <p>
          φ es un número irracional — su expansión decimal no termina ni se
          repite. La misma proporción aparece como el límite de los cocientes de
          Fibonacci (1, 2, 3, 5, 8, 13, 21, …): F(n+1)/F(n) se acerca cada vez más
          a φ a medida que n crece, sin llegar nunca — la versión "infinita" de
          esta geometría.
        </p>
      </footer>
    </section>
  );
}
