// Thin client over GET /api/audit/{run_id} — the real CEMAF audit trail for
// one generation run (every candidate research_loop weighed, not just the
// pattern that won). Validates response shape at the boundary.

const ENDPOINT = "/api/audit";

export class AuditError extends Error {
  readonly status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

export interface AuditEntry {
  readonly id: string;
  readonly type: string;
  readonly timestamp: string;
  readonly source: string;
  readonly payload: Readonly<Record<string, unknown>>;
}

export interface AuditTimeline {
  readonly run_id: string;
  readonly entries: readonly AuditEntry[];
}

function isAuditEntry(x: unknown): x is AuditEntry {
  if (typeof x !== "object" || x === null) return false;
  const e = x as Record<string, unknown>;
  return (
    typeof e.id === "string" &&
    typeof e.type === "string" &&
    typeof e.timestamp === "string" &&
    typeof e.source === "string" &&
    typeof e.payload === "object" &&
    e.payload !== null
  );
}

function isAuditTimeline(x: unknown): x is AuditTimeline {
  if (typeof x !== "object" || x === null) return false;
  const p = x as Record<string, unknown>;
  return typeof p.run_id === "string" && Array.isArray(p.entries) && p.entries.every(isAuditEntry);
}

// run_id is the same content-addressed cache key already in audio_url
// ("<cache_url>/<run_id>.wav") — no new identifier to thread through.
export function runIdFromAudioUrl(audioUrl: string): string | null {
  const match = /\/([^/]+)\.wav$/.exec(audioUrl);
  return match ? match[1] : null;
}

export async function fetchAuditTrail(runId: string): Promise<AuditTimeline> {
  let response: Response;
  try {
    response = await fetch(`${ENDPOINT}/${encodeURIComponent(runId)}`);
  } catch (err) {
    throw new AuditError(`Network error: ${errorMessage(err)}`, 0);
  }
  if (!response.ok) {
    let detail = "request failed";
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // ignore
    }
    throw new AuditError(detail, response.status);
  }
  const json: unknown = await response.json();
  if (!isAuditTimeline(json)) {
    throw new AuditError("BFF returned an unexpected audit shape", 500);
  }
  return json;
}
