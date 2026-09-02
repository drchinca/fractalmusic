// Pure Strudel pattern-code generation — turns a GeneratedPayload plus the
// live mixing-surface controls into an actual Strudel code string. No React,
// no DOM; StrudelPanel.tsx renders the surface and feeds it these builders.

import { GenerateError } from "../composer/api";
import type { Flavor } from "../composer/types";
import type { StrudelGeneration } from "./api";

export const STARTER_CODE = `setcps(0.75)

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

export const FLAVOR_LABELS: Record<Flavor, string> = {
  free: "Libre",
  "penta-walk": "Paseo pentatónico",
  "carta-progression": "Progresión de cartas",
};

export const BAND_LABELS: Record<"strong" | "tentative" | "exploratory", string> = {
  strong: "Fiel al libro",
  tentative: "Inspirado en el libro",
  exploratory: "Exploración libre",
};

export const SOUND_LABELS: Record<"sine" | "triangle" | "sawtooth" | "square", string> = {
  sine: "Senoidal",
  triangle: "Triángulo",
  sawtooth: "Sierra",
  square: "Cuadrada",
};

export const BASS_LABELS: Record<"root" | "walk" | "octaves", string> = {
  root: "Tónica",
  walk: "Caminado",
  octaves: "Octavas",
};

export const KICK_LABELS: Record<"four" | "half" | "syncopated" | "euclid", string> = {
  four: "Cuatro al piso",
  half: "A medias",
  syncopated: "Sincopado",
  euclid: "Euclídeo",
};

export const SNARE_LABELS: Record<"backbeat" | "clap" | "four" | "offbeat", string> = {
  backbeat: "Contratiempo",
  clap: "Palmas",
  four: "Cuatro pulsos",
  offbeat: "Fuera del pulso",
};

export const HAT_LABELS: Record<"eighth" | "sixteenth" | "skip" | "open", string> = {
  eighth: "Corcheas",
  sixteenth: "Semicorcheas",
  skip: "Saltado",
  open: "Abierto",
};

export const FILL_LABELS: Record<"none" | "clap-drop" | "tom-run" | "snare-roll", string> = {
  none: "Sin remate",
  "clap-drop": "Bajón con palma",
  "tom-run": "Vuelta de toms",
  "snare-roll": "Redoble de caja",
};

export type StrudelSound = "sine" | "triangle" | "sawtooth" | "square";
export type DrumBank = "tr808" | "tr909" | "tr707";
export type KickPattern = "four" | "half" | "syncopated" | "euclid";
export type SnarePattern = "backbeat" | "clap" | "four" | "offbeat";
export type HatPattern = "eighth" | "sixteenth" | "skip" | "open";
export type FillPattern = "none" | "clap-drop" | "tom-run" | "snare-roll";
export type BassPattern = "root" | "walk" | "octaves";
export type SurfaceSection = "melody" | "bass" | "drums";

export interface StrudelSurfaceControls {
  voiceSound: StrudelSound;
  voiceGain: number;
  octaveShift: number;
  speed: number;
  voiceAttack: number;
  voiceRelease: number;
  voicePan: number;
  voiceShape: number;
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
  bassPan: number;
  bassShape: number;
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
  drumShape: number;
  swing: number;
}

export const SOUND_OPTIONS: readonly StrudelSound[] = ["triangle", "sine", "sawtooth", "square"];
export const DRUM_BANK_OPTIONS: readonly DrumBank[] = ["tr909", "tr808", "tr707"];

export const SPEED_OPTIONS: readonly { label: string; value: number }[] = [
  { label: "1/2", value: 0.5 },
  { label: "1", value: 1 },
  { label: "3/2", value: 1.5 },
  { label: "2", value: 2 },
];

export const SURFACE_SECTIONS: readonly { id: SurfaceSection; label: string }[] = [
  { id: "melody", label: "Melodía" },
  { id: "bass", label: "Bajo" },
  { id: "drums", label: "Batería" },
];

export const KICK_PATTERNS: Record<KickPattern, string> = {
  four: "bd*4",
  half: "bd ~ bd ~",
  syncopated: "bd [~ bd] ~ bd",
  euclid: "bd(5,8)",
};

export const SNARE_PATTERNS: Record<SnarePattern, string> = {
  backbeat: "~ sd ~ sd",
  clap: "~ cp ~ cp",
  four: "sd*4",
  offbeat: "~ ~ sd [~ cp]",
};

export const HAT_PATTERNS: Record<HatPattern, string> = {
  eighth: "hh*8",
  sixteenth: "hh*16",
  skip: "[hh ~]*4",
  open: "hh*6 [oh hh]",
};

export const FILL_PATTERNS: Record<FillPattern, string | null> = {
  none: null,
  "clap-drop": "~ ~ ~ [cp sd]",
  "tom-run": "~ ~ [lt mt] [ht cp]",
  "snare-roll": "~ ~ sd*4 cp",
};

export const DEFAULT_SURFACE: StrudelSurfaceControls = {
  voiceSound: "triangle",
  voiceGain: 0.22,
  octaveShift: 0,
  speed: 1,
  voiceAttack: 0.01,
  voiceRelease: 0.18,
  voicePan: 0.5,
  voiceShape: 0,
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
  bassPan: 0.5,
  bassShape: 0,
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
  drumShape: 0.05,
  swing: 0,
};

export const PATCH_PRESETS: readonly {
  id: string;
  label: string;
  patch: Partial<StrudelSurfaceControls>;
}[] = [
  {
    id: "fractal",
    label: "Fractal",
    patch: {
      voiceSound: "triangle",
      voiceGain: 0.22,
      voiceAttack: 0.01,
      voiceRelease: 0.18,
      voiceShape: 0,
      delay: 0,
      room: 0.12,
      bassEnabled: true,
      bassPattern: "root",
      drumsEnabled: false,
    },
  },
  {
    id: "club",
    label: "Club",
    patch: {
      voiceSound: "sawtooth",
      voiceGain: 0.25,
      voiceAttack: 0,
      voiceRelease: 0.12,
      voiceShape: 0.08,
      filterEnabled: true,
      filterCutoff: 1400,
      bassEnabled: true,
      bassPattern: "walk",
      bassGain: 0.22,
      drumsEnabled: true,
      kickPattern: "four",
      snarePattern: "backbeat",
      hatPattern: "sixteenth",
      fillPattern: "clap-drop",
      drumShape: 0.1,
    },
  },
  {
    id: "dub",
    label: "Dub",
    patch: {
      voiceSound: "sine",
      voiceGain: 0.18,
      voiceAttack: 0.03,
      voiceRelease: 0.42,
      delay: 0.38,
      room: 0.55,
      bassEnabled: true,
      bassPattern: "octaves",
      bassGain: 0.2,
      drumDelay: 0.18,
      drumRoom: 0.35,
      swing: 0.08,
    },
  },
  {
    id: "break",
    label: "Break",
    patch: {
      voiceSound: "square",
      voiceGain: 0.16,
      speed: 1.5,
      bassEnabled: true,
      bassPattern: "walk",
      drumsEnabled: true,
      kickPattern: "syncopated",
      snarePattern: "offbeat",
      hatPattern: "open",
      fillPattern: "snare-roll",
      drumShape: 0.18,
      swing: 0.14,
    },
  },
];

export function errorMessage(err: unknown): string {
  if (err instanceof GenerateError) return err.message;
  return err instanceof Error ? err.message : String(err);
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

export function stepValue(value: number, min: number, max: number, step: number): number {
  const stepped = Math.round((clamp(value, min, max) - min) / step) * step + min;
  return Number(clamp(stepped, min, max).toFixed(4));
}

export function numberFromInput(value: string, fallback: number, min: number, max: number): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return clamp(parsed, min, max);
}

export function fmtNumber(value: number): string {
  if (Number.isInteger(value)) return String(value);
  return value.toFixed(3).replace(/0+$/, "").replace(/\.$/, "");
}

export function commentText(value: string, limit = 120): string {
  return value.replace(/[\r\n]+/g, " ").replace(/\s+/g, " ").trim().slice(0, limit);
}

export function shiftedNote(note: string, octave: number, shift: number): string {
  return `${note.toLowerCase()}${clamp(octave + shift, 0, 8)}`;
}

export function bassNotes(generation: StrudelGeneration, controls: StrudelSurfaceControls): string {
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

export function starterBassNotes(controls: StrudelSurfaceControls): string {
  if (controls.bassPattern === "root") return "a1*4";
  if (controls.bassPattern === "octaves") return "a1 a2";
  return "a1 c2 d2 e2 a1 c2 d2 e2";
}

export function drumLayer(pattern: string, controls: StrudelSurfaceControls, gain: number): string {
  const lines = [
    `  s("${pattern}")`,
    `    .bank("${controls.drumBank}")`,
    `    .gain(${fmtNumber(gain)})`,
  ];
  if (controls.drumShape > 0) {
    lines.push(`    .shape(${fmtNumber(controls.drumShape)})`);
  }
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

export function starterDrumLayers(controls: StrudelSurfaceControls): string[] {
  const layers: string[] = [];
  if (!controls.drumsEnabled) return layers;
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
  return layers;
}

export function melodyLayer(notes: string, controls: StrudelSurfaceControls): string {
  const lines = [
    `  note("${notes}")`,
    `    .sound("${controls.voiceSound}")`,
    `    .gain(${fmtNumber(controls.voiceGain)})`,
    `    .attack(${fmtNumber(controls.voiceAttack)})`,
    `    .release(${fmtNumber(controls.voiceRelease)})`,
    `    .pan(${fmtNumber(controls.voicePan)})`,
  ];
  if (controls.voiceShape > 0) {
    lines.push(`    .shape(${fmtNumber(controls.voiceShape)})`);
  }
  if (controls.filterEnabled) {
    lines.push(`    .lpf(${fmtNumber(controls.filterCutoff)})`);
  }
  if (controls.delay > 0) {
    lines.push(`    .delay(${fmtNumber(controls.delay)})`);
  }
  if (controls.room > 0) {
    lines.push(`    .room(${fmtNumber(controls.room)})`);
  }
  return lines.join("\n");
}

export function buildStarterCode(controls: StrudelSurfaceControls): string {
  const cycle = 16;
  const speed = fmtNumber(controls.speed);
  const starterNotes = [
    shiftedNote("A", 4, controls.octaveShift),
    shiftedNote("C", 5, controls.octaveShift),
    shiftedNote("E", 5, controls.octaveShift),
    shiftedNote("A", 5, controls.octaveShift),
  ].join(" ");
  const layers = [melodyLayer(starterNotes, controls)];

  if (controls.droneEnabled) {
    layers.push(
      [
        `  note("a${controls.droneOctave}")`,
        `    .sound("${controls.droneSound}")`,
        `    .slow(${cycle})`,
        `    .gain(${fmtNumber(controls.droneGain)})`,
      ].join("\n"),
    );
  }
  if (controls.bassEnabled) {
    layers.push(
      [
        `  note("${starterBassNotes(controls)}")`,
        `    .sound("${controls.bassSound}")`,
        `    .lpf(${fmtNumber(controls.bassCutoff)})`,
        `    .gain(${fmtNumber(controls.bassGain)})`,
        `    .pan(${fmtNumber(controls.bassPan)})`,
        ...(controls.bassShape > 0 ? [`    .shape(${fmtNumber(controls.bassShape)})`] : []),
      ].join("\n"),
    );
  }

  return [
    "// Fractal Music: preview",
    "// key: A Eolico",
    `// surface: voice=${controls.voiceSound} speed=${speed} octave=${controls.octaveShift} bank=${controls.drumBank}`,
    `setcps(96 / 60 / ${cycle} * ${speed})`,
    "",
    "stack(",
    [...layers, ...starterDrumLayers(controls)].join(",\n"),
    ")",
  ].join("\n");
}

export function buildControlledCode(
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

  const layers = [melodyLayer(notes, controls)];
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
        `    .pan(${fmtNumber(controls.bassPan)})`,
        ...(controls.bassShape > 0 ? [`    .shape(${fmtNumber(controls.bassShape)})`] : []),
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
