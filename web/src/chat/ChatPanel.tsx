import { type FormEvent, type JSX, useState } from "react";

import { AnswerView } from "./AnswerView";
import { LLMToggle } from "./LLMToggle";
import { ChatError, askTheBooks } from "./api";
import type { ChatResponse, LLMChoice } from "./types";

type Status =
  | { readonly kind: "idle" }
  | { readonly kind: "loading" }
  | { readonly kind: "ready"; readonly result: ChatResponse }
  | { readonly kind: "error"; readonly message: string };

const SUGGESTIONS: readonly string[] = [
  "¿Qué es el Dodecamundo?",
  "¿Por qué Frigio suena flamenco?",
  "¿Cómo se relacionan Locrio y Jónico?",
  "¿Qué es la Cero Pitágoras?",
];

export function ChatPanel(): JSX.Element {
  const [question, setQuestion] = useState("");
  const [llm, setLlm] = useState<LLMChoice>("claude");
  const [status, setStatus] = useState<Status>({ kind: "idle" });

  const isLoading = status.kind === "loading";
  const trimmed = question.trim();
  const canSubmit = trimmed.length >= 3 && !isLoading;

  async function submit(e: FormEvent): Promise<void> {
    e.preventDefault();
    if (!canSubmit) return;
    setStatus({ kind: "loading" });
    try {
      const result = await askTheBooks({ question: trimmed, llm });
      setStatus({ kind: "ready", result });
    } catch (err) {
      const message =
        err instanceof ChatError
          ? `${err.message}${err.reason ? ` — ${err.reason}` : ""}`
          : (err as Error).message;
      setStatus({ kind: "error", message });
    }
  }

  function pickSuggestion(s: string): void {
    setQuestion(s);
  }

  return (
    <section className="chat-panel" aria-label="Pregunta a los libros">
      <header className="chat-header">
        <h2>Pregunta a los libros</h2>
        <p className="chat-blurb">
          Las respuestas vienen de <em>El Sistema Fractal</em> y{" "}
          <em>2025 Fractal Music World</em>. Cada afirmación enlaza al pasaje
          original.
        </p>
      </header>

      <form className="chat-form" onSubmit={submit}>
        <label className="chat-question-label" htmlFor="chat-question">
          Tu pregunta
        </label>
        <textarea
          id="chat-question"
          className="chat-question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="¿Qué es el Dodecamundo?"
          rows={3}
          maxLength={500}
          disabled={isLoading}
        />

        <div className="chat-controls">
          <LLMToggle value={llm} onChange={setLlm} disabled={isLoading} />
          <button
            type="submit"
            className="chat-submit"
            disabled={!canSubmit}
            aria-busy={isLoading}
          >
            {isLoading ? "Buscando…" : "Preguntar"}
          </button>
        </div>

        {status.kind === "idle" && (
          <ul className="chat-suggestions" aria-label="Sugerencias">
            {SUGGESTIONS.map((s) => (
              <li key={s}>
                <button
                  type="button"
                  className="chat-suggestion"
                  onClick={() => pickSuggestion(s)}
                >
                  {s}
                </button>
              </li>
            ))}
          </ul>
        )}
      </form>

      <output className="chat-output" aria-live="polite">
        {status.kind === "loading" && (
          <p className="chat-loading">Leyendo los libros…</p>
        )}
        {status.kind === "ready" && <AnswerView result={status.result} />}
        {status.kind === "error" && (
          <div className="chat-error" role="alert">
            <p>{status.message}</p>
            <p className="chat-error-hint">
              Si el BFF no está corriendo: <code>cd chat_bff &amp;&amp; uv run uvicorn chat_bff.app:create_app --factory</code>
            </p>
          </div>
        )}
      </output>
    </section>
  );
}
