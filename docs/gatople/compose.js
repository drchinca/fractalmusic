// Composition / improvisation page — walks a progression from progressions.json
// and tells the player which scale to solo in at each step. Reuses the static
// renderers (outer disc, piano, fretboard) from app.js's primitives via lib.js.

import {
  SVG_NS,
  SEG_DEG,
  RING_OUTER,
  NOTE_RADIUS,
  NOTE_DISC_R,
  GUITAR_TUNING,
  FRET_COUNT,
  FRET_W,
  STRING_H,
  FRET_PAD_LEFT,
  WHITE_INDICES,
  BLACK_INDICES,
  BLACK_LOWER,
  polar,
  clockAngle,
  arcPath,
  indexOfNote,
  displayNote,
  roleAtNote,
} from "./lib.js";
import { createAudioEngine } from "./audio.js";

const RING_INNER = 165;
const RING_MID = (RING_OUTER + RING_INNER) / 2;

// --- Outer disc (clock-hour layout, role glyphs) ---

function renderOuter(svgGroup, roles) {
  for (const role of roles) {
    const angle = clockAngle(role.clock_hour);
    const start = angle - SEG_DEG / 2;
    const end = angle + SEG_DEG / 2;
    const seg = document.createElementNS(SVG_NS, "path");
    seg.setAttribute("d", arcPath(start, end, RING_OUTER, RING_INNER));
    seg.setAttribute("fill", role.wheel_color);
    seg.setAttribute("class", "role-segment");
    seg.dataset.mode = role.mode_name;
    svgGroup.appendChild(seg);

    const [gx, gy] = polar(angle, RING_MID);
    const glyph = document.createElementNS(SVG_NS, "text");
    glyph.setAttribute("class", "role-glyph");
    glyph.setAttribute("x", gx);
    glyph.setAttribute("y", gy);
    glyph.setAttribute("fill", role.glyph_fg);
    glyph.textContent = role.display_glyph;
    svgGroup.appendChild(glyph);
  }
}

// --- Inner disc (note labels at clock positions) ---

function renderInner(group, roles) {
  for (const role of roles) {
    const angle = clockAngle(role.clock_hour);
    const [x, y] = polar(angle, NOTE_RADIUS);
    const item = document.createElementNS(SVG_NS, "g");
    item.setAttribute("class", "note-item");
    item.setAttribute("transform", `translate(${x} ${y})`);
    const disc = document.createElementNS(SVG_NS, "circle");
    disc.setAttribute("class", "note-disc");
    disc.setAttribute("r", NOTE_DISC_R);
    const label = document.createElementNS(SVG_NS, "text");
    label.setAttribute("class", "note-label");
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("dominant-baseline", "central");
    label.textContent = displayNote(role.note_default);
    item.appendChild(disc);
    item.appendChild(label);
    group.appendChild(item);
  }
}

// --- Next-step arrow on the wheel ---

function drawNextArrow(svg, fromRole, toRole) {
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  if (!fromRole || !toRole || fromRole === toRole) return;

  const fromAngle = clockAngle(fromRole.clock_hour);
  const toAngle = clockAngle(toRole.clock_hour);
  const r = NOTE_RADIUS - 35;
  const [x1, y1] = polar(fromAngle, r);
  const [x2, y2] = polar(toAngle, r);

  // Curved path between the two role positions, anchored by the wheel center.
  const path = document.createElementNS(SVG_NS, "path");
  const sweep = ((toAngle - fromAngle + 360) % 360) > 180 ? 0 : 1;
  path.setAttribute(
    "d",
    `M ${x1.toFixed(1)} ${y1.toFixed(1)} A ${r} ${r} 0 0 ${sweep} ${x2.toFixed(1)} ${y2.toFixed(1)}`,
  );
  path.setAttribute("class", "next-arrow");
  svg.appendChild(path);

  // Arrowhead — small triangle at toAngle, pointing tangentially to the curve.
  const tangent = sweep === 1 ? toAngle - 80 : toAngle + 80;
  const [tx, ty] = polar(tangent, 10);
  const head = document.createElementNS(SVG_NS, "polygon");
  head.setAttribute(
    "points",
    `${x2.toFixed(1)},${y2.toFixed(1)} ${(x2 + tx).toFixed(1)},${(y2 + ty).toFixed(1)} ${
      (x2 + tx * 0.4 + (tx > 0 ? -ty : ty) * 0.4).toFixed(1)
    },${(y2 + ty * 0.4 + (tx > 0 ? tx : -tx) * 0.4).toFixed(1)}`,
  );
  head.setAttribute("class", "next-arrow-head");
  svg.appendChild(head);
}

