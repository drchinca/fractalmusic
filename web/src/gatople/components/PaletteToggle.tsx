import type { JSX } from "react";

import type { Palette } from "../types";

interface PaletteToggleProps {
  readonly palette: Palette;
  readonly onChange: (palette: Palette) => void;
}

export function PaletteToggle({
  palette,
  onChange,
}: PaletteToggleProps): JSX.Element {
  return (
    <div className="palette-toggle">
      <span>Paleta de stickers:</span>
      <button
        type="button"
        className={palette === "carta" ? "active" : undefined}
        onClick={() => onChange("carta")}
      >
        Colores de carta
      </button>
      <button
        type="button"
        className={palette === "mono" ? "active" : undefined}
        onClick={() => onChange("mono")}
      >
        Blanco y negro
      </button>
    </div>
  );
}