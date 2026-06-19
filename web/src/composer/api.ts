// Thin client over POST /api/generate. Validates response shape at boundary.

import { isFlavor } from "./types";
import type { ComposerOptions, GeneratedEvent, GeneratedPayload, GenerateRequest } from "./types";

const ENDPOINT = "/api/generate";
const OPTIONS_ENDPOINT = "/api/generate/options";

export class GenerateError extends Error {
  readonly status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

function isEvent(x: unknown): x is GeneratedEvent {
  if (typeof x !== "object" || x === null) return false;
  const e = x as Record<string, unknown>;
  return (
    typeof e.note === "string" &&
    typeof e.octave === "number" &&
    typeof e.beat === "number" &&
    typeof e.duration === "number" &&
    typeof e.time_sec === "number" &&
    typeof e.freq_hz === "number" &&
    typeof e.role_hour === "number" &&
    typeof e.carta_glyph === "string"
  );
}

export function isGeneratedPayload(x: unknown): x is GeneratedPayload {
  if (typeof x !== "object" || x === null) return false;
  const p = x as Record<string, unknown>;
  return (
    typeof p.schema_version === "number" &&
    typeof p.pattern_name === "string" &&
    typeof p.bpm === "number" &&
    typeof p.tonic === "string" &&
    typeof p.mode === "string" &&
    typeof p.key_label === "string" &&
    typeof p.total_beats === "number" &&
    typeof p.requires_user_gesture === "boolean" &&
    typeof p.confidence === "object" &&
    p.confidence !== null &&
    Array.isArray(p.events) &&
    p.events.every(isEvent) &&
    typeof p.provenance === "object" &&
    p.provenance !== null &&
    (p.audio_url === null || typeof p.audio_url === "string")
  );
}

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

export async function generateMusic(req: GenerateRequest): Promise<GeneratedPayload> {
  let response: Response;
  try {
    response = await fetch(ENDPOINT, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(req),
    });
  } catch (err) {
    throw new GenerateError(`Network error: ${errorMessage(err)}`, 0);
  }
  if (!response.ok) {
    let detail = "request failed";
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // ignore
    }
    throw new GenerateError(detail, response.status);
  }
  const json: unknown = await response.json();
  if (!isGeneratedPayload(json)) {
    throw new GenerateError("BFF returned an unexpected shape", 500);
  }
  return json;
}

export async function fetchOptions(): Promise<ComposerOptions> {
  let response: Response;
  try {
    response = await fetch(OPTIONS_ENDPOINT);
  } catch (err) {
    throw new GenerateError(`Network error: ${errorMessage(err)}`, 0);
  }
  if (!response.ok) {
    throw new GenerateError("could not load options", response.status);
  }
  const json = (await response.json()) as {
    tonics?: unknown;
    modes?: unknown;
    flavors?: unknown;
  };
  const tonics = Array.isArray(json.tonics) ? json.tonics.filter((x): x is string => typeof x === "string") : [];
  const modes = Array.isArray(json.modes) ? json.modes.filter((x): x is string => typeof x === "string") : [];
  const flavors = Array.isArray(json.flavors)
    ? json.flavors.filter((x): x is string => typeof x === "string").filter(isFlavor)
    : [];
  if (tonics.length === 0 || modes.length === 0 || flavors.length === 0) {
    throw new GenerateError("BFF returned an unexpected options shape", 500);
  }
  return { tonics, modes, flavors };
}
