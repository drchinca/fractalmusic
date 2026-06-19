import { type JSX, useState } from "react";
import type { Citation } from "./types";

interface CitationChipProps {
  readonly citation: Citation;
  readonly index: number;
}

export function CitationChip({ citation, index }: CitationChipProps): JSX.Element {
  const [open, setOpen] = useState(false);
  const label = `${index} · ${citation.book_title} p.${citation.page_start}`;
  return (
    <span className={`citation-chip ${citation.verified ? "is-verified" : "is-source"}`}>
      <button
        type="button"
        className="citation-chip-button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-label={`Mostrar cita ${index} de ${citation.book_title}, página ${citation.page_start}`}
      >
        {label}
      </button>
      {open && (
        <span className="citation-chip-snippet" role="tooltip">
          <span className="citation-chip-meta">
            {citation.book_hash} · ch{citation.chapter_idx}§{citation.section_idx}¶
            {citation.paragraph_idx} · p.{citation.page_start}
          </span>
          <span className="citation-chip-text">{citation.snippet}</span>
        </span>
      )}
    </span>
  );
}