// --- Piano + fretboard with in-scale highlighting ---

const PIANO_W = 560;
const PIANO_H = 180;

function renderPiano(svg, chromatic) {
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  const whiteW = PIANO_W / WHITE_INDICES.length;
  const blackW = whiteW * 0.62;
  const blackH = PIANO_H * 0.6;
  const whiteCol = {};
  WHITE_INDICES.forEach((idx, col) => { whiteCol[idx] = col; });

  for (const idx of WHITE_INDICES) {
    const x = whiteCol[idx] * whiteW;
    const note = chromatic[idx];
    const g = document.createElementNS(SVG_NS, "g");
    g.setAttribute("class", "piano-key piano-white");
    g.dataset.note = note;
    g.innerHTML = `
      <rect x="${x}" y="0" width="${whiteW}" height="${PIANO_H}" fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
      <rect class="piano-tint" x="${x + 4}" y="${PIANO_H - 70}" width="${whiteW - 8}" height="60" rx="4" stroke="#1a1a1a" stroke-width="1"/>
      <text class="piano-glyph" x="${x + whiteW / 2}" y="${PIANO_H - 50}" text-anchor="middle" dominant-baseline="central" font-size="20" font-weight="700"></text>
      <text class="piano-note" x="${x + whiteW / 2}" y="${PIANO_H - 22}" text-anchor="middle" font-size="13"></text>`;
    svg.appendChild(g);
  }
  for (const idx of BLACK_INDICES) {
    const x = whiteCol[BLACK_LOWER[idx]] * whiteW + whiteW - blackW / 2;
    const note = chromatic[idx];
    const g = document.createElementNS(SVG_NS, "g");
    g.setAttribute("class", "piano-key piano-black");
    g.dataset.note = note;
    g.innerHTML = `
      <rect x="${x}" y="0" width="${blackW}" height="${blackH}" fill="#0a0a0a"/>
      <rect class="piano-tint" x="${x + 3}" y="${blackH - 50}" width="${blackW - 6}" height="42" rx="4" stroke="#fff" stroke-width="1"/>
      <text class="piano-glyph" x="${x + blackW / 2}" y="${blackH - 32}" text-anchor="middle" dominant-baseline="central" font-size="14" fill="#fff"></text>
      <text class="piano-note" x="${x + blackW / 2}" y="${blackH - 13}" text-anchor="middle" font-size="10" fill="#fff"></text>`;
    svg.appendChild(g);
  }
}

