import { GenerateError, isGeneratedPayload } from "../composer/api";
import type { GeneratedPayload, GenerateRequest } from "../composer/types";

const ENDPOINT = "/api/generate/strudel";

export interface StrudelGeneration {
  schema_version: number;
  pattern_name: string;
  bpm: number;
  total_beats: number;
  code: string;
  generated_from: GeneratedPayload;
  book_guidance: StrudelBookGuidance[];
  warnings: string[];
}

export interface StrudelBookGuidance {
  book_hash: string;
  book_title: string;
  chapter_idx: number;
  section_idx: number;
  paragraph_idx: number;
  page_start: number;
  snippet: string;
  strudel_use: string;
}

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

function isBookGuidance(x: unknown): x is StrudelBookGuidance {
  if (typeof x !== "object" || x === null) return false;
  const guidance = x as Record<string, unknown>;
  return (
    typeof guidance.book_hash === "string" &&
    typeof guidance.book_title === "string" &&
    typeof guidance.chapter_idx === "number" &&
    typeof guidance.section_idx === "number" &&
    typeof guidance.paragraph_idx === "number" &&
    typeof guidance.page_start === "number" &&
    typeof guidance.snippet === "string" &&
    typeof guidance.strudel_use === "string"
  );
}

function isStrudelGeneration(x: unknown): x is StrudelGeneration {
  if (typeof x !== "object" || x === null) return false;
  const payload = x as Record<string, unknown>;
  return (
    typeof payload.schema_version === "number" &&
    typeof payload.pattern_name === "string" &&
    typeof payload.bpm === "number" &&
    typeof payload.total_beats === "number" &&
    typeof payload.code === "string" &&
    isGeneratedPayload(payload.generated_from) &&
    Array.isArray(payload.book_guidance) &&
    payload.book_guidance.every(isBookGuidance) &&
    Array.isArray(payload.warnings) &&
    payload.warnings.every((warning) => typeof warning === "string")
  );
}

export async function generateStrudel(
  req: GenerateRequest,
): Promise<StrudelGeneration> {
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
  if (!isStrudelGeneration(json)) {
    throw new GenerateError("BFF returned an unexpected Strudel shape", 500);
  }
  return json;
}
