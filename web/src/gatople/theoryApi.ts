// Thin client over GET /api/theory/*. BE owns all chord/geometry math —
// this only validates response shape at the boundary, never derives it.

const OPTIONS_ENDPOINT = "/api/theory/chord-options";
const CHORD_ENDPOINT = "/api/theory/chord";

export class TheoryError extends Error {
  readonly status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

export interface ChordOptions {
  readonly modes: readonly string[];
  readonly qualities: readonly string[];
}

export interface Polygon2D {
  readonly vertices: readonly (readonly [number, number])[];
  readonly centroid: readonly [number, number];
  readonly perimeter: number;
  readonly is_regular: boolean;
}

export interface ChordGeometry {
  readonly tonic: string;
  readonly mode: string;
  readonly degree: number;
  readonly quality: string;
  readonly root: string;
  readonly symbol: string;
  readonly notes: readonly string[];
  readonly glyphs: readonly string[];
  readonly polygon: Polygon2D;
  readonly coordinates_3d: readonly (readonly [number, number, number])[];
  readonly edge_consonance: readonly number[];
}

function isChordOptions(x: unknown): x is ChordOptions {
  if (typeof x !== "object" || x === null) return false;
  const p = x as Record<string, unknown>;
  return (
    Array.isArray(p.modes) &&
    p.modes.every((m) => typeof m === "string") &&
    Array.isArray(p.qualities) &&
    p.qualities.every((q) => typeof q === "string")
  );
}

function isChordGeometry(x: unknown): x is ChordGeometry {
  if (typeof x !== "object" || x === null) return false;
  const p = x as Record<string, unknown>;
  return (
    typeof p.symbol === "string" &&
    typeof p.root === "string" &&
    Array.isArray(p.notes) &&
    Array.isArray(p.glyphs) &&
    typeof p.polygon === "object" &&
    p.polygon !== null &&
    Array.isArray((p.polygon as Record<string, unknown>).vertices) &&
    Array.isArray(p.edge_consonance)
  );
}

export async function fetchChordOptions(): Promise<ChordOptions> {
  let response: Response;
  try {
    response = await fetch(OPTIONS_ENDPOINT);
  } catch (err) {
    throw new TheoryError(`Network error: ${errorMessage(err)}`, 0);
  }
  if (!response.ok) {
    throw new TheoryError("could not load chord options", response.status);
  }
  const json: unknown = await response.json();
  if (!isChordOptions(json)) {
    throw new TheoryError("BFF returned an unexpected chord-options shape", 500);
  }
  return json;
}

export async function fetchChordGeometry(params: {
  tonic: string;
  mode: string;
  degree: number;
  quality: string;
}): Promise<ChordGeometry> {
  const query = new URLSearchParams({
    tonic: params.tonic,
    mode: params.mode,
    degree: String(params.degree),
    quality: params.quality,
  });
  let response: Response;
  try {
    response = await fetch(`${CHORD_ENDPOINT}?${query.toString()}`);
  } catch (err) {
    throw new TheoryError(`Network error: ${errorMessage(err)}`, 0);
  }
  if (!response.ok) {
    let detail = "request failed";
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // ignore
    }
    throw new TheoryError(detail, response.status);
  }
  const json: unknown = await response.json();
  if (!isChordGeometry(json)) {
    throw new TheoryError("BFF returned an unexpected chord shape", 500);
  }
  return json;
}
