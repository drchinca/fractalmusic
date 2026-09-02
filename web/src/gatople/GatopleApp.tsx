import { type JSX, useState } from "react";

import payloadJson from "../../public/data.json";
import { BindingsTable } from "./components/BindingsTable";
import { ChordOverlay } from "./components/ChordOverlay";
import { ChordPicker } from "./components/ChordPicker";
import { Fretboard } from "./components/Fretboard";
import { PaletteToggle } from "./components/PaletteToggle";
import { Piano } from "./components/Piano";
import { StepControls } from "./components/StepControls";
import { Wheel } from "./components/Wheel";
import { displayNote } from "./geometry";
import { useGatople } from "./hooks/useGatople";
import type { ChordGeometry } from "./theoryApi";
import type { Chromatic, FretboardTable, Payload, Role, RotationTable } from "./types";

// Static import of the canonical Python-derived snapshot. Vite types the JSON
// at compile time and bundles it (~6 KB → ~1 KB gzip) so there's no loading
// state and no fetch round-trip. The Python drift test still guards the source.
// Cast through `unknown` because Vite's JSON import infers literal arrays
// (string[]), but the Payload type is precise (12-tuple, mode-name unions, etc.).
// The Python build_gatople_data.py + drift test guarantee the actual shape.
const payload = payloadJson as unknown as Payload;

export function GatopleApp(): JSX.Element {
  return (
    <GatopleStage
      chromatic={payload.chromatic}
      roles={payload.roles}
      rotations={payload.rotations}
      enharmonic={payload.enharmonic}
      fretboard={payload.fretboard}
    />
  );
}

interface GatopleStageProps {
  readonly chromatic: Chromatic;
  readonly roles: readonly Role[];
  readonly rotations: RotationTable;
  readonly enharmonic: Readonly<Record<string, string>>;
  readonly fretboard: FretboardTable;
}

function GatopleStage({
  chromatic,
  roles,
  rotations,
  enharmonic,
  fretboard,
}: GatopleStageProps): JSX.Element {
  const { tonicOffset, palette, setTonic, step, setPalette } =
    useGatople(chromatic);
  const [chord, setChord] = useState<ChordGeometry | null>(null);

  const tonicNote = chromatic[tonicOffset];
  const eolicoRole = roles.find((r) => r.position === 0);
  const eolicoModeName = eolicoRole?.mode_name ?? "";

  function reset(): void {
    setTonic("A");
  }

  return (
    <>
      <header>
        <h1>El Gátople</h1>
        <p className="subtitle">
          El disco exterior es fijo: cada rol conserva su glifo, color y
          posición horaria. El disco interior rota — arrastralo, o tocá
          cualquier nota para fijarla como tónica. Todo el sistema de escalas
          se reordena con una sola rotación.
        </p>
      </header>

      <main>
        <div className="stage">
          <Wheel
            roles={roles}
            chromatic={chromatic}
            enharmonic={enharmonic}
            tonicOffset={tonicOffset}
            onSetTonic={setTonic}
            onStep={step}
          >
            {chord !== null && (
              <ChordOverlay
                notes={chord.notes}
                symbol={chord.symbol}
                isRegular={chord.polygon.is_regular}
                roles={roles}
                tonicOffset={tonicOffset}
                rotations={rotations}
              />
            )}
          </Wheel>
          <p className="tonic-readout">
            Tónica: <strong>{displayNote(tonicNote, enharmonic)}</strong>{" "}
            <span className="tonic-mode">({eolicoModeName})</span>
          </p>
          <StepControls
            variant="header"
            onStepBack={() => step(-1)}
            onReset={reset}
            onStepForward={() => step(1)}
          />
        </div>

        <aside className="readout">
          <ChordPicker tonic={tonicNote} onChordChange={setChord} />
          {chord !== null && (
            <div className="chord-readout" aria-live="polite">
              <p className="chord-symbol">
                {chord.symbol}
                <span className="chord-glyphs">
                  {chord.glyphs.map((g, i) => (
                    <span key={i}>{g}</span>
                  ))}
                </span>
              </p>
              <p className="chord-notes">{chord.notes.join(" · ")}</p>
              <p className="chord-tension">
                Tensión (consonancia por lado):{" "}
                {chord.edge_consonance.map((c) => c.toFixed(2)).join(" · ")}
              </p>
            </div>
          )}
          <h2>Asignaciones actuales</h2>
          <BindingsTable
            roles={roles}
            rotations={rotations}
            enharmonic={enharmonic}
            tonicOffset={tonicOffset}
          />
        </aside>
      </main>

      <section className="instruments">
        <PaletteToggle palette={palette} onChange={setPalette} />

        <h2>Piano</h2>
        <p className="caption">
          Cada tecla lleva el rol actualmente vinculado a su nota física. Hacé
          girar la rueda y el teclado se repinta al instante.
        </p>
        <Piano
          roles={roles}
          chromatic={chromatic}
          rotations={rotations}
          enharmonic={enharmonic}
          tonicOffset={tonicOffset}
          palette={palette}
        />

        <h2>Diapasón de guitarra (EADGBE)</h2>
        <p className="caption">
          12 trastes en las 6 cuerdas, cada posición pintada con su rol
          actual. Mismo modelo, misma rotación.
        </p>
        <Fretboard
          roles={roles}
          fretboard={fretboard}
          rotations={rotations}
          enharmonic={enharmonic}
          tonicOffset={tonicOffset}
          palette={palette}
        />

        <StepControls
          variant="footer"
          onStepBack={() => step(-1)}
          onReset={reset}
          onStepForward={() => step(1)}
        />
      </section>

      <footer>
        <p>
          Datos tomados de <code>fractalmusic.wheel.ROLES</code>. Los glifos y
          colores vienen de las 12 cartas pintadas a mano del{" "}
          <a href="https://github.com/drchinca/fractalmusic">
            Sistema Fractal
          </a>
          .
        </p>
      </footer>
    </>
  );
}
