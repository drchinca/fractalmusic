import {
  type CSSProperties,
  type FormEvent,
  type JSX,
  type KeyboardEvent as ReactKeyboardEvent,
  type PointerEvent as ReactPointerEvent,
  useCallback,
  useEffect,
  useId,
  useRef,
  useState,
} from "react";
import "@strudel/repl";

import { fetchOptions, GenerateError } from "../composer/api";
import { isFlavor } from "../composer/types";
import type { ComposerOptions, Flavor } from "../composer/types";
import { generateStrudel, type StrudelGeneration } from "./api";

const STARTER_CODE = `setcps(0.75)

stack(
  note("<a2 e3 c3 g2>")
    .sound("sawtooth")
    .lpf(700)
    .gain(.22),
  note("a4 [c5 e5] <g5 e5>")
    .sound("triangle")
    .delay(.25)
    .room(.35)
    .gain(.16),
  note("<a3 c4 e4 g4>*2")
    .sound("sine")
    .gain(.1)
)`;

const FLAVOR_LABELS: Record<Flavor, string> = {
  free: "Libre",
  "penta-walk": "Paseo pentatónico",
  "carta-progression": "Progresión de cartas",
};

const BAND_LABELS: Record<"strong" | "tentative" | "exploratory", string> = {
  strong: "Fiel al libro",
  tentative: "Inspirado en el libro",
  exploratory: "Exploración libre",
};

const SOUND_LABELS: Record<"sine" | "triangle" | "sawtooth" | "square", string> = {
  sine: "Senoidal",
  triangle: "Triángulo",
  sawtooth: "Sierra",
  square: "Cuadrada",
};

const BASS_LABELS: Record<"root" | "walk" | "octaves", string> = {
  root: "Tónica",
  walk: "Caminado",
  octaves: "Octavas",
};

const KICK_LABELS: Record<"four" | "half" | "syncopated" | "euclid", string> = {
  four: "Cuatro al piso",
  half: "A medias",
  syncopated: "Sincopado",
  euclid: "Euclídeo",
};

const SNARE_LABELS: Record<"backbeat" | "clap" | "four" | "offbeat", string> = {
  backbeat: "Contratiempo",
  clap: "Palmas",
  four: "Cuatro pulsos",
  offbeat: "Fuera del pulso",
};

const HAT_LABELS: Record<"eighth" | "sixteenth" | "skip" | "open", string> = {
  eighth: "Corcheas",
  sixteenth: "Semicorcheas",
  skip: "Saltado",
  open: "Abierto",
};

const FILL_LABELS: Record<"none" | "clap-drop" | "tom-run" | "snare-roll", string> = {
  none: "Sin remate",
  "clap-drop": "Bajón con palma",
  "tom-run": "Vuelta de toms",
  "snare-roll": "Redoble de caja",
};

type StrudelSound = "sine" | "triangle" | "sawtooth" | "square";
type CodeMode = "controlled" | "manual";
type DrumBank = "tr808" | "tr909" | "tr707";
type KickPattern = "four" | "half" | "syncopated" | "euclid";
type SnarePattern = "backbeat" | "clap" | "four" | "offbeat";
type HatPattern = "eighth" | "sixteenth" | "skip" | "open";
type FillPattern = "none" | "clap-drop" | "tom-run" | "snare-roll";
type BassPattern = "root" | "walk" | "octaves";

interface StrudelSurfaceControls {
  voiceSound: StrudelSound;
  voiceGain: number;
  octaveShift: number;
  speed: number;
  droneEnabled: boolean;
  droneSound: StrudelSound;
  droneOctave: number;
  droneGain: number;
  filterEnabled: boolean;
  filterCutoff: number;
  delay: number;
  room: number;
  bassEnabled: boolean;
  bassPattern: BassPattern;
  bassSound: StrudelSound;
  bassGain: number;
  bassCutoff: number;
  drumsEnabled: boolean;
  drumBank: DrumBank;
  kickEnabled: boolean;
  kickPattern: KickPattern;
  kickGain: number;
  snareEnabled: boolean;
  snarePattern: SnarePattern;
  snareGain: number;
  hatsEnabled: boolean;
  hatPattern: HatPattern;
  hatGain: number;
  fillPattern: FillPattern;
  fillGain: number;
  drumRoom: number;
  drumDelay: number;
  swing: number;
}

interface StrudelEditorElement extends HTMLElement {
  editor?: {
    clear?: () => void;
    code?: string;
    evaluate?: () => Promise<void> | void;
    setCode?: (code: string) => void;
    stop?: () => void;
  };
}

interface KnobProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  disabled?: boolean;
  onChange: (value: number) => void;
}

const SOUND_OPTIONS: readonly StrudelSound[] = ["triangle", "sine", "sawtooth", "square"];
const DRUM_BANK_OPTIONS: readonly DrumBank[] = ["tr909", "tr808", "tr707"];

