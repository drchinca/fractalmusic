import { useEffect, type JSX } from "react";

import { BindingsTable } from "./components/BindingsTable";
import { Fretboard } from "./components/Fretboard";
import { PaletteToggle } from "./components/PaletteToggle";
import { Piano } from "./components/Piano";
import { StepControls } from "./components/StepControls";
import { Wheel } from "./components/Wheel";
import { displayNote } from "./geometry";
import { useGatople } from "./hooks/useGatople";
import { usePayload } from "./hooks/usePayload";
import type { Chromatic, Role } from "./types";

export function GatopleApp(): JSX.Element {
  const { payload, error } = usePayload("data.json");

  if (error !== null) {
    return (
      <main>
        <p role="alert">Failed to load Gátople data: {error}</p>
      </main>
    );
  }
  if (payload === null) {
    return (
      <main>
        <p>Loading…</p>
      </main>
    );
  }

  return <GatopleStage chromatic={payload.chromatic} roles={payload.roles} />;
}

interface GatopleStageProps {
  readonly chromatic: Chromatic;
  readonly roles: readonly Role[];
}

function GatopleStage({ chromatic, roles }: GatopleStageProps): JSX.Element {
  const { tonicOffset, palette, setTonic, step, setPalette } =
    useGatople(chromatic);

  useEffect(() => {
    function handleKey(event: KeyboardEvent): void {
      const target = event.target as Element | null;
      if (target?.matches("input, textarea, select")) return;
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        step(-1);
      } else if (event.key === "ArrowRight") {
        event.preventDefault();
        step(1);
      }
    }
    document.addEventListener("keydown", handleKey);
    return () => {
      document.removeEventListener("keydown", handleKey);
    };
  }, [step]);

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
          The outer disc is fixed: each role keeps its glyph, color, and clock
          position. The inner disc rotates — drag it, or click any note to set
          it as the tonic. The whole scale system re-arranges with a single
          rotation.
        </p>
      </header>

      <main>
        <div className="stage">
          <Wheel
            roles={roles}
            chromatic={chromatic}
            tonicOffset={tonicOffset}
            onSetTonic={setTonic}
          />
          <p className="tonic-readout">
            Tonic: <strong>{displayNote(tonicNote)}</strong>{" "}
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
          <h2>Current bindings</h2>
          <BindingsTable
            roles={roles}
            chromatic={chromatic}
            tonicOffset={tonicOffset}
          />
        </aside>
      </main>

      <section className="instruments">
        <PaletteToggle palette={palette} onChange={setPalette} />

        <h2>Piano</h2>
        <p className="caption">
          Each key wears the role currently bound to its physical note. Spin
          the wheel and the keyboard repaints in lockstep.
        </p>
        <Piano
          roles={roles}
          chromatic={chromatic}
          tonicOffset={tonicOffset}
          palette={palette}
        />

        <h2>Guitar fretboard (EADGBE)</h2>
        <p className="caption">
          12 frets across all 6 strings, every position painted with its
          current role. Same data model, same rotation.
        </p>
        <Fretboard
          roles={roles}
          chromatic={chromatic}
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
          Data sourced from <code>fractalmusic.wheel.ROLES</code>. Glyphs and
          colors come from the 12 hand-painted cartas of the{" "}
          <a href="https://github.com/drchinca/fractalmusic">
            Sistema Fractal
          </a>
          .
        </p>
      </footer>
    </>
  );
}