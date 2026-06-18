// El Gátople — interactive two-disc spinner + piano + fretboard.
//
// Pure renderer. All glyphs, colors, labels, and bindings come from data.json
// (built by scripts/build_gatople_data.py). The JS is responsible only for
// layout, rotation, and event wiring — never for interpreting Sistema Fractal
// semantics.
//
// Layout convention: outer disc is laid out by clock hour (Función Cuartal),
// not chromatic index. Hour 12 sits at the top, hour 9 (A Eólico, the horizon)
// at 9 o'clock, hour 6 (★III, casa de Gátople) at the bottom.

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
  noteAtRolePosition,
  roleAtNote,
} from "./lib.js";
import { bindKeyboard, createAudioEngine } from "./audio.js";

// Inner-disc note positions live on a circle of radius NOTE_RADIUS at the
// canonical clock-hour angle of each role. Geometry overlays sit on the same
// circle so they rotate with the inner disc and stay tied to the notes.

/**
 * Render the chosen geometry overlays (heptagon / pentagram / zonas) into
 * the #geometry-layer / #zonas-layer groups. Idempotent — clears + redraws.
 *
 * Heptagon: connects the 7 hepta worlds (⋮ △ □ + ♀ ↑ ↓) — the diatonic
 *   skeleton drawn at the clock hours of A, B, C, D, E, F, G.
 * Pentagram: connects the 5 ★ worlds (Penta I..V) — Pythagoras's pentalfa,
 *   drawn through clock hours 5, 9, 1, 6, 2 in star order.
 * Zonas: 4 quality-flavored quadrant arcs (Ch. 8 grouping).
 *
 * @param {{
 *   inner: SVGGElement,
 *   zonas: SVGGElement,
 *   roles: readonly import("./lib.js").RoleEntry[],
 *   shapes: { heptagon: boolean, pentagram: boolean, zonas: boolean },
 * }} args
 */
function renderGeometry({ inner, zonas, roles, shapes }) {
  while (inner.firstChild) inner.removeChild(inner.firstChild);
  while (zonas.firstChild) zonas.removeChild(zonas.firstChild);

  const points = (filterFn) =>
    roles
      .filter(filterFn)
      .map((r) => polar(clockAngle(r.clock_hour), NOTE_RADIUS));

  if (shapes.heptagon) {
    const pts = points((r) => !r.is_penta);
    inner.appendChild(makePoly(pts, "geom-heptagon"));
  }
  if (shapes.pentagram) {
    // Star order: visit every other vertex around the 5-cycle.
    const pentaPts = points((r) => r.is_penta);
    const starOrder = [0, 2, 4, 1, 3];
    const pts = starOrder.map((i) => pentaPts[i]).filter(Boolean);
    inner.appendChild(makePoly(pts, "geom-pentagram"));
  }
  if (shapes.zonas) {
    // Four zona arcs (Ch. 8): groupings of 3 modes by quality flavor.
    // ⋮ Eólico zona = relaxation (red); + Dórico = opening (green);
    // ♀ Frigio = closure (red-violet); ↓ Mixolidio = compression (green-orange).
    // Drawn as faint colored arcs in the gap between inner ring and notes.
    const zonaSpec = [
      { glyph: "⋮", color: "#D43A2C", label: "zona ⋮" },
      { glyph: "+", color: "#3FA34D", label: "zona +" },
      { glyph: "♀", color: "#7D5BA6", label: "zona ♀" },
      { glyph: "↓", color: "#E67E22", label: "zona ↓" },
    ];
    for (const spec of zonaSpec) {
      const center = roles.find((r) => r.glyph === spec.glyph);
      if (!center) continue;
      // Each zona arc spans ±45° around its anchor mode, drawn at radius
      // halfway between the inner ring and the notes.
      const angle = clockAngle(center.clock_hour);
      const arc = makeZonaArc(angle - 45, angle + 45, NOTE_RADIUS - 18, spec.color, spec.label);
      zonas.appendChild(arc);
    }
  }
}

function makePoly(points, className) {
  const path = document.createElementNS(SVG_NS, "polygon");
  path.setAttribute(
    "points",
    points.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" "),
  );
  path.setAttribute("class", className);
  return path;
}