const SPEED_OPTIONS: readonly { label: string; value: number }[] = [
  { label: "1/2", value: 0.5 },
  { label: "1", value: 1 },
  { label: "3/2", value: 1.5 },
  { label: "2", value: 2 },
];

const KICK_PATTERNS: Record<KickPattern, string> = {
  four: "bd*4",
  half: "bd ~ bd ~",
  syncopated: "bd [~ bd] ~ bd",
  euclid: "bd(5,8)",
};

const SNARE_PATTERNS: Record<SnarePattern, string> = {
  backbeat: "~ sd ~ sd",
  clap: "~ cp ~ cp",
  four: "sd*4",
  offbeat: "~ ~ sd [~ cp]",
};

const HAT_PATTERNS: Record<HatPattern, string> = {
  eighth: "hh*8",
  sixteenth: "hh*16",
  skip: "[hh ~]*4",
  open: "hh*6 [oh hh]",
};

const FILL_PATTERNS: Record<FillPattern, string | null> = {
  none: null,
  "clap-drop": "~ ~ ~ [cp sd]",
  "tom-run": "~ ~ [lt mt] [ht cp]",
  "snare-roll": "~ ~ sd*4 cp",
};

const DEFAULT_SURFACE: StrudelSurfaceControls = {
  voiceSound: "triangle",
  voiceGain: 0.22,
  octaveShift: 0,
  speed: 1,
  droneEnabled: true,
  droneSound: "sine",
  droneOctave: 2,
  droneGain: 0.08,
  filterEnabled: false,
  filterCutoff: 1200,
  delay: 0,
  room: 0,
  bassEnabled: true,
  bassPattern: "root",
  bassSound: "sawtooth",
  bassGain: 0.14,
  bassCutoff: 500,
  drumsEnabled: true,
  drumBank: "tr909",
  kickEnabled: true,
  kickPattern: "four",
  kickGain: 0.75,
  snareEnabled: true,
  snarePattern: "backbeat",
  snareGain: 0.38,
  hatsEnabled: true,
  hatPattern: "eighth",
  hatGain: 0.18,
  fillPattern: "none",
  fillGain: 0.34,
  drumRoom: 0.12,
  drumDelay: 0,
  swing: 0,
};

function errorMessage(err: unknown): string {
  if (err instanceof GenerateError) return err.message;
  return err instanceof Error ? err.message : String(err);
}

function loadEditorCode(editor: StrudelEditorElement, code: string): void {
  editor.setAttribute("code", code);
  editor.editor?.setCode?.(code);
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function stepValue(value: number, min: number, max: number, step: number): number {
  const stepped = Math.round((clamp(value, min, max) - min) / step) * step + min;
  return Number(clamp(stepped, min, max).toFixed(4));
}

function numberFromInput(value: string, fallback: number, min: number, max: number): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return clamp(parsed, min, max);
}

function fmtNumber(value: number): string {
  if (Number.isInteger(value)) return String(value);
  return value.toFixed(3).replace(/0+$/, "").replace(/\.$/, "");
}

function commentText(value: string, limit = 120): string {
  return value.replace(/[\r\n]+/g, " ").replace(/\s+/g, " ").trim().slice(0, limit);
}

function shiftedNote(note: string, octave: number, shift: number): string {
  return `${note.toLowerCase()}${clamp(octave + shift, 0, 8)}`;
}

function bassNotes(generation: StrudelGeneration, controls: StrudelSurfaceControls): string {
  const source = generation.generated_from;
  if (controls.bassPattern === "root") {
    return `${source.tonic.toLowerCase()}1*4`;
  }
  if (controls.bassPattern === "octaves") {
    return `${source.tonic.toLowerCase()}1 ${source.tonic.toLowerCase()}2`;
  }
  return source.events
    .slice(0, 8)
    .map((event) => shiftedNote(event.note, Math.min(event.octave, 2), -2))
    .join(" ");
}

function drumLayer(pattern: string, controls: StrudelSurfaceControls, gain: number): string {
  const lines = [
    `  s("${pattern}")`,
    `    .bank("${controls.drumBank}")`,
    `    .gain(${fmtNumber(gain)})`,
  ];
  if (controls.drumRoom > 0) {
    lines.push(`    .room(${fmtNumber(controls.drumRoom)})`);
  }
  if (controls.drumDelay > 0) {
    lines.push(`    .delay(${fmtNumber(controls.drumDelay)})`);
  }
  if (controls.swing > 0) {
    lines.push(`    .swingBy(${fmtNumber(controls.swing)}, 4)`);
  }
  return lines.join("\n");
}

