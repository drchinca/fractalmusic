import { type JSX } from "react";
import { CitationChip } from "./CitationChip";
import type { ChatResponse, Citation } from "./types";

interface AnswerViewProps {
  readonly result: ChatResponse;
}

const MARKER_RE =
  /\[[a-f0-9]{8}\s*[·.:\-\s]\s*ch\d+\s*[§·.:\-\s]\s*\d+\s*[¶·.:\-\s]\s*\d+\s+p\.?\s*\d+\]/gu;

export function AnswerView({ result }: AnswerViewProps): JSX.Element {
  if (result.answer === null) {
    return <NullAnswer result={result} />;
  }
  return <GroundedAnswer answer={result.answer} citations={result.citations} />;
}

function GroundedAnswer({
  answer,
  citations,
}: {
  readonly answer: string;
  readonly citations: readonly Citation[];
}): JSX.Element {
  // Strip the inline markers so the prose reads cleanly; the chips below
  // give the user verifiable provenance instead.
  const prose = answer.replace(MARKER_RE, "").replace(/\s+\./g, ".").trim();
  return (
    <div className="answer-view answer-grounded">
      <p className="answer-prose">{prose}</p>
      <div className="answer-citations" aria-label="Citations supporting this answer">
        {citations.map((c, i) => (
          <CitationChip
            key={`${c.book_hash}-${c.chapter_idx}-${c.section_idx}-${c.paragraph_idx}-${i}`}
            citation={c}
            index={i + 1}
          />
        ))}
      </div>
    </div>
  );
}

function NullAnswer({ result }: { readonly result: ChatResponse }): JSX.Element {
  const reasonCopy: Record<string, string> = {
    no_evidence_in_corpus: "No tengo evidencia suficiente en estos libros para responder.",
    unknown_chunk: "Encontré pasajes, pero no pude anclar la respuesta a ellos con confianza.",
    low_fidelity: "Encontré pasajes, pero no pude anclar la respuesta a ellos con confianza.",
    uncited_claim: "Encontré pasajes, pero no pude anclar la respuesta a ellos con confianza.",
    no_citations: "Encontré pasajes, pero no pude anclar la respuesta a ellos con confianza.",
  };
  const message = reasonCopy[result.reason ?? ""] ?? "No pude responder con seguridad.";
  return (
    <div className="answer-view answer-null">
      <p className="answer-null-message">{message}</p>
      {result.citations.length > 0 && (
        <>
          <p className="answer-null-hint">Lo que sí encontré en los libros:</p>
          <div className="answer-citations">
            {result.citations.map((c, i) => (
              <CitationChip
                key={`${c.book_hash}-${c.chapter_idx}-${c.section_idx}-${c.paragraph_idx}-${i}`}
                citation={c}
                index={i + 1}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