function makeZonaArc(startDeg, endDeg, radius, color, label) {
  const [x1, y1] = polar(startDeg, radius);
  const [x2, y2] = polar(endDeg, radius);
  const large = endDeg - startDeg > 180 ? 1 : 0;
  const path = document.createElementNS(SVG_NS, "path");
  path.setAttribute(
    "d",
    `M ${x1.toFixed(1)} ${y1.toFixed(1)} A ${radius} ${radius} 0 ${large} 1 ${x2.toFixed(1)} ${y2.toFixed(1)}`,
  );
  path.setAttribute("class", "zona-arc");
  path.setAttribute("stroke", color);
  const title = document.createElementNS(SVG_NS, "title");
  title.textContent = label;
  path.appendChild(title);
  return path;
}

const RING_INNER = 165;
const RING_MID = (RING_OUTER + RING_INNER) / 2;

// --- Outer disc (clock-hour layout, role glyphs) ---

function renderOuter(svgGroup, roles, onHover) {
  for (const role of roles) {
    const angle = clockAngle(role.clock_hour);
    const start = angle - SEG_DEG / 2;
    const end = angle + SEG_DEG / 2;

    const seg = document.createElementNS(SVG_NS, "path");
    seg.setAttribute("d", arcPath(start, end, RING_OUTER, RING_INNER));
    seg.setAttribute("fill", role.wheel_color);
    seg.setAttribute("class", "role-segment");
    seg.dataset.position = String(role.position);
    const title = document.createElementNS(SVG_NS, "title");
    title.textContent =
      `${role.carta_name}${role.clock_hour === 6 ? " (Casa de Gátople)" : ""}` +
      ` · ${role.mode_name} · ${role.quality} · ${role.clock_hour} o'clock`;
    seg.appendChild(title);
    seg.addEventListener("pointerenter", () => onHover(role));
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

// --- Inner disc (note labels, always upright while disc spins) ---

function renderInnerNotes(group, roles, onNoteClick) {
  for (const role of roles) {
    const angle = clockAngle(role.clock_hour);
    const [x, y] = polar(angle, NOTE_RADIUS);
    const note = role.note_default;

    const item = document.createElementNS(SVG_NS, "g");
    item.setAttribute("class", "note-item");
    item.setAttribute("transform", `translate(${x} ${y})`);
    item.dataset.angle = angle;
    item.dataset.note = note;
    item.addEventListener("click", () => onNoteClick(note));

    const disc = document.createElementNS(SVG_NS, "circle");
    disc.setAttribute("class", "note-disc");
    disc.setAttribute("r", NOTE_DISC_R);

    const label = document.createElementNS(SVG_NS, "text");
    label.setAttribute("class", "note-label");
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("dominant-baseline", "central");
    label.textContent = displayNote(note);

    item.appendChild(disc);
    item.appendChild(label);
    group.appendChild(item);
  }
}

function applyRotation(innerDisc, deg) {
  innerDisc.setAttribute("transform", `rotate(${deg})`);
  for (const item of innerDisc.querySelectorAll(".note-item")) {
    const angle = parseFloat(item.dataset.angle);
    const [x, y] = polar(angle, NOTE_RADIUS);
    item.setAttribute("transform", `translate(${x} ${y}) rotate(${-deg})`);
  }
}

// --- Piano keyboard (one octave A→G#) ---

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
      <rect x="${x}" y="0" width="${whiteW}" height="${PIANO_H}"
            fill="#fff" stroke="#1a1a1a" stroke-width="1.5"/>
      <rect class="piano-tint" x="${x + 4}" y="${PIANO_H - 70}"
            width="${whiteW - 8}" height="60" rx="3"
            stroke="#1a1a1a" stroke-width="1"/>
      <text class="piano-glyph" x="${x + whiteW / 2}" y="${PIANO_H - 50}"
            text-anchor="middle" dominant-baseline="central"
            font-size="20" font-weight="700"></text>
      <text class="piano-note" x="${x + whiteW / 2}" y="${PIANO_H - 22}"
            text-anchor="middle" font-size="13"></text>`;
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
      <rect class="piano-tint" x="${x + 3}" y="${blackH - 50}"
            width="${blackW - 6}" height="42" rx="3"
            stroke="#fff" stroke-width="1"/>
      <text class="piano-glyph" x="${x + blackW / 2}" y="${blackH - 32}"
            text-anchor="middle" dominant-baseline="central"
            font-size="16" font-weight="700" fill="#fff"></text>
      <text class="piano-note" x="${x + blackW / 2}" y="${blackH - 13}"
            text-anchor="middle" font-size="11" fill="#fff"></text>`;
    svg.appendChild(g);
  }
}

