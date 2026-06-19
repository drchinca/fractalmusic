import { type JSX, useCallback, useEffect, useRef, useState } from "react";

import { fetchOptions, generateMusic, GenerateError } from "./api";
import { isFlavor } from "./types";
import type { ComposerOptions, Flavor, GeneratedPayload } from "./types";

const FLAVOR_LABELS: Record<Flavor, string> = {
  free: "Libre",
  "penta-walk": "Paseo pentatónico",
  "carta-progression": "Progresión de cartas",
};

const BAND_LABELS: Record<GeneratedPayload["confidence"]["band"], string> = {
  strong: "Fiel al libro",
  tentative: "Inspirado en el libro",
  exploratory: "Exploración libre",
};

function errorMessage(err: unknown): string {
  if (err instanceof GenerateError) return err.message;
  return err instanceof Error ? err.message : String(err);
}

export function ComposerPanel(): JSX.Element {
  const [options, setOptions] = useState<ComposerOptions | null>(null);
  const [optionsError, setOptionsError] = useState<string | null>(null);

  const [tonic, setTonic] = useState<string>("A");
  const [mode, setMode] = useState<string>("Eólico");
  const [length, setLength] = useState<number>(16);
  const [flavor, setFlavor] = useState<Flavor>("free");
  const [showExtras, setShowExtras] = useState<boolean>(false);

  const [payload, setPayload] = useState<GeneratedPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [activeRoleHour, setActiveRoleHour] = useState<number | null>(null);

  useEffect(() => {
    fetchOptions()
      .then((opts) => setOptions(opts))
      .catch((err: unknown) => setOptionsError(errorMessage(err)));
  }, []);

  const generate = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const result = await generateMusic({ tonic, mode, length, flavor });
      setPayload(result);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [tonic, mode, length, flavor]);

  // Highlight the role under the playhead.
  useEffect(() => {
    if (payload === null) return;
    const audio = audioRef.current;
    if (audio === null) return;

    function onTime(): void {
      if (audio === null || payload === null) return;
      const t = audio.currentTime;
      // Find the latest event whose time_sec <= t and time_sec + duration_sec > t.
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

  if (optionsError !== null) {
    return (
      <section className="composer-panel" aria-label="Compositor fractal">
        <p className="composer-error">No pudimos cargar el compositor: {optionsError}</p>
      </section>
    );
  }

  if (options === null) {
    return (
      <section className="composer-panel" aria-label="Compositor fractal">
        <p className="composer-meta">Cargando…</p>
      </section>
    );
  }

  return (
    <section className="composer-panel" aria-label="Compositor fractal">
      <header className="composer-header">
        <h1>Componer con la rueda</h1>
        <p className="composer-sub">
          La rueda elige las notas, el motor las hace sonar como un instrumento real.
        </p>
      </header>

      <form
        className="composer-form"
        onSubmit={(e) => {
          e.preventDefault();
          void generate();
        }}
      >
        <label className="composer-field">
          <span>Tónica</span>
          <select value={tonic} onChange={(e) => setTonic(e.target.value)}>
            {options.tonics.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
        <label className="composer-field">
          <span>Modo</span>
          <select value={mode} onChange={(e) => setMode(e.target.value)}>
            {options.modes.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" className="composer-generate" disabled={loading}>
          {loading ? "Componiendo…" : "Generar"}
        </button>

        {showExtras && (
          <>
            <label className="composer-field">
              <span>Cantidad de notas</span>
              <input
                type="number"
                min={4}
                max={64}
                value={length}
                onChange={(e) => setLength(Number(e.target.value))}
              />
            </label>
            <label className="composer-field">
              <span>Estilo</span>
              <select
                value={flavor}
                onChange={(e) => {
                  const v = e.target.value;
                  if (isFlavor(v)) setFlavor(v);
                }}
              >
                {options.flavors.map((f) => (
                  <option key={f} value={f}>
                    {FLAVOR_LABELS[f]}
                  </option>
                ))}
              </select>
            </label>
          </>
        )}

        <button
          type="button"
          className="composer-extras-toggle"
          onClick={() => setShowExtras((v) => !v)}
          aria-expanded={showExtras}
        >
          {showExtras ? "Menos opciones" : "Más opciones"}
        </button>
      </form>

      <p className="composer-status" aria-live="polite">
        {loading ? "Componiendo y renderizando audio…" : ""}
      </p>

      {error !== null && (
        <p className="composer-error">No pudimos componer ahora mismo: {error}</p>
      )}

      {payload === null && !loading && error === null && (
        <article className="composer-empty">
          <h2>Tu primera melodía</h2>
          <p>
            Apretá <strong>Generar</strong> y la rueda elige {length} notas en{" "}
            {tonic} {mode}. El motor las renderiza con piano, pad y un drone — sale un WAV
            real, no un beep.
          </p>
        </article>
      )}

      {payload !== null && (
        <article className="composer-result" aria-live="polite">
          <header className="composer-result-head">
            <h2>{payload.key_label}</h2>
            <span className={`composer-band composer-band-${payload.confidence.band}`}>
              {BAND_LABELS[payload.confidence.band]}
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
                className={`composer-note ${
                  activeRoleHour === ev.role_hour ? "is-active" : ""
                }`}
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
            {payload.provenance.chapter !== null && (
              <span> · {payload.provenance.chapter}</span>
            )}
            {payload.provenance.quote !== null && (
              <blockquote>{payload.provenance.quote}</blockquote>
            )}
          </footer>
        </article>
      )}
    </section>
  );
}
