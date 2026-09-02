// Geometry and layout constants. Mirrors docs/gatople/app.js.

export const RING_OUTER = 240;
export const RING_INNER = 165;
export const RING_MID = (RING_OUTER + RING_INNER) / 2;
export const NOTE_RADIUS = 130;
export const NOTE_DISC_R = 22;
export const SEG_DEG = 30;

export const PIANO_W = 560;
export const PIANO_H = 180;
export const WHITE_INDICES: readonly number[] = [0, 2, 3, 5, 7, 8, 10];
export const BLACK_INDICES: readonly number[] = [1, 4, 6, 9, 11];
export const BLACK_LOWER: Readonly<Record<number, number>> = {
  1: 0,
  4: 3,
  6: 5,
  9: 8,
  11: 10,
};

export const FRET_W = 60;
export const STRING_H = 36;
export const FRET_PAD_LEFT = 56;
