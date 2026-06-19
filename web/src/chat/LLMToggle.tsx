import { type JSX } from "react";
import type { LLMChoice } from "./types";

interface LLMToggleProps {
  readonly value: LLMChoice;
  readonly onChange: (next: LLMChoice) => void;
  readonly disabled: boolean;
}

export function LLMToggle({ value, onChange, disabled }: LLMToggleProps): JSX.Element {
  return (
    <fieldset className="llm-toggle" disabled={disabled}>
      <legend className="llm-toggle-legend">Modelo</legend>
      <label className={`llm-toggle-option ${value === "claude" ? "is-selected" : ""}`}>
        <input
          type="radio"
          name="llm"
          value="claude"
          checked={value === "claude"}
          onChange={() => onChange("claude")}
        />
        <span>Claude</span>
      </label>
      <label className={`llm-toggle-option ${value === "ollama" ? "is-selected" : ""}`}>
        <input
          type="radio"
          name="llm"
          value="ollama"
          checked={value === "ollama"}
          onChange={() => onChange("ollama")}
        />
        <span>Ollama (local)</span>
      </label>
    </fieldset>
  );
}
