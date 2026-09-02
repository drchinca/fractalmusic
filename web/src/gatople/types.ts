// Gátople data model — mirrors fractalmusic.wheel.ROLES (Python source of truth).

export type Chromatic = readonly [
  string, string, string, string, string, string,
  string, string, string, string, string, string,
];

export type RoleFamily = "hepta" | "penta";
export type RoleQuality = "major" | "minor" | "diminished";

export interface Role {
  readonly position: number;
  readonly note_default: string;
  readonly mode_name: string;
  readonly glyph: string;
  readonly display_glyph: string;
  readonly display_label: string;
  readonly family: RoleFamily;
  readonly quality: RoleQuality;
  readonly clock_hour: number;
  readonly scale_steps: readonly number[];
  readonly wheel_color: string;
  readonly carta_color: string;
  readonly carta_image: string;
  readonly coordinates_3d: readonly [number, number, number];
  readonly glyph_fg: string;
  readonly carta_name: string;
  readonly is_penta: boolean;
  readonly roman: string | null;
}

export interface PentaRoot {
  readonly roman: string;
  readonly note: string;
}

// rotations[tonicOffset][rolePosition] -> note. All 12 possible spins,
// pre-baked so the FE never recomputes "(position + tonicOffset) % 12".
export type RotationTable = readonly Chromatic[];

// fretboard[stringIndex][fret] -> note, frets 0..FRET_COUNT. Tonic-
// independent (a guitar's open tuning doesn't spin with the wheel).
export type FretboardTable = readonly (readonly string[])[];

export interface Payload {
  readonly chromatic: Chromatic;
  readonly roles: readonly Role[];
  readonly penta_roots: readonly PentaRoot[];
  readonly rotations: RotationTable;
  readonly enharmonic: Readonly<Record<string, string>>;
  readonly fretboard: FretboardTable;
  readonly phi: number;
}

export type Palette = "carta" | "mono";