function buildControlledCode(
  generation: StrudelGeneration,
  controls: StrudelSurfaceControls,
): string {
  const source = generation.generated_from;
  const notes = source.events
    .map((event) => shiftedNote(event.note, event.octave, controls.octaveShift))
    .join(" ");
  const cycle = fmtNumber(generation.total_beats);
  const speed = fmtNumber(controls.speed);
  const drone = `${source.tonic.toLowerCase()}${controls.droneOctave}`;

  const voiceLines = [
    `  note("${notes}")`,
    `    .sound("${controls.voiceSound}")`,
    `    .gain(${fmtNumber(controls.voiceGain)})`,
  ];
  if (controls.filterEnabled) {
    voiceLines.push(`    .lpf(${fmtNumber(controls.filterCutoff)})`);
  }
  if (controls.delay > 0) {
    voiceLines.push(`    .delay(${fmtNumber(controls.delay)})`);
  }
  if (controls.room > 0) {
    voiceLines.push(`    .room(${fmtNumber(controls.room)})`);
  }

  const layers = [voiceLines.join("\n")];
  if (controls.droneEnabled) {
    layers.push(
      [
        `  note("${drone}")`,
        `    .sound("${controls.droneSound}")`,
        `    .slow(${cycle})`,
        `    .gain(${fmtNumber(controls.droneGain)})`,
      ].join("\n"),
    );
  }
  if (controls.bassEnabled) {
    layers.push(
      [
        `  note("${bassNotes(generation, controls)}")`,
        `    .sound("${controls.bassSound}")`,
        `    .lpf(${fmtNumber(controls.bassCutoff)})`,
        `    .gain(${fmtNumber(controls.bassGain)})`,
      ].join("\n"),
    );
  }
  if (controls.drumsEnabled) {
    if (controls.kickEnabled) {
      layers.push(drumLayer(KICK_PATTERNS[controls.kickPattern], controls, controls.kickGain));
    }
    if (controls.snareEnabled) {
      layers.push(drumLayer(SNARE_PATTERNS[controls.snarePattern], controls, controls.snareGain));
    }
    if (controls.hatsEnabled) {
      layers.push(drumLayer(HAT_PATTERNS[controls.hatPattern], controls, controls.hatGain));
    }
    const fillPattern = FILL_PATTERNS[controls.fillPattern];
    if (fillPattern !== null) {
      layers.push(drumLayer(fillPattern, controls, controls.fillGain));
    }
  }

  const bookComments = generation.book_guidance.flatMap((guidance, index) => [
    `// book ${index + 1}: ${commentText(guidance.book_hash, 16)} p.${guidance.page_start} ${commentText(guidance.book_title, 64)}`,
    `// strudel use ${index + 1}: ${commentText(guidance.strudel_use, 180)}`,
  ]);

  return [
    `// Fractal Music: ${generation.pattern_name}`,
    `// key: ${source.key_label}`,
    `// confidence: ${source.confidence.band} ${fmtNumber(source.confidence.score)}`,
    `// roles: ${source.events.map((event) => event.role_hour).join(" ")}`,
    `// glyphs: ${source.events.map((event) => event.carta_glyph).join(" ")}`,
    `// surface: voice=${controls.voiceSound} speed=${speed} octave=${controls.octaveShift} bank=${controls.drumBank}`,
    `// source: ${source.provenance.book_title}`,
    ...(source.provenance.chapter === null ? [] : [`// chapter: ${source.provenance.chapter}`]),
    ...bookComments,
    `setcps(${generation.bpm} / 60 / ${cycle} * ${speed})`,
    "",
    "stack(",
    layers.join(",\n"),
    ")",
  ].join("\n");
}

function Knob({ label, value, min, max, step, disabled = false, onChange }: KnobProps): JSX.Element {
  const dragRef = useRef<{ pointerId: number; startY: number; startValue: number } | null>(null);
  const percent = max === min ? 0 : (value - min) / (max - min);
  const rotation = -135 + clamp(percent, 0, 1) * 270;
  const sweep = clamp(percent, 0, 1) * 270;
  const style = {
    "--knob-rotation": `${rotation}deg`,
    "--knob-sweep": `${sweep}deg`,
  } as CSSProperties;

  function commit(nextValue: number): void {
    if (disabled) return;
    onChange(stepValue(nextValue, min, max, step));
  }

  function onPointerDown(event: ReactPointerEvent<HTMLDivElement>): void {
    if (disabled) return;
    event.preventDefault();
    event.currentTarget.setPointerCapture(event.pointerId);
    dragRef.current = {
      pointerId: event.pointerId,
      startY: event.clientY,
      startValue: value,
    };
  }

  function onPointerMove(event: ReactPointerEvent<HTMLDivElement>): void {
    const drag = dragRef.current;
    if (drag === null || drag.pointerId !== event.pointerId) return;
    const delta = (drag.startY - event.clientY) * ((max - min) / 180);
    commit(drag.startValue + delta);
  }

  function onPointerEnd(event: ReactPointerEvent<HTMLDivElement>): void {
    if (dragRef.current?.pointerId === event.pointerId) {
      dragRef.current = null;
    }
  }

  function onKeyDown(event: ReactKeyboardEvent<HTMLDivElement>): void {
    if (disabled) return;
    let nextValue: number | null = null;
    if (event.key === "ArrowUp" || event.key === "ArrowRight") nextValue = value + step;
    if (event.key === "ArrowDown" || event.key === "ArrowLeft") nextValue = value - step;
    if (event.key === "PageUp") nextValue = value + step * 10;
    if (event.key === "PageDown") nextValue = value - step * 10;
    if (event.key === "Home") nextValue = min;
    if (event.key === "End") nextValue = max;
    if (nextValue === null) return;
    event.preventDefault();
    commit(nextValue);
  }

  return (
    <label className={`strudel-knob ${disabled ? "is-disabled" : ""}`}>
      <span>{label}</span>
      <div
        role="slider"
        tabIndex={disabled ? -1 : 0}
        aria-label={label}
        aria-valuemin={min}
        aria-valuemax={max}
        aria-valuenow={Number(value.toFixed(3))}
        aria-disabled={disabled}
        className="strudel-knob-face"
        style={style}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerEnd}
        onPointerCancel={onPointerEnd}
        onKeyDown={onKeyDown}
      >
        <span className="strudel-knob-marker" />
      </div>
      <output>{fmtNumber(value)}</output>
    </label>
  );
}