function renderFretboard(svg, chromatic) {
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  const rows = GUITAR_TUNING.length;
  const bg = document.createElementNS(SVG_NS, "rect");
  bg.setAttribute("x", 0); bg.setAttribute("y", 0);
  bg.setAttribute("width", FRET_PAD_LEFT + FRET_COUNT * FRET_W);
  bg.setAttribute("height", rows * STRING_H + 22);
  bg.setAttribute("fill", "#fffaf1");
  svg.appendChild(bg);

  for (let f = 0; f <= FRET_COUNT; f++) {
    const x = FRET_PAD_LEFT + f * FRET_W;
    const wire = document.createElementNS(SVG_NS, "line");
    wire.setAttribute("x1", x); wire.setAttribute("x2", x);
    wire.setAttribute("y1", 0); wire.setAttribute("y2", rows * STRING_H);
    wire.setAttribute("stroke", "#1a1a1a");
    wire.setAttribute("stroke-width", f === 0 ? 3 : 1.5);
    svg.appendChild(wire);
    if (f > 0) {
      const num = document.createElementNS(SVG_NS, "text");
      num.setAttribute("x", x - FRET_W / 2);
      num.setAttribute("y", rows * STRING_H + 16);
      num.setAttribute("text-anchor", "middle");
      num.setAttribute("font-size", "12");
      num.setAttribute("fill", "#444");
      num.textContent = f;
      svg.appendChild(num);
    }
  }

  const strings = [...GUITAR_TUNING].reverse();
  for (let s = 0; s < strings.length; s++) {
    const baseIdx = chromatic.indexOf(strings[s]);
    for (let f = 0; f <= FRET_COUNT; f++) {
      const chromIdx = (baseIdx + f) % 12;
      const note = chromatic[chromIdx];
      const x = f === 0 ? 0 : FRET_PAD_LEFT + (f - 1) * FRET_W;
      const w = f === 0 ? FRET_PAD_LEFT : FRET_W;
      const y = s * STRING_H;
      const g = document.createElementNS(SVG_NS, "g");
      g.setAttribute("class", "fret-cell");
      g.dataset.note = note;
      g.innerHTML = `
        <rect class="fret-tint" x="${x + 4}" y="${y + 4}" width="${w - 8}" height="${STRING_H - 8}" rx="4" stroke="#1a1a1a" stroke-width="1"/>
        <text class="fret-glyph" x="${x + w / 2}" y="${y + STRING_H / 2 - 4}" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700"></text>
        <text class="fret-label" x="${x + w / 2}" y="${y + STRING_H - 8}" text-anchor="middle" font-size="10" fill="#444"></text>`;
      svg.appendChild(g);
    }
  }
}

function repaintInstruments(piano, fretboard, roles, chromatic, scaleNotes) {
  const inScale = new Set(scaleNotes);
  for (const key of piano.querySelectorAll(".piano-key")) {
    const note = key.dataset.note;
    const role = roleAtNote(note, roles, 0, chromatic);
    if (!role) continue;
    const tint = key.querySelector(".piano-tint");
    const glyph = key.querySelector(".piano-glyph");
    const label = key.querySelector(".piano-note");
    tint.setAttribute("fill", role.carta_color);
    glyph.textContent = role.display_glyph;
    label.textContent = displayNote(note);
    key.classList.toggle("in-scale", inScale.has(note));
  }
  for (const cell of fretboard.querySelectorAll(".fret-cell")) {
    const note = cell.dataset.note;
    const role = roleAtNote(note, roles, 0, chromatic);
    if (!role) continue;
    const tint = cell.querySelector(".fret-tint");
    const glyph = cell.querySelector(".fret-glyph");
    const label = cell.querySelector(".fret-label");
    tint.setAttribute("fill", role.carta_color);
    glyph.textContent = role.display_glyph;
    label.textContent = displayNote(note);
    cell.classList.toggle("in-scale", inScale.has(note));
  }
}

// --- Drone synth ---

class Drone {
  constructor() {
    this.ctx = null;
    this.osc = null;
    this.env = null;
    this.currentNote = null;
  }

  start(note, octave, audioCtx) {
    if (!this.ctx) this.ctx = audioCtx;
    if (!this.ctx) return;
    if (this.currentNote === `${note}${octave}`) return;
    this.stop();

    const sciIndex = { C: 0, "C#": 1, D: 2, "D#": 3, E: 4, F: 5, "F#": 6,
                       G: 7, "G#": 8, A: 9, "A#": 10, B: 11 };
    const enharmonic = { Bb: "A#", Db: "C#", Eb: "D#", Gb: "F#", Ab: "G#" };
    const idx = sciIndex[enharmonic[note] ?? note];
    if (idx === undefined) return;
    const semitonesFromA4 = (octave - 4) * 12 + (idx - 9);
    const freq = 440 * 2 ** (semitonesFromA4 / 12);

    this.osc = this.ctx.createOscillator();
    this.env = this.ctx.createGain();
    this.osc.type = "sine";
    this.osc.frequency.value = freq;
    this.osc.connect(this.env);
    this.env.connect(this.ctx.destination);
    this.env.gain.setValueAtTime(0.0001, this.ctx.currentTime);
    this.env.gain.exponentialRampToValueAtTime(0.05, this.ctx.currentTime + 0.4);
    this.osc.start();
    this.currentNote = `${note}${octave}`;
  }

