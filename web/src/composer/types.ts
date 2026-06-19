// Mirror of fractalmusic.generate.WebPayload. FE never derives notes/freqs.

export interface GeneratedEvent {
  note: string;
  octave: number;
  beat: number;
  duration: number;
  time_sec: number;
  freq_hz: number;
  role_hour: number;
  carta_glyph: string;
}

export interface GeneratedProvenance {
  book_hash: string;
  book_title: string;
  chapter: string | null;
  page: number | null;
  quote: string | null;
}

export interface GeneratedPayload {
  schema_version: number;
  pattern_name: string;
  bpm: number;
  tonic: string;
  mode: string;
  key_label: string;
  total_beats: number;
  requires_user_gesture: boolean;
  confidence: { score: number; band: "strong" | "tentative" | "exploratory" };
  events: GeneratedEvent[];
  provenance: GeneratedProvenance;
  audio_url: string | null;
}

export type Flavor = "free" | "penta-walk" | "carta-progression";
export const FLAVOR_VALUES: readonly Flavor[] = ["free", "penta-walk", "carta-progression"];

export function isFlavor(value: string): value is Flavor {
  return (FLAVOR_VALUES as readonly string[]).includes(value);
}

export interface GenerateRequest {
  tonic: string;
  mode: string;
  length: number;
  flavor: Flavor;
}

export interface ComposerOptions {
  tonics: readonly string[];
  modes: readonly string[];
  flavors: readonly Flavor[];
}
