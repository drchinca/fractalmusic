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
      <span>Sticker palette:</span>
      <button
        type="button"
        className={palette === "carta" ? "active" : undefined}
        onClick={() => onChange("carta")}
      >
        Carta colors
      </button>
      <button
        type="button"
        className={palette === "mono" ? "active" : undefined}
        onClick={() => onChange("mono")}
      >
        Black &amp; white
      </button>
    </div>
  );
}