function repaintPiano(svg, roles, tonicOffset, chromatic, palette) {
  // Two palettes:
  //   carta — every key tinted with role.carta_color (red/green/blue/ivory)
  //   mono  — Penta-BW rule: cells whose role is a ★ render solid black,
  //           hepta cells render white. The pattern slides as the user spins
  //           the wheel because role bindings change per tonic.
  for (const key of svg.querySelectorAll(".piano-key")) {
    const note = key.dataset.note;
    const role = roleAtNote(note, roles, tonicOffset, chromatic);
    if (!role) continue;
    const tint = key.querySelector(".piano-tint");
    const glyph = key.querySelector(".piano-glyph");
    const label = key.querySelector(".piano-note");
    if (palette === "mono") {
      const fill = role.is_penta ? "#111" : "#ffffff";
      const fg = role.is_penta ? "#ffffff" : "#111";
      tint.setAttribute("fill", fill);
      glyph.setAttribute("fill", fg);
      label.setAttribute("fill", fg);
    } else {
      tint.setAttribute("fill", role.carta_color);
      glyph.removeAttribute("fill");
      label.removeAttribute("fill");
    }
    glyph.textContent = role.display_glyph;
    label.textContent = displayNote(note);
  }
}

// --- Guitar fretboard (EADGBE × 12 frets) ---

