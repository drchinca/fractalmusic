import { type JSX, useCallback, useEffect, useRef, useState } from "react";

import { generateMusic, GenerateError } from "./api";
import { GeneratedResult } from "./GeneratedResult";
import type { GeneratedPayload } from "./types";

const MAX_CHARS = 500;
const DEFAULT_LENGTH = 16;

function errorMessage(err: unknown): string {
  if (err instanceof GenerateError) return err.message;
  return err instanceof Error ? err.message : String(err);
}

export function DescribePanel(): JSX.Element {
  const [text, setText] = useState<string>("");
  const [payload, setPayload] = useState<GeneratedPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [activeRoleHour, setActiveRoleHour] = useState<number | null>(null);

  const generate = useCallback(async (): Promise<void> => {
    const free_text = text.trim();
    if (free_text.length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const result = await generateMusic({
        tonic: "A",
        mode: "Eólico",
        length: DEFAULT_LENGTH,
        flavor: "free",
        free_text,
      });
      setPayload(result);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [text]);

  // Highlight the role under the playhead — same logic as ComposerPanel.
  useEffect(() => {
    if (payload === null) return;
    const audio = audioRef.current;
    if (audio === null) return;

    function onTime(): void {
      if (audio === null || payload === null) return;
      const t = audio.currentTime;
      const secPerBeat = 60 / payload.bpm;
      const current = payload.events.find((ev) => {
        const start = ev.time_sec;
        const end = start + ev.duration * secPerBeat;
        return t >= start && t < end;
      });
      setActiveRoleHour(current?.role_hour ?? null);
    }

    audio.addEventListener("timeupdate", onTime);
    audio.addEventListener("ended", () => setActiveRoleHour(null));
    return () => {
      audio.removeEventListener("timeupdate", onTime);
    };
  }, [payload]);

  return (
    <section className="composer-panel" aria-label="Describir una canción">
      <header className="composer-header">
        <h1>Describir con palabras</h1>
        <p className="composer-sub">
          Contá el ánimo o el estilo que buscás — un modelo elige tónica, modo y notas
          válidas del Sistema Fractal, y el motor las renderiza como audio real.
        </p>
      </header>

      <form
        className="composer-form"
        onSubmit={(e) => {
          e.preventDefault();
          void generate();
        }}
      >
        <label className="composer-field composer-field-wide">
          <span>Descripción</span>
          <textarea
            value={text}
            maxLength={MAX_CHARS}
            rows={3}
            placeholder="Ej: una melodía pop alegre con trompetas, para empezar el día"
            onChange={(e) => setText(e.target.value)}
          />
          <span className="composer-char-count">
            {text.length} / {MAX_CHARS}
          </span>
        </label>
        <button type="submit" className="composer-generate" disabled={loading || text.trim().length === 0}>
          {loading ? "Componiendo…" : "Generar"}
        </button>
      </form>

      <p className="composer-status" aria-live="polite">
        {loading ? "Eligiendo notas y renderizando audio…" : ""}
      </p>

      {error !== null && <p className="composer-error">No pudimos componer ahora mismo: {error}</p>}

      {payload === null && !loading && error === null && (
        <article className="composer-empty">
          <h2>De palabras a canción</h2>
          <p>
            Escribí el ánimo que buscás y apretá <strong>Generar</strong>. Esto no
            reproduce una canción completa arreglada (batería, trompeta real, estructura
            de verso/estribillo) — elige una melodía real y válida del Sistema Fractal
            que capture esa descripción.
          </p>
        </article>
      )}

      {payload !== null && (
        <GeneratedResult payload={payload} audioRef={audioRef} activeRoleHour={activeRoleHour} />
      )}
    </section>
  );
}
