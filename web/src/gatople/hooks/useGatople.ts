import { useCallback, useState } from "react";

import { indexOfNote } from "../geometry";
import type { Chromatic, Palette } from "../types";

export interface GatopleState {
  readonly tonicOffset: number;
  readonly palette: Palette;
  readonly setTonic: (note: string) => void;
  readonly step: (delta: number) => void;
  readonly setPalette: (palette: Palette) => void;
}

export function useGatople(chromatic: Chromatic): GatopleState {
  const [tonicOffset, setTonicOffset] = useState<number>(0);
  const [palette, setPaletteState] = useState<Palette>("carta");

  const setTonic = useCallback(
    (note: string): void => {
      const idx = indexOfNote(note, chromatic);
      if (idx < 0) return;
      setTonicOffset(idx);
    },
    [chromatic],
  );

  const step = useCallback(
    (delta: number): void => {
      setTonicOffset((prev) => ((prev + delta) % 12 + 12) % 12);
    },
    [],
  );

  const setPalette = useCallback((next: Palette): void => {
    setPaletteState(next);
  }, []);

  return { tonicOffset, palette, setTonic, step, setPalette };
}
