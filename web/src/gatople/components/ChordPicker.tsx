import { type JSX, useEffect, useState } from "react";

import { fetchChordGeometry, fetchChordOptions, TheoryError } from "../theoryApi";
import type { ChordGeometry, ChordOptions } from "../theoryApi";

const ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"] as const;

function maxDegreeFor(mode: string): number {
  return mode.startsWith("Penta") ? 5 : 7;
}

function errorMessage(err: unknown): string {
  if (err instanceof TheoryError) return err.message;
  return err instanceof Error ? err.message : String(err);
}

interface ChordPickerProps {
  readonly tonic: string;
  readonly onChordChange: (chord: ChordGeometry | null) => void;
}

export function ChordPicker({ tonic, onChordChange }: ChordPickerProps): JSX.Element {
  const [options, setOptions] = useState<ChordOptions | null>(null);
  const [mode, setMode] = useState<string>("Eólico");
  const [degree, setDegree] = useState<number>(1);
  const [quality, setQuality] = useState<string>("augmented");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchChordOptions()
      .then((opts) => setOptions(opts))
      .catch((err: unknown) => setError(errorMessage(err)));
  }, []);

  const maxDegree = maxDegreeFor(mode);

  // Re-fetch whenever the wheel's tonic changes, or any picker field
  // changes — the geometry is tonic-derived, so the overlay must follow
  // the wheel rotation the same way every other readout on this tab does.
  useEffect(() => {
    if (options === null) return;
    let cancelled = false;
    fetchChordGeometry({ tonic, mode, degree, quality })
      .then((chord) => {
        if (!cancelled) {
          setError(null);
          onChordChange(chord);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(errorMessage(err));
          onChordChange(null);
        }
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tonic, mode, degree, quality, options]);

  if (options === null) {
    return <p className="chord-picker-meta">Cargando acordes…</p>;
  }

  return (
    <div className="chord-picker">
      <h2>Geometría del acorde</h2>
      <p className="chord-picker-caption">
        Elegí un grado y una calidad — el acorde se dibuja sobre la rueda, en
        la tónica actual.
      </p>
      <div className="chord-picker-fields">
        <label className="chord-picker-field">
          <span>Modo</span>
          <select
            value={mode}
            onChange={(e) => {
              const nextMode = e.target.value;
              setMode(nextMode);
              if (degree > maxDegreeFor(nextMode)) setDegree(1);
            }}
          >
            {options.modes.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </label>
        <label className="chord-picker-field">
          <span>Grado</span>
          <select value={degree} onChange={(e) => setDegree(Number(e.target.value))}>
            {Array.from({ length: maxDegree }, (_, i) => i + 1).map((d) => (
              <option key={d} value={d}>
                {ROMAN[d - 1]}
              </option>
            ))}
          </select>
        </label>
        <label className="chord-picker-field">
          <span>Calidad</span>
          <select value={quality} onChange={(e) => setQuality(e.target.value)}>
            {options.qualities.map((q) => (
              <option key={q} value={q}>
                {q}
              </option>
            ))}
          </select>
        </label>
      </div>
      {error !== null && <p className="chord-picker-error">No pudimos dibujar el acorde: {error}</p>}
    </div>
  );
}
