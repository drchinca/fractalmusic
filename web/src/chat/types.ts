// Mirrors chat_bff Pydantic models. These are validated on every fetch
// — the BFF can change shape and we'll surface it as a parse error
// rather than a confusing runtime crash deep in a component.

export type LLMChoice = "claude" | "ollama";

export interface Citation {
  readonly book_hash: string;
  readonly book_title: string;
  readonly chapter_idx: number;
  readonly section_idx: number;
  readonly paragraph_idx: number;
  readonly page_start: number;
  readonly snippet: string;
  readonly verified: boolean;
}

export interface ChatRequest {
  readonly question: string;
  readonly llm: LLMChoice;
}

export interface ChatResponse {
  readonly llm: LLMChoice;
  readonly answer: string | null;
  readonly citations: readonly Citation[];
  readonly model_reading: string | null;
  readonly reason: string | null;
  readonly elapsed_ms: number;
}