export function StrudelPanel(): JSX.Element {
  const hostRef = useRef<HTMLDivElement>(null);
  const editorRef = useRef<StrudelEditorElement | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const codeRef = useRef<string>(STARTER_CODE);
  const headingId = useId();

  const [options, setOptions] = useState<ComposerOptions | null>(null);
  const [optionsError, setOptionsError] = useState<string | null>(null);
  const [tonic, setTonic] = useState<string>("A");
  const [mode, setMode] = useState<string>("Eólico");
  const [length, setLength] = useState<number>(16);
  const [flavor, setFlavor] = useState<Flavor>("free");
  const [surface, setSurface] = useState<StrudelSurfaceControls>(DEFAULT_SURFACE);
  const [generation, setGeneration] = useState<StrudelGeneration | null>(null);
  const [code, setCode] = useState<string>(STARTER_CODE);
  const [codeMode, setCodeMode] = useState<CodeMode>("controlled");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [strudelPlaying, setStrudelPlaying] = useState<boolean>(false);
  const [pyTheoryPlaying, setPyTheoryPlaying] = useState<boolean>(false);

  const applyCode = useCallback((nextCode: string, mode: CodeMode): void => {
    codeRef.current = nextCode;
    setCode(nextCode);
    setCodeMode(mode);
    if (editorRef.current !== null) {
      loadEditorCode(editorRef.current, nextCode);
    }
  }, []);

  useEffect(() => {
    fetchOptions()
      .then((opts) => setOptions(opts))
      .catch((err: unknown) => setOptionsError(errorMessage(err)));
  }, []);

  useEffect(() => {
    const host = hostRef.current;
    if (host === null) return undefined;

    const editor = document.createElement("strudel-editor") as StrudelEditorElement;
    editor.className = "strudel-editor";
    editor.setAttribute("code", codeRef.current);
    editorRef.current = editor;
    host.replaceChildren(editor);

    function syncCode(): void {
      const nextCode = editor.editor?.code;
      if (typeof nextCode !== "string" || nextCode === codeRef.current) return;
      codeRef.current = nextCode;
      setCode(nextCode);
      setCodeMode("manual");
    }

    const intervalId = window.setInterval(syncCode, 400);
    host.addEventListener("keyup", syncCode, true);
    host.addEventListener("input", syncCode, true);
    host.addEventListener("paste", syncCode, true);
    host.addEventListener("blur", syncCode, true);

    return () => {
      window.clearInterval(intervalId);
      host.removeEventListener("keyup", syncCode, true);
      host.removeEventListener("input", syncCode, true);
      host.removeEventListener("paste", syncCode, true);
      host.removeEventListener("blur", syncCode, true);
      editor.editor?.stop?.();
      editor.editor?.clear?.();
      setStrudelPlaying(false);
      editorRef.current = null;
      host.replaceChildren();
    };
  }, []);

  const generate = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);
    audioRef.current?.pause();
    setPyTheoryPlaying(false);
    try {
      const result = await generateStrudel({ tonic, mode, length, flavor });
      setGeneration(result);
      applyCode(buildControlledCode(result, surface), "controlled");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [applyCode, tonic, mode, length, flavor, surface]);

  function updateSurface(patch: Partial<StrudelSurfaceControls>): void {
    const nextSurface = { ...surface, ...patch };
    setSurface(nextSurface);
    if (generation !== null) {
      applyCode(buildControlledCode(generation, nextSurface), "controlled");
    }
  }

  function restoreControlledCode(): void {
    if (generation === null) {
      applyCode(STARTER_CODE, "controlled");
      return;
    }
    applyCode(buildControlledCode(generation, surface), "controlled");
  }

  function playStrudelLoop(): void {
    void editorRef.current?.editor?.evaluate?.();
    setStrudelPlaying(true);
  }

  function stopStrudelLoop(): void {
    editorRef.current?.editor?.stop?.();
    setStrudelPlaying(false);
  }

  async function togglePyTheoryAudio(): Promise<void> {
    const audio = audioRef.current;
    if (audio === null) return;
    if (audio.paused) {
      try {
        await audio.play();
        setPyTheoryPlaying(true);
      } catch (err) {
        setError(`No pudimos iniciar PyTheory: ${errorMessage(err)}`);
      }
      return;
    }
    audio.pause();
    audio.currentTime = 0;
    setPyTheoryPlaying(false);
  }

  function submit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    void generate();
  }

  if (optionsError !== null) {
    return (
      <section className="strudel-panel" aria-labelledby={headingId}>
        <h2 id={headingId}>Strudel</h2>
        <p className="strudel-error">No pudimos cargar Strudel: {optionsError}</p>
      </section>
    );
  }

  return (
    <section className="strudel-panel" aria-labelledby={headingId}>
      <header className="strudel-header">
        <p className="strudel-kicker">Patrón en vivo</p>
        <h2 id={headingId}>Estudio Fractal</h2>
      </header>

      <p className="strudel-status" aria-live="polite">
        {loading ? "Componiendo y armando el patrón..." : ""}
      </p>

      {error !== null && (
        <p className="strudel-error">No pudimos continuar: {error}</p>
      )}

      <div className="strudel-studio">
        <section className="pytheory-panel" aria-label="Versión piano">
          <header className="surface-head">
            <p>Versión piano</p>
            <h3>Lo que compuso la rueda</h3>
          </header>

          <form className="pytheory-form" onSubmit={submit}>
            <label className="strudel-field">
              <span>Tónica</span>
              <select
                value={tonic}
                disabled={options === null || loading}
                onChange={(event) => setTonic(event.target.value)}
              >
                {(options?.tonics ?? [tonic]).map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </select>
            </label>

            <label className="strudel-field">
              <span>Modo</span>
              <select
                value={mode}
                disabled={options === null || loading}
                onChange={(event) => setMode(event.target.value)}
              >
                {(options?.modes ?? [mode]).map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </select>
            </label>

            <label className="strudel-field">
              <span>Notas</span>
              <input
                type="number"
                min={4}
                max={64}
                value={length}
                disabled={loading}
                onChange={(event) => setLength(numberFromInput(event.target.value, length, 4, 64))}
              />
            </label>

            <label className="strudel-field">
              <span>Estilo</span>
              <select
                value={flavor}
                disabled={options === null || loading}
                onChange={(event) => {
                  const value = event.target.value;
                  if (isFlavor(value)) setFlavor(value);
                }}
              >
                {(options?.flavors ?? [flavor]).map((value) => (
                  <option key={value} value={value}>
                    {FLAVOR_LABELS[value]}
                  </option>
                ))}
              </select>
            </label>

            <button type="submit" className="strudel-generate" disabled={loading}>
              {loading ? "Componiendo..." : "Componer patrón"}
            </button>
          </form>

          <div className="pytheory-transport" aria-label="Transporte de la versión piano">
            <button
              type="button"
              className="transport-button transport-button-primary"
              disabled={generation?.generated_from.audio_url == null}
              onClick={() => {
                void togglePyTheoryAudio();
              }}
            >
              {pyTheoryPlaying ? "■ Parar piano" : "▶ Tocar versión piano"}
            </button>
            <span>{generation === null ? "Sin patrón todavía" : `${generation.total_beats} pulsos`}</span>
          </div>

          {generation?.generated_from.audio_url !== null && generation !== null && (
            <audio
              ref={audioRef}
              className="strudel-audio-hidden"
              src={generation.generated_from.audio_url}
              preload="auto"
              onEnded={() => setPyTheoryPlaying(false)}
              onPause={() => setPyTheoryPlaying(false)}
              onPlay={() => setPyTheoryPlaying(true)}
            >
              Tu navegador no soporta el reproductor de audio.
            </audio>
          )}

          <div className="pytheory-context" aria-live="polite">
            {generation === null ? (
              <div className="strudel-empty">
                <h3>Patrón</h3>
                <p>
                  {options === null
                    ? "Cargando opciones..."
                    : `${tonic} ${mode} - ${length} notas`}
                </p>
              </div>
            ) : (
              <>
                <header className="strudel-result-head">
                  <h3>{generation.generated_from.key_label}</h3>
                  <span>{BAND_LABELS[generation.generated_from.confidence.band]}</span>
                </header>

                <dl className="strudel-facts">
                  <div>
                    <dt>Patrón</dt>
                    <dd>{generation.pattern_name}</dd>
                  </div>
                  <div>
                    <dt>Tempo</dt>
                    <dd>♩ = {generation.bpm}</dd>
                  </div>
                  <div>
                    <dt>Ciclo</dt>
                    <dd>{generation.total_beats} pulsos</dd>
                  </div>
                  <div>
                    <dt>Código</dt>
                    <dd>{codeMode === "controlled" ? "Sincronizado con la rueda" : "Editado a mano"}</dd>
                  </div>
                </dl>

                <div className="strudel-strip" role="list">
                  {generation.generated_from.events.map((event, index) => (
                    <span
                      key={`${event.beat}-${event.note}-${event.octave}-${index}`}
                      role="listitem"
                      className="strudel-note"
                      title={`${event.note}${event.octave} · hora ${event.role_hour} en la rueda · carta ${event.carta_glyph}`}
                    >
                      <span className="strudel-note-glyph">{event.carta_glyph}</span>
                      <span>
                        {event.note}
                        <sub>{event.octave}</sub>
                      </span>
                    </span>
                  ))}
                </div>

                <footer className="strudel-prov">
                  <span>{generation.generated_from.provenance.book_title}</span>
                  {generation.generated_from.provenance.chapter !== null && (
                    <span>{generation.generated_from.provenance.chapter}</span>
                  )}
                </footer>

                {generation.book_guidance.length > 0 && (
                  <section className="strudel-book-guidance" aria-label="Libro a Strudel">
                    <h4>Libro a Strudel</h4>
                    <ol>
                      {generation.book_guidance.map((guidance) => (
                        <li
                          key={`${guidance.book_hash}-${guidance.chapter_idx}-${guidance.section_idx}-${guidance.paragraph_idx}`}
                        >
                          <strong>{guidance.strudel_use}</strong>
                          <span>
                            {guidance.book_hash} · p.{guidance.page_start} · ch.
                            {guidance.chapter_idx}
                          </span>
                          <p>{guidance.snippet}</p>
                        </li>
                      ))}
                    </ol>
                  </section>
                )}

                {generation.warnings.length > 0 && (
                  <ul className="strudel-warnings">
                    {generation.warnings.map((warning) => (
                      <li key={warning}>{warning}</li>
                    ))}
                  </ul>
                )}
              </>
            )}
          </div>
        </section>

        <section className="strudel-live-panel" aria-label="Patrón en vivo">
          <header className="surface-head">
            <p>Patrón en vivo</p>
            <h3>Loop con batería y bajo</h3>
          </header>

          <div className="strudel-actions" aria-label="Transporte del patrón">
            <button type="button" className="transport-button transport-button-primary" onClick={playStrudelLoop}>
              {strudelPlaying ? "↻ Volver a tocar" : "▶ Tocar patrón"}
            </button>
            <button type="button" className="transport-button" onClick={stopStrudelLoop}>
              ■ Parar
            </button>
            <button type="button" className="transport-button" onClick={restoreControlledCode}>
              Restaurar al original
            </button>
          </div>

          <div className="strudel-control-groups">
            <section className="control-group">
              <header>
                <h4>Melodía</h4>
              </header>
              <div className="control-grid">
                <label className="strudel-field">
                  <span>Timbre</span>
                  <select
                    value={surface.voiceSound}
                    onChange={(event) => updateSurface({ voiceSound: event.target.value as StrudelSound })}
                  >
                    {SOUND_OPTIONS.map((value) => (
                      <option key={value} value={value}>
                        {SOUND_LABELS[value]}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="strudel-field">
                  <span>Velocidad</span>
                  <select
                    value={surface.speed}
                    onChange={(event) => updateSurface({
                      speed: numberFromInput(event.target.value, surface.speed, 0.5, 2),
                    })}
                  >
                    {SPEED_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
                <Knob
                  label="Volumen"
                  value={surface.voiceGain}
                  min={0}
                  max={1}
                  step={0.01}
                  onChange={(voiceGain) => updateSurface({ voiceGain })}
                />
                <Knob
                  label="Octava"
                  value={surface.octaveShift}
                  min={-3}
                  max={3}
                  step={1}
                  onChange={(octaveShift) => updateSurface({ octaveShift })}
                />
                <label className="strudel-check">
                  <input
                    type="checkbox"
                    checked={surface.filterEnabled}
                    onChange={(event) => updateSurface({ filterEnabled: event.target.checked })}
                  />
                  <span>Filtro</span>
                </label>
                <Knob
                  label="Frecuencia"
                  value={surface.filterCutoff}
                  min={200}
                  max={6000}
                  step={50}
                  disabled={!surface.filterEnabled}
                  onChange={(filterCutoff) => updateSurface({ filterCutoff })}
                />
                <Knob
                  label="Eco"
                  value={surface.delay}
                  min={0}
                  max={0.75}
                  step={0.01}
                  onChange={(delay) => updateSurface({ delay })}
                />
                <Knob
                  label="Sala"
                  value={surface.room}
                  min={0}
                  max={1}
                  step={0.01}
                  onChange={(room) => updateSurface({ room })}
                />
              </div>
            </section>

            <section className="control-group">
              <header>
                <h4>Bordón y bajo</h4>
              </header>
              <div className="control-grid">
                <label className="strudel-check">
                  <input
                    type="checkbox"
                    checked={surface.droneEnabled}
                    onChange={(event) => updateSurface({ droneEnabled: event.target.checked })}
                  />
                  <span>Bordón</span>
                </label>
                <label className="strudel-field">
                  <span>Timbre del bordón</span>
                  <select
                    value={surface.droneSound}
                    disabled={!surface.droneEnabled}
                    onChange={(event) => updateSurface({ droneSound: event.target.value as StrudelSound })}
                  >
                    {SOUND_OPTIONS.map((value) => (
                      <option key={value} value={value}>
                        {SOUND_LABELS[value]}
                      </option>
                    ))}
                  </select>
                </label>
                <Knob
                  label="Octava del bordón"
                  value={surface.droneOctave}
                  min={0}
                  max={5}
                  step={1}
                  disabled={!surface.droneEnabled}
                  onChange={(droneOctave) => updateSurface({ droneOctave })}
                />
                <Knob
                  label="Volumen del bordón"
                  value={surface.droneGain}
                  min={0}
                  max={1}
                  step={0.01}
                  disabled={!surface.droneEnabled}
                  onChange={(droneGain) => updateSurface({ droneGain })}
                />
                <label className="strudel-check">
                  <input
                    type="checkbox"
                    checked={surface.bassEnabled}
                    onChange={(event) => updateSurface({ bassEnabled: event.target.checked })}
                  />
                  <span>Bajo</span>
                </label>
                <label className="strudel-field">
                  <span>Patrón del bajo</span>
                  <select
                    value={surface.bassPattern}
                    disabled={!surface.bassEnabled}
                    onChange={(event) => updateSurface({ bassPattern: event.target.value as BassPattern })}
                  >
                    <option value="root">{BASS_LABELS.root}</option>
                    <option value="walk">{BASS_LABELS.walk}</option>
                    <option value="octaves">{BASS_LABELS.octaves}</option>
                  </select>
                </label>
                <label className="strudel-field">
                  <span>Timbre del bajo</span>
                  <select
                    value={surface.bassSound}
                    disabled={!surface.bassEnabled}
                    onChange={(event) => updateSurface({ bassSound: event.target.value as StrudelSound })}
                  >
                    {SOUND_OPTIONS.map((value) => (
                      <option key={value} value={value}>
                        {SOUND_LABELS[value]}
                      </option>
                    ))}
                  </select>
                </label>
                <Knob
                  label="Volumen del bajo"
                  value={surface.bassGain}
                  min={0}
                  max={1}
                  step={0.01}
                  disabled={!surface.bassEnabled}
                  onChange={(bassGain) => updateSurface({ bassGain })}
                />
                <Knob
                  label="Filtro del bajo"
                  value={surface.bassCutoff}
                  min={120}
                  max={2000}
                  step={20}
                  disabled={!surface.bassEnabled}
                  onChange={(bassCutoff) => updateSurface({ bassCutoff })}
                />
              </div>
            </section>

            <section className="control-group">
              <header>
                <h4>Batería y remates</h4>
              </header>
              <div className="control-grid">
                <label className="strudel-check">
                  <input
                    type="checkbox"
                    checked={surface.drumsEnabled}
                    onChange={(event) => updateSurface({ drumsEnabled: event.target.checked })}
                  />
                  <span>Batería</span>
                </label>
                <label className="strudel-field">
                  <span>Set de batería</span>
                  <select
                    value={surface.drumBank}
                    disabled={!surface.drumsEnabled}
                    onChange={(event) => updateSurface({ drumBank: event.target.value as DrumBank })}
                  >
                    {DRUM_BANK_OPTIONS.map((value) => (
                      <option key={value} value={value}>
                        {value.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="strudel-check">
                  <input
                    type="checkbox"
                    checked={surface.kickEnabled}
                    disabled={!surface.drumsEnabled}
                    onChange={(event) => updateSurface({ kickEnabled: event.target.checked })}
                  />
                  <span>Bombo</span>
                </label>
                <label className="strudel-field">
                  <span>Patrón del bombo</span>
                  <select
                    value={surface.kickPattern}
                    disabled={!surface.drumsEnabled || !surface.kickEnabled}
                    onChange={(event) => updateSurface({ kickPattern: event.target.value as KickPattern })}
                  >
                    <option value="four">{KICK_LABELS.four}</option>
                    <option value="half">{KICK_LABELS.half}</option>
                    <option value="syncopated">{KICK_LABELS.syncopated}</option>
                    <option value="euclid">{KICK_LABELS.euclid}</option>
                  </select>
                </label>
                <Knob
                  label="Volumen del bombo"
                  value={surface.kickGain}
                  min={0}
                  max={1}
                  step={0.01}
                  disabled={!surface.drumsEnabled || !surface.kickEnabled}
                  onChange={(kickGain) => updateSurface({ kickGain })}
                />
                <label className="strudel-check">
                  <input
                    type="checkbox"
                    checked={surface.snareEnabled}
                    disabled={!surface.drumsEnabled}
                    onChange={(event) => updateSurface({ snareEnabled: event.target.checked })}
                  />
                  <span>Caja</span>
                </label>
                <label className="strudel-field">
                  <span>Patrón de la caja</span>
                  <select
                    value={surface.snarePattern}
                    disabled={!surface.drumsEnabled || !surface.snareEnabled}
                    onChange={(event) => updateSurface({ snarePattern: event.target.value as SnarePattern })}
                  >
                    <option value="backbeat">{SNARE_LABELS.backbeat}</option>
                    <option value="clap">{SNARE_LABELS.clap}</option>
                    <option value="four">{SNARE_LABELS.four}</option>
                    <option value="offbeat">{SNARE_LABELS.offbeat}</option>
                  </select>
                </label>
                <Knob
                  label="Volumen de la caja"
                  value={surface.snareGain}
                  min={0}
                  max={1}
                  step={0.01}
                  disabled={!surface.drumsEnabled || !surface.snareEnabled}
                  onChange={(snareGain) => updateSurface({ snareGain })}
                />
                <label className="strudel-check">
                  <input
                    type="checkbox"
                    checked={surface.hatsEnabled}
                    disabled={!surface.drumsEnabled}
                    onChange={(event) => updateSurface({ hatsEnabled: event.target.checked })}
                  />
                  <span>Hi-hat</span>
                </label>
                <label className="strudel-field">
                  <span>Patrón del hi-hat</span>
                  <select
                    value={surface.hatPattern}
                    disabled={!surface.drumsEnabled || !surface.hatsEnabled}
                    onChange={(event) => updateSurface({ hatPattern: event.target.value as HatPattern })}
                  >
                    <option value="eighth">{HAT_LABELS.eighth}</option>
                    <option value="sixteenth">{HAT_LABELS.sixteenth}</option>
                    <option value="skip">{HAT_LABELS.skip}</option>
                    <option value="open">{HAT_LABELS.open}</option>
                  </select>
                </label>
                <Knob
                  label="Volumen del hi-hat"
                  value={surface.hatGain}
                  min={0}
                  max={1}
                  step={0.01}
                  disabled={!surface.drumsEnabled || !surface.hatsEnabled}
                  onChange={(hatGain) => updateSurface({ hatGain })}
                />
                <label className="strudel-field">
                  <span>Remate</span>
                  <select
                    value={surface.fillPattern}
                    disabled={!surface.drumsEnabled}
                    onChange={(event) => updateSurface({ fillPattern: event.target.value as FillPattern })}
                  >
                    <option value="none">{FILL_LABELS.none}</option>
                    <option value="clap-drop">{FILL_LABELS["clap-drop"]}</option>
                    <option value="tom-run">{FILL_LABELS["tom-run"]}</option>
                    <option value="snare-roll">{FILL_LABELS["snare-roll"]}</option>
                  </select>
                </label>
                <Knob
                  label="Volumen del remate"
                  value={surface.fillGain}
                  min={0}
                  max={1}
                  step={0.01}
                  disabled={!surface.drumsEnabled || surface.fillPattern === "none"}
                  onChange={(fillGain) => updateSurface({ fillGain })}
                />
                <Knob
                  label="Sala de la batería"
                  value={surface.drumRoom}
                  min={0}
                  max={1}
                  step={0.01}
                  disabled={!surface.drumsEnabled}
                  onChange={(drumRoom) => updateSurface({ drumRoom })}
                />
                <Knob
                  label="Eco de la batería"
                  value={surface.drumDelay}
                  min={0}
                  max={0.75}
                  step={0.01}
                  disabled={!surface.drumsEnabled}
                  onChange={(drumDelay) => updateSurface({ drumDelay })}
                />
                <Knob
                  label="Swing"
                  value={surface.swing}
                  min={0}
                  max={0.33}
                  step={0.01}
                  disabled={!surface.drumsEnabled}
                  onChange={(swing) => updateSurface({ swing })}
                />
              </div>
            </section>
          </div>

          <div
            ref={hostRef}
            className="strudel-editor-host"
            aria-label="Editor de Strudel"
            data-code-length={code.length}
          />
        </section>
      </div>
    </section>
  );
}
