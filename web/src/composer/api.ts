// Thin client over POST /api/generate. Validates response shape at boundary.

import { isFlavor } from "./types";
import type { ComposerOptions, GeneratedPayload, GenerateRequest } from "./types";

const ENDPOINT = "/api/generate";
const OPTIONS_ENDPOINT = "/api/generate/options";

export class GenerateError extends Error {
  readonly status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
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
  const json = await response.json();
  return json as GeneratedPayload;
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
