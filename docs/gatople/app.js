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

const SVG_NS = "http://www.w3.org/2000/svg";

const RING_OUTER = 240;
const RING_INNER = 165;
const RING_MID = (RING_OUTER + RING_INNER) / 2;
const NOTE_RADIUS = 130;
const NOTE_DISC_R = 22;
const SEG_DEG = 30;

const ENHARMONIC_FLAT = {
  "A#": "Bb", "C#": "Db", "D#": "Eb", "F#": "Gb", "G#": "Ab",
};

const GUITAR_TUNING = ["E", "A", "D", "G", "B", "E"];
const FRET_COUNT = 12;

function polar(deg, radius) {
  const rad = (deg - 90) * (Math.PI / 180);
  return [radius * Math.cos(rad), radius * Math.sin(rad)];
}

function clockAngle(hour) {
  return (hour % 12) * SEG_DEG;
}

function arcPath(startDeg, endDeg, rOuter, rInner) {
  const [x1o, y1o] = polar(startDeg, rOuter);
  const [x2o, y2o] = polar(endDeg, rOuter);
  const [x1i, y1i] = polar(startDeg, rInner);
  const [x2i, y2i] = polar(endDeg, rInner);
  const large = endDeg - startDeg > 180 ? 1 : 0;
  return [
    "M", x1i, y1i,
    "L", x1o, y1o,
    "A", rOuter, rOuter, 0, large, 1, x2o, y2o,
    "L", x2i, y2i,
    "A", rInner, rInner, 0, large, 0, x1i, y1i,
    "Z",
  ].join(" ");
}

function indexOfNote(note, chromatic) {
  const i = chromatic.indexOf(note);
  if (i >= 0) return i;
  for (const [sharp, flat] of Object.entries(ENHARMONIC_FLAT)) {
    if (flat === note) return chromatic.indexOf(sharp);
  }
  return -1;
}

function displayNote(note) {
  return ENHARMONIC_FLAT[note] ? `${note}/${ENHARMONIC_FLAT[note]}` : note;
}

function noteAtRolePosition(rolePosition, tonicOffset, chromatic) {
  return chromatic[(rolePosition + tonicOffset) % 12];
}

function roleAtNote(note, roles, tonicOffset, chromatic) {
  const noteIdx = indexOfNote(note, chromatic);
  if (noteIdx < 0) return null;
  const position = (noteIdx - tonicOffset + 12) % 12;
  return roles.find((r) => r.position === position) ?? null;
}

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
    const title = document.createElementNS(SVG_NS, "title");
    title.textContent =
      `${role.carta_name} · ${role.mode_name} · ${role.quality} · ${role.clock_hour} o'clock`;
    seg.appendChild(title);
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
const WHITE_INDICES = [0, 2, 3, 5, 7, 8, 10];
const BLACK_INDICES = [1, 4, 6, 9, 11];
const BLACK_LOWER = { 1: 0, 4: 3, 6: 5, 9: 8, 11: 10 };

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
  for (const key of svg.querySelectorAll(".piano-key")) {
    const note = key.dataset.note;
    const role = roleAtNote(note, roles, tonicOffset, chromatic);
    if (!role) continue;
    const tint = key.querySelector(".piano-tint");
    const glyph = key.querySelector(".piano-glyph");
    const label = key.querySelector(".piano-note");
    tint.setAttribute("fill", palette === "mono" ? "#ffffff" : role.carta_color);
    glyph.textContent = role.display_glyph;
    label.textContent = displayNote(note);
  }
}

// --- Guitar fretboard (EADGBE × 12 frets) ---

const FRET_W = 60;
const STRING_H = 36;
const FRET_PAD_LEFT = 56;

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
  for (const cell of svg.querySelectorAll(".fret-cell")) {
    const note = cell.dataset.note;
    const role = roleAtNote(note, roles, tonicOffset, chromatic);
    if (!role) continue;
    const tint = cell.querySelector(".fret-tint");
    const glyph = cell.querySelector(".fret-glyph");
    const label = cell.querySelector(".fret-label");
    tint.setAttribute("fill", palette === "mono" ? "#ffffff" : role.carta_color);
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
  const data = await fetch("data.json").then((r) => r.json());
  const { chromatic, roles } = data;

  const wheel = document.getElementById("wheel");
  const outer = document.getElementById("outer-disc");
  const inner = document.getElementById("inner-disc");
  const piano = document.getElementById("piano");
  const fretboard = document.getElementById("fretboard");

  let tonicOffset = 0;
  let palette = "carta";

  renderOuter(outer, roles);
  renderInnerNotes(inner, roles, setTonic);
  renderPiano(piano, chromatic);
  renderFretboard(fretboard, chromatic);

  function repaint() {
    applyRotation(inner, -tonicOffset * SEG_DEG);
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
}

main();
