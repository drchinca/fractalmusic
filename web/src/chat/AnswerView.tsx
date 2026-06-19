import { type JSX } from "react";
import { CitationChip } from "./CitationChip";
import type { ChatResponse, Citation } from "./types";

interface AnswerViewProps {
  readonly result: ChatResponse;
}

const MARKER_RE =
  /\[[a-f0-9]{8}\s*[·.:\-\s]\s*ch\d+\s*[§·.:\-\s]\s*\d+\s*[¶·.:\-\s]\s*\d+\s+p\.?\s*\d+\]/gu;

export function AnswerView({ result }: AnswerViewProps): JSX.Element {
  if (result.answer !== null) {
    return <GroundedAnswer answer={result.answer} citations={result.citations} />;
  }
  if (result.model_reading !== null) {
    return <ReadingAnswer text={result.model_reading} citations={result.citations} />;
  }
  // No verified answer AND no reading: retrieval was empty (out of corpus)
  // or the model_reading second pass itself failed.
  const headline =
    result.reason === "no_evidence_in_corpus"
      ? "No encontré nada en estos libros sobre tu pregunta. Probá una más cercana al Sistema Fractal — el Dodecamundo, los modos griegos, o las cartas."
      : "No pude responder con seguridad.";
  return (
    <div className="answer-view answer-null">
      <p className="answer-null-message">{headline}</p>
    </div>
  );
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

function ReadingAnswer({
  text,
  citations,
}: {
  readonly text: string;
  readonly citations: readonly Citation[];
}): JSX.Element {
  // The interpretive reply when strict citation grounding failed.
  // Badge + dashed border carry the "this is softer" signal; the prose
  // and the chunk list below it speak for themselves.
  return (
    <div className="answer-view answer-reading">
      <span className="answer-reading-badge">Lectura del modelo</span>
      <p className="answer-prose">{text}</p>
      {citations.length > 0 && (
        <>
          <p className="answer-null-hint">Pasajes encontrados en los libros:</p>
          <div className="answer-citations">
            {citations.map((c, i) => (
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

