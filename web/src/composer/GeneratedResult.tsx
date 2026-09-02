import { type JSX, type RefObject } from "react";

import { AuditTrail } from "./AuditTrail";
import { runIdFromAudioUrl } from "./auditApi";
import type { GeneratedPayload } from "./types";

// Score.band measures adherence to the Sistema Fractal's own rules (mode
// membership, rhythmic coherence, fractal shape) — it says nothing about
// whether the pattern's notes came from the book corpus. For patterns an
// LLM composed from a free-text description, "faithful to the book" would
// be a false claim (provenance.book_hash="llm-composed" already says so
// honestly) — so the label set is picked by source, not just by band.
const BOOK_BAND_LABELS: Record<GeneratedPayload["confidence"]["band"], string> = {
  strong: "Fiel al libro",
  tentative: "Inspirado en el libro",
  exploratory: "Exploración libre",
};
const LLM_BAND_LABELS: Record<GeneratedPayload["confidence"]["band"], string> = {
  strong: "Fiel al sistema",
  tentative: "Inspirado en el sistema",
  exploratory: "Exploración libre",
};

interface GeneratedResultProps {
  payload: GeneratedPayload;
  audioRef: RefObject<HTMLAudioElement | null>;
  activeRoleHour: number | null;
}

export function GeneratedResult({ payload, audioRef, activeRoleHour }: GeneratedResultProps): JSX.Element {
  const isLlmComposed = payload.provenance.book_hash === "llm-composed";
  const bandLabels = isLlmComposed ? LLM_BAND_LABELS : BOOK_BAND_LABELS;
  const runId = payload.audio_url !== null ? runIdFromAudioUrl(payload.audio_url) : null;
  return (
    <article className="composer-result" aria-live="polite">
      <header className="composer-result-head">
        <h2>{payload.key_label}</h2>
        <span className={`composer-band composer-band-${payload.confidence.band}`}>
          {bandLabels[payload.confidence.band]}
        </span>
      </header>

      {payload.audio_url !== null && (
        <audio
          ref={audioRef}
          controls
          className="composer-audio"
          src={payload.audio_url}
          preload="auto"
        >
          Tu navegador no soporta el reproductor de audio.
        </audio>
      )}

      <div className="composer-meta-row">
        <span className="composer-meta">
          {payload.events.length} notas · ♩ = {payload.bpm}
        </span>
        {payload.audio_url !== null && (
          <a
            className="composer-download"
            href={payload.audio_url}
            download={`fractalmusic-${payload.tonic}-${payload.mode}.wav`}
          >
            ↓ Descargar WAV
          </a>
        )}
      </div>

      <div className="composer-strip" role="list">
        {payload.events.map((ev, i) => (
          <span
            key={i}
            role="listitem"
            className={`composer-note ${activeRoleHour === ev.role_hour ? "is-active" : ""}`}
            title={`${ev.note}${ev.octave} · posición ${ev.role_hour} en la rueda · ${ev.carta_glyph}`}
          >
            <span className="composer-note-glyph">{ev.carta_glyph}</span>
            <span className="composer-note-name">
              {ev.note}
              <sub>{ev.octave}</sub>
            </span>
          </span>
        ))}
      </div>

      <footer className="composer-prov">
        <span>{payload.provenance.book_title}</span>
        {payload.provenance.chapter !== null && <span> · {payload.provenance.chapter}</span>}
        {payload.provenance.quote !== null && <blockquote>{payload.provenance.quote}</blockquote>}
      </footer>

      {runId !== null && <AuditTrail runId={runId} />}
    </article>
  );
}