  stop() {
    if (!this.osc || !this.env || !this.ctx) return;
    const now = this.ctx.currentTime;
    this.env.gain.cancelScheduledValues(now);
    this.env.gain.setValueAtTime(this.env.gain.value, now);
    this.env.gain.exponentialRampToValueAtTime(0.0001, now + 0.3);
    this.osc.stop(now + 0.35);
    this.osc = null;
    this.env = null;
    this.currentNote = null;
  }
}

// --- Scale notes from a step ---

function scaleNotesFor(step, roles, chromatic) {
  // step.improvise_in is e.g. "A Eólico", "D# Penta 2".
  const match = step.improvise_in.match(/^([A-G][#b]?)\s+(.+)$/);
  if (!match) return [];
  const tonic = match[1];
  const modeName = match[2];
  const role = roles.find((r) => r.mode_name === modeName);
  if (!role) return [];
  const tonicIdx = indexOfNote(tonic, chromatic);
  if (tonicIdx < 0) return [];
  const out = [chromatic[tonicIdx]];
  let idx = tonicIdx;
  for (const stepSemi of role.scale_steps.slice(0, -1)) {
    idx = (idx + stepSemi) % 12;
    out.push(chromatic[idx]);
  }
  return out;
}

function tonicOf(step) {
  const match = step.improvise_in.match(/^([A-G][#b]?)\s+/);
  return match ? match[1] : "A";
}

// --- Main ---

async function main() {
  const [data, progData] = await Promise.all([
    fetch("data.json").then((r) => r.json()),
    fetch("progressions.json").then((r) => r.json()),
  ]);
  const { chromatic, roles } = data;
  const { progressions } = progData;

  const outer = document.getElementById("outer-disc");
  const inner = document.getElementById("inner-disc");
  const arrowLayer = document.getElementById("next-arrow-layer");
  const piano = document.getElementById("piano");
  const fretboard = document.getElementById("fretboard");

  renderOuter(outer, roles);
  renderInner(inner, roles);
  renderPiano(piano, chromatic);
  renderFretboard(fretboard, chromatic);

  // Progression list.
  const list = document.getElementById("progression-list");
  for (const prog of progressions) {
    const li = document.createElement("li");
    li.dataset.id = prog.id;
    li.innerHTML = `<strong>${prog.name}</strong><small>${prog.summary}</small>`;
    list.appendChild(li);
  }

  const engine = createAudioEngine();
  const drone = new Drone();

  let currentProg = progressions[0];
  let stepIndex = 0;
  let playing = false;
  let bpm = 84;
  let droneOn = true;
  let intervalId = null;

  function activate(prog) {
    currentProg = prog;
    stepIndex = 0;
    document.getElementById("provenance").textContent =
      "Source: " + (prog.book_ref?.join(", ") ?? "—");
    list.querySelectorAll("li").forEach((li) => {
      li.classList.toggle("is-active", li.dataset.id === prog.id);
    });
    document.getElementById("step-total").textContent = String(prog.steps.length);
    paintStep();
  }

  function currentStep() {
    return currentProg.steps[stepIndex];
  }
  function nextStep() {
    return currentProg.steps[(stepIndex + 1) % currentProg.steps.length];
  }

  function paintStep() {
    const step = currentStep();
    const next = nextStep();
    const role = roles.find((r) => r.mode_name === step.role);
    const nextRole = roles.find((r) => r.mode_name === next.role);
    const notes = scaleNotesFor(step, roles, chromatic);

    // Wheel — highlight current segment, draw arrow to next.
    for (const seg of outer.querySelectorAll(".role-segment")) {
      seg.classList.toggle("is-current", seg.dataset.mode === step.role);
    }
    drawNextArrow(arrowLayer, role, nextRole);

    // Side panel readout.
    document.getElementById("step-cur").textContent = String(stepIndex + 1);
    document.getElementById("step-glyph").textContent = step.glyph;
    document.getElementById("step-mode").textContent = step.role;
    document.getElementById("step-scale").textContent = step.improvise_in;
    document.getElementById("step-hint").textContent = step.hint;
    document.getElementById("step-bars").textContent = String(step.bars);
    const notesEl = document.getElementById("step-notes");
    notesEl.innerHTML = notes
      .map((n) => `<span class="note-pill">${displayNote(n)}</span>`)
      .join("");
    document.getElementById("next-glyph").textContent = next.glyph;
    document.getElementById("next-mode").textContent = next.role;

    // Instruments.
    repaintInstruments(piano, fretboard, roles, chromatic, notes);

    // Drone — soft sine on the step's tonic.
    if (droneOn) {
      // Kick the AudioContext on first paint via a no-op note (gesture required).
      const t = tonicOf(step);
      // Drone needs the engine's ctx; the engine creates it on first playNote.
      // Trigger a silent-ish note to bring up the ctx, then start the drone.
      try {
        engine.playNote(t, 4, { durationMs: 1, gain: 0.001 });
      } catch (_) { /* user hasn't interacted yet */ }
      // Pull the ctx out of the engine via a probe oscillator's context.
      const probe = engine.playNote(t, 4, { durationMs: 1, gain: 0.001 });
      drone.start(t, 3, probe?.context ?? null);
    } else {
      drone.stop();
    }
  }

  // Click a progression to load it.
  list.addEventListener("click", (e) => {
    const li = e.target.closest("li");
    if (!li) return;
    const prog = progressions.find((p) => p.id === li.dataset.id);
    if (prog) activate(prog);
  });

  document.querySelector("[data-action='prev']")?.addEventListener("click", () => {
    stepIndex = (stepIndex - 1 + currentProg.steps.length) % currentProg.steps.length;
    paintStep();
  });
  document.querySelector("[data-action='next']")?.addEventListener("click", () => {
    stepIndex = (stepIndex + 1) % currentProg.steps.length;
    paintStep();
  });

  const playBtn = document.getElementById("play-toggle");
  playBtn?.addEventListener("click", () => {
    playing = !playing;
    playBtn.setAttribute("aria-pressed", String(playing));
    playBtn.textContent = playing ? "❚❚ Pause" : "▶ Play";
    if (playing) {
      scheduleAdvance();
    } else if (intervalId !== null) {
      window.clearTimeout(intervalId);
      intervalId = null;
    }
  });

  function scheduleAdvance() {
    if (intervalId !== null) window.clearTimeout(intervalId);
    const step = currentStep();
    const msPerBar = (60 / bpm) * 4 * 1000;  // assume 4/4 time
    const dwellMs = step.bars * msPerBar;
    intervalId = window.setTimeout(() => {
      if (!playing) return;
      stepIndex = (stepIndex + 1) % currentProg.steps.length;
      paintStep();
      scheduleAdvance();
    }, dwellMs);
  }

  const bpmEl = /** @type {HTMLInputElement} */ (document.getElementById("bpm"));
  const bpmReadout = document.getElementById("bpm-readout");
  bpmEl?.addEventListener("input", () => {
    bpm = Number(bpmEl.value);
    if (bpmReadout) bpmReadout.textContent = String(bpm);
  });

  const droneEl = /** @type {HTMLInputElement} */ (document.getElementById("drone-toggle"));
  droneEl?.addEventListener("change", () => {
    droneOn = droneEl.checked;
    if (!droneOn) drone.stop();
    else paintStep();
  });

  document.addEventListener("keydown", (event) => {
    if (event.target.matches("input, textarea, select")) return;
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      stepIndex = (stepIndex - 1 + currentProg.steps.length) % currentProg.steps.length;
      paintStep();
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      stepIndex = (stepIndex + 1) % currentProg.steps.length;
      paintStep();
    } else if (event.key === " ") {
      event.preventDefault();
      playBtn?.click();
    }
  });

  activate(currentProg);
}

main();
