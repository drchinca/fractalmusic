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

function copyForReason(
  reason: string | null,
  hasSources: boolean,
): { readonly headline: string; readonly hint: string | null } {
  // unknown_chunk: LLM cited a paragraph we didn't retrieve — almost
  //   always means the answer is in a chapter not yet indexed.
  // low_fidelity | uncited_claim | no_citations: model saw passages but
  //   couldn't ground in them.
  // no_evidence_in_corpus: retrieval found nothing.
  if (reason === "no_evidence_in_corpus") {
    return {
      headline:
        "No encontré nada en estos libros sobre tu pregunta. Probá una más cercana al Sistema Fractal — el Dodecamundo, los modos griegos, o las cartas.",
      hint: null,
    };
  }
  if (reason === "unknown_chunk") {
    return {
      headline:
        "El modelo intentó citar un pasaje que no está en la parte indexada de los libros. Esa respuesta probablemente vive en un capítulo aún no incluido.",
      hint: hasSources ? "Pasajes relacionados que sí están indexados:" : null,
    };
  }
  if (reason === "low_fidelity" || reason === "uncited_claim" || reason === "no_citations") {
    return {
      headline:
        "Encontré pasajes pero no pude responder con confianza desde ellos. Mirá lo que aparece y juzgá vos.",
      hint: hasSources ? "Pasajes relacionados:" : null,
    };
  }
  return { headline: "No pude responder con seguridad.", hint: null };
}

function NullAnswer({ result }: { readonly result: ChatResponse }): JSX.Element {
  const copy = copyForReason(result.reason, result.citations.length > 0);
  return (
    <div className="answer-view answer-null">
      <p className="answer-null-message">{copy.headline}</p>
      {copy.hint !== null && result.citations.length > 0 && (
        <>
          <p className="answer-null-hint">{copy.hint}</p>
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
