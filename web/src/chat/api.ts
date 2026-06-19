// Thin client over POST /api/chat. Validates the response shape at the
// boundary; everything inside the React tree can trust the type.

import type { ChatRequest, ChatResponse, Citation, LLMChoice } from "./types";

// In dev, vite.config.ts proxies /api → http://localhost:8002.
// In prod, the BFF and the static bundle ship together so /api is same-origin.
const ENDPOINT = "/api/chat";

export class ChatError extends Error {
  readonly status: number;
  readonly reason: string | null;
  constructor(message: string, status: number, reason: string | null = null) {
    super(message);
    this.status = status;
    this.reason = reason;
  }
}

function isLLMChoice(x: unknown): x is LLMChoice {
  return x === "claude" || x === "ollama";
}

function isCitation(x: unknown): x is Citation {
  if (typeof x !== "object" || x === null) return false;
  const c = x as Record<string, unknown>;
  return (
    typeof c.book_hash === "string" &&
    typeof c.book_title === "string" &&
    typeof c.chapter_idx === "number" &&
    typeof c.section_idx === "number" &&
    typeof c.paragraph_idx === "number" &&
    typeof c.page_start === "number" &&
    typeof c.snippet === "string" &&
    typeof c.verified === "boolean"
  );
}

function isChatResponse(x: unknown): x is ChatResponse {
  if (typeof x !== "object" || x === null) return false;
  const r = x as Record<string, unknown>;
  return (
    isLLMChoice(r.llm) &&
    (r.answer === null || typeof r.answer === "string") &&
    Array.isArray(r.citations) &&
    r.citations.every(isCitation) &&
    (r.reason === null || typeof r.reason === "string") &&
    typeof r.elapsed_ms === "number"
  );
}

export async function askTheBooks(req: ChatRequest): Promise<ChatResponse> {
  let response: Response;
  try {
    response = await fetch(ENDPOINT, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(req),
    });
  } catch (err) {
    throw new ChatError(`Network error: ${(err as Error).message}`, 0);
  }

  if (!response.ok) {
    let body: unknown = null;
    try {
      body = await response.json();
    } catch {
      // ignore — the 4xx/5xx body shape isn't load-bearing here
    }
    const reason =
      typeof body === "object" && body !== null && "detail" in body
        ? String((body as { detail: unknown }).detail)
        : null;
    throw new ChatError(
      `Chat request failed (${response.status})`,
      response.status,
      reason,
    );
  }

  const json = await response.json();
  if (!isChatResponse(json)) {
    throw new ChatError("BFF returned an unexpected shape", 500);
  }
  return json;
}