function renderFretboard(svg, chromatic) {
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  const rows = GUITAR_TUNING.length;

  const bg = document.createElementNS(SVG_NS, "rect");
  bg.setAttribute("x", 0);
  bg.setAttribute("y", 0);
  bg.setAttribute("width", FRET_PAD_LEFT + FRET_COUNT * FRET_W);
  bg.setAttribute("height", rows * STRING_H + 22);
  bg.setAttribute("fill", "#f3e3c0");
  svg.appendChild(bg);

  for (let f = 0; f <= FRET_COUNT; f++) {
    const x = FRET_PAD_LEFT + f * FRET_W;
    const wire = document.createElementNS(SVG_NS, "line");
    wire.setAttribute("x1", x);
    wire.setAttribute("x2", x);
    wire.setAttribute("y1", 0);
    wire.setAttribute("y2", rows * STRING_H);
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
        <rect class="fret-tint" x="${x + 4}" y="${y + 4}"
              width="${w - 8}" height="${STRING_H - 8}" rx="3"
              stroke="#1a1a1a" stroke-width="1"/>
        <text class="fret-glyph" x="${x + w / 2}" y="${y + STRING_H / 2 - 4}"
              text-anchor="middle" dominant-baseline="central"
              font-size="14" font-weight="700"></text>
        <text class="fret-label" x="${x + w / 2}" y="${y + STRING_H - 8}"
              text-anchor="middle" font-size="10" fill="#444"></text>`;
      svg.appendChild(g);
    }
  }
}

function repaintFretboard(svg, roles, tonicOffset, chromatic, palette) {
  // Penta-BW (mono): every fret position whose currently-bound role is a ★
  // renders as a solid black cell with a white glyph. Hepta cells are white
  // with a black glyph. The pattern slides horizontally as the user spins
  // the wheel — that's the canonical "pentatonic on the neck" view.
  for (const cell of svg.querySelectorAll(".fret-cell")) {
    const note = cell.dataset.note;
    const role = roleAtNote(note, roles, tonicOffset, chromatic);
    if (!role) continue;
    const tint = cell.querySelector(".fret-tint");
    const glyph = cell.querySelector(".fret-glyph");
    const label = cell.querySelector(".fret-label");
    if (palette === "mono") {
      const fill = role.is_penta ? "#111" : "#ffffff";
      const fg = role.is_penta ? "#ffffff" : "#111";
      tint.setAttribute("fill", fill);
      glyph.setAttribute("fill", fg);
      label.setAttribute("fill", role.is_penta ? "#ffffff" : "#444");
    } else {
      tint.setAttribute("fill", role.carta_color);
      glyph.removeAttribute("fill");
      label.setAttribute("fill", "#444");
    }
    glyph.textContent = role.display_glyph;
    label.textContent = displayNote(note);
  }
}

// --- Readouts ---

function updateBindings(roles, tonicOffset, chromatic) {
  const tbody = document.querySelector("#bindings tbody");
  tbody.innerHTML = "";
  const sorted = [...roles].sort((a, b) => a.clock_hour - b.clock_hour);
  for (const role of sorted) {
    const tr = document.createElement("tr");
    const note = noteAtRolePosition(role.position, tonicOffset, chromatic);
    const swatch = `<span class="swatch" style="background:${role.wheel_color}"></span>`;
    const label = role.is_penta ? role.display_glyph : role.mode_name;
    tr.innerHTML = `
      <td>${swatch}${label}</td>
      <td class="glyph-cell" style="color:${role.glyph_fg}">${role.display_glyph}</td>
      <td>${displayNote(note)}</td>
      <td>${role.clock_hour}</td>`;
    tbody.appendChild(tr);
  }
}

function updateTonicReadout(roles, tonicOffset, chromatic) {
  const tonic = chromatic[tonicOffset];
  document.getElementById("tonic-label").textContent = displayNote(tonic);
  const eolicoRole = roles.find((r) => r.position === 0);
  document.getElementById("tonic-mode").textContent = eolicoRole.mode_name;
}

// --- Main ---

async function main() {
  const data = /** @type {import("./lib.js").Payload} */ (
    await fetch("data.json").then((r) => r.json())
  );
  const { chromatic, roles } = data;

  const wheel = document.getElementById("wheel");
  const outer = document.getElementById("outer-disc");
  const inner = document.getElementById("inner-disc");
  const geometryLayer = document.getElementById("geometry-layer");
  const zonasLayer = document.getElementById("zonas-layer");
  const piano = document.getElementById("piano");
  const fretboard = document.getElementById("fretboard");

  let tonicOffset = 0;
  let palette = "carta";
  const shapes = { heptagon: false, pentagram: false, zonas: false };
  const engine = createAudioEngine();

  // Carta-card panel — slide in the painted card on segment hover.
  const cartaCard = document.getElementById("carta-card");
  const cartaImg = /** @type {HTMLImageElement} */ (document.getElementById("carta-card-img"));
  const cartaTitle = document.getElementById("carta-card-title");
  const cartaSub = document.getElementById("carta-card-sub");
  function showCarta(role) {
    if (!cartaCard) return;
    cartaImg.src = role.carta_image;
    cartaImg.alt = `${role.carta_name} carta`;
    cartaTitle.textContent =
      `${role.carta_name}${role.clock_hour === 6 ? " — casa de Gátople" : ""}`;
    cartaSub.textContent =
      `${role.mode_name} · ${role.quality} · ${role.clock_hour} o'clock`;
    cartaCard.classList.add("is-visible");
  }
  // Hide when leaving the wheel altogether (not on segment-to-segment move).
  document.getElementById("wheel")?.addEventListener("pointerleave", () => {
    cartaCard?.classList.remove("is-visible");
  });

  renderOuter(outer, roles, showCarta);
  renderInnerNotes(inner, roles, setTonic);
  renderPiano(piano, chromatic);
  renderFretboard(fretboard, chromatic);
  renderGeometry({ inner: geometryLayer, zonas: zonasLayer, roles, shapes });

  // Click-to-play on piano keys + fretboard cells. Uses the shared engine so
  // the AudioContext is the same one driving the QWERTY keyboard.
  function noteAtClick(target) {
    const node = target.closest("[data-note]");
    return node?.dataset.note ?? null;
  }
  piano.addEventListener("pointerdown", (event) => {
    const note = noteAtClick(event.target);
    if (note) engine.playNote(note);
  });
  fretboard.addEventListener("pointerdown", (event) => {
    const note = noteAtClick(event.target);
    if (note) engine.playNote(note);
  });

  function repaint() {
    applyRotation(inner, -tonicOffset * SEG_DEG);
    applyRotation(geometryLayer, -tonicOffset * SEG_DEG);
    updateTonicReadout(roles, tonicOffset, chromatic);
    updateBindings(roles, tonicOffset, chromatic);
    repaintPiano(piano, roles, tonicOffset, chromatic, palette);
    repaintFretboard(fretboard, roles, tonicOffset, chromatic, palette);
  }

  function setTonic(note) {
    const idx = indexOfNote(note, chromatic);
    if (idx < 0) return;
    tonicOffset = idx;
    repaint();
  }

  function step(delta) {
    const next = ((tonicOffset + delta) % 12 + 12) % 12;
    setTonic(chromatic[next]);
  }

  function setPalette(p) {
    palette = p;
    document.querySelectorAll("[data-palette]").forEach((b) => {
      b.classList.toggle("active", b.dataset.palette === palette);
    });
    repaint();
  }

  document.querySelectorAll("[data-action='reset']")
    .forEach((b) => b.addEventListener("click", () => setTonic("A")));
  document.querySelectorAll("[data-action='step-back']")
    .forEach((b) => b.addEventListener("click", () => step(-1)));
  document.querySelectorAll("[data-action='step-fwd']")
    .forEach((b) => b.addEventListener("click", () => step(1)));
  document.querySelectorAll("[data-palette]")
    .forEach((b) => b.addEventListener("click", () => setPalette(b.dataset.palette)));

  // Geometry overlay toggles + Cero Pitágoras.
  document.querySelectorAll("[data-shape]").forEach((b) => {
    b.addEventListener("click", () => {
      const key = b.dataset.shape;
      shapes[key] = !shapes[key];
      b.setAttribute("aria-pressed", shapes[key] ? "true" : "false");
      b.classList.toggle("active", shapes[key]);
      renderGeometry({ inner: geometryLayer, zonas: zonasLayer, roles, shapes });
      applyRotation(geometryLayer, -tonicOffset * SEG_DEG);
    });
  });
  // Cero Pitágoras (Ch. 4): the founding gesture — five fingers on five black
  // keys, arpeggiated. Always plays C# D# F# G# A# regardless of the wheel's
  // current tonic, because the gesture's identity is the literal black keys.
  document.querySelectorAll("[data-action='cero-pitagoras']").forEach((b) => {
    b.addEventListener("click", () => {
      const oct = engine.getOctave();
      engine.playSequence([
        ["C#", oct], ["D#", oct], ["F#", oct], ["G#", oct], ["A#", oct],
      ], { stepMs: 240 });
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.target.matches("input, textarea, select")) return;
    if (event.key === "ArrowLeft") { event.preventDefault(); step(-1); }
    else if (event.key === "ArrowRight") { event.preventDefault(); step(1); }
  });

  // Drag-to-spin: 30° drag = one semitone tonic shift.
  let dragging = false;
  let dragStartAngle = 0;
  let dragStartOffset = 0;

  function pointerAngle(event) {
    const rect = wheel.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    return Math.atan2(event.clientY - cy, event.clientX - cx) * (180 / Math.PI);
  }

  wheel.addEventListener("pointerdown", (event) => {
    if (event.target.closest(".note-item")) return;
    dragging = true;
    dragStartAngle = pointerAngle(event);
    dragStartOffset = tonicOffset;
    wheel.classList.add("dragging");
    inner.classList.add("dragging");
    wheel.setPointerCapture(event.pointerId);
  });
  wheel.addEventListener("pointermove", (event) => {
    if (!dragging) return;
    const delta = pointerAngle(event) - dragStartAngle;
    applyRotation(inner, -dragStartOffset * SEG_DEG + delta);
  });
  function endDrag(event) {
    if (!dragging) return;
    dragging = false;
    wheel.classList.remove("dragging");
    inner.classList.remove("dragging");
    wheel.releasePointerCapture(event.pointerId);
    const delta = pointerAngle(event) - dragStartAngle;
    const semitones = Math.round(delta / SEG_DEG);
    const newOffset = ((dragStartOffset + semitones) % 12 + 12) % 12;
    setTonic(chromatic[newOffset]);
  }
  wheel.addEventListener("pointerup", endDrag);
  wheel.addEventListener("pointercancel", endDrag);

  setTonic("A");
  setPalette("carta");

  // QWERTY keyboard play layer — see ./audio.js for the mapping.
  bindKeyboard({ onSetTonic: setTonic, engine });
}

main();
