// El Gátople — kinetic scale wheel + piano/fretboard flows.
//
// ROLES remains the source of truth. The browser only moves the layers:
// notes set the tonic, the function ring can orbit, and the selected scale
// paints the wheel, keyboard, and fretboard from the same binding state.

const SVG_NS = "http://www.w3.org/2000/svg";
const RING_OUTER = 240;
const RING_INNER = 164;
const RING_MID = (RING_OUTER + RING_INNER) / 2;
const NOTE_RADIUS = 130;
const NOTE_DISC_R = 22;
const SCALE_RADIUS = 102;
const SEG_DEG = 30;

const ENHARMONIC = {
  "A#": "Bb", "C#": "Db", "D#": "Eb", "F#": "Gb", "G#": "Ab",
};

const GUITAR_TUNING = ["E", "A", "D", "G", "B", "E"];
const FRET_COUNT = 12;
const PIANO_W = 640;
const PIANO_H = 180;
const WHITE_KEYS = [
  { idx: 0, note: "A" },
  { idx: 2, note: "B" },
  { idx: 3, note: "C" },
  { idx: 5, note: "D" },
  { idx: 7, note: "E" },
  { idx: 8, note: "F" },
  { idx: 10, note: "G" },
  { idx: 12, note: "A" },
];
const BLACK_INDICES = [1, 4, 6, 9, 11];
const BLACK_LOWER = { 1: 0, 4: 3, 6: 5, 9: 8, 11: 10 };
const FRET_W = 60;
const STRING_H = 36;
const FRET_PAD_LEFT = 56;

function polar(deg, radius) {
  const rad = (deg - 90) * (Math.PI / 180);
  return [radius * Math.cos(rad), radius * Math.sin(rad)];
}

function clockAngle(hour) {
  return (hour % 12) * SEG_DEG;
}

function normalizeOffset(value) {
  return ((value % 12) + 12) % 12;
}

function normalizeDegrees(deg) {
  return ((deg % 360) + 360) % 360;
}

function shortestDelta(fromDeg, toDeg) {
  return ((toDeg - fromDeg + 540) % 360) - 180;
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

function noteFor(rolePosition, tonicOffset, chromatic) {
  return chromatic[(rolePosition + tonicOffset) % 12];
}

function indexOfNote(note, chromatic) {
  const idx = chromatic.indexOf(note);
  if (idx >= 0) return idx;
  for (const [sharp, flat] of Object.entries(ENHARMONIC)) {
    if (flat === note) return chromatic.indexOf(sharp);
  }
  return -1;
}

function displayNote(note) {
  return ENHARMONIC[note] ? `${note}/${ENHARMONIC[note]}` : note;
}

function roleAtNote(note, roles, tonicOffset, chromatic) {
  const noteIdx = indexOfNote(note, chromatic);
  if (noteIdx < 0) return null;
  const position = normalizeOffset(noteIdx - tonicOffset);
  return roles.find((role) => role.position === position) ?? null;
}

function roleDisplay(role) {
  return role.is_penta ? role.display_glyph : role.mode_name;
}

function scaleIndices(role, tonicOffset) {
  const rootIdx = normalizeOffset(role.position + tonicOffset);
  const indices = [rootIdx];
  let cursor = rootIdx;
  for (const step of role.scale_steps.slice(0, -1)) {
    cursor = normalizeOffset(cursor + step);
    indices.push(cursor);
  }
  return indices;
}

function scaleState(roles, activeRolePosition, tonicOffset, chromatic) {
  const role = roles.find((item) => item.position === activeRolePosition) ?? roles[0];
  const indices = scaleIndices(role, tonicOffset);
  const rootIdx = normalizeOffset(role.position + tonicOffset);
  const root = chromatic[rootIdx];
  return {
    role,
    indices,
    indexSet: new Set(indices),
    rootIdx,
    root,
    label: `${displayNote(root)} ${roleDisplay(role)}`,
  };
}

function orbitHour(role, functionDeg) {
  const angle = normalizeDegrees(clockAngle(role.clock_hour) + functionDeg);
  const hour = Math.round(angle / SEG_DEG) % 12;
  return hour === 0 ? 12 : hour;
}

function orbitControlValue(functionDeg) {
  return Math.round(((functionDeg + 180) % 360 + 360) % 360 - 180);
}

function syncOrbitControl(control, state) {
  if (document.activeElement !== control) {
    control.value = String(orbitControlValue(state.functionDeg));
  }
}

// --- Wheel layers ---

function renderOuter(svgGroup, roles, onRoleClick) {
  for (const role of roles) {
    const angle = clockAngle(role.clock_hour);
    const start = angle - SEG_DEG / 2;
    const end = angle + SEG_DEG / 2;

    const seg = document.createElementNS(SVG_NS, "path");
    seg.setAttribute("d", arcPath(start, end, RING_OUTER, RING_INNER));
    seg.setAttribute("fill", role.wheel_color);
    seg.setAttribute("class", "role-segment");
    seg.dataset.position = role.position;
    seg.addEventListener("click", () => onRoleClick(role.position));
    const title = document.createElementNS(SVG_NS, "title");
    title.textContent = `${role.carta_name} · ${role.mode_name} · ${role.quality}`;
    seg.appendChild(title);
    svgGroup.appendChild(seg);

    const [gx, gy] = polar(angle, RING_MID);
    const glyph = document.createElementNS(SVG_NS, "text");
    glyph.setAttribute("class", "role-glyph");
    glyph.setAttribute("x", gx);
    glyph.setAttribute("y", gy);
    glyph.setAttribute("fill", role.glyph_fg);
    glyph.dataset.position = role.position;
    glyph.dataset.x = gx;
    glyph.dataset.y = gy;
    glyph.textContent = role.display_glyph;
    svgGroup.appendChild(glyph);
  }
}

function renderSymbolTrails(group, roles) {
  group.innerHTML = "";
  for (const role of roles) {
    const base = clockAngle(role.clock_hour);
    for (let lane = 0; lane < 3; lane += 1) {
      const trail = document.createElementNS(SVG_NS, "text");
      trail.setAttribute("class", "symbol-trail");
      trail.setAttribute("fill", role.glyph_fg);
      trail.dataset.baseAngle = base + lane * 10 - 10;
      trail.dataset.radius = 63 + lane * 31;
      trail.dataset.position = role.position;
      trail.dataset.lane = lane;
      trail.textContent = role.display_glyph;
      group.appendChild(trail);
    }
  }
}

function renderInner(group, roles, onNoteClick) {
  for (const role of roles) {
    const angle = clockAngle(role.clock_hour);
    const [x, y] = polar(angle, NOTE_RADIUS);
    const note = role.note_default;
    const item = document.createElementNS(SVG_NS, "g");
    item.setAttribute("class", "note-item");
    item.setAttribute("transform", `translate(${x} ${y})`);
    item.dataset.angle = angle;
    item.dataset.note = note;
    item.dataset.position = role.position;
    item.addEventListener("click", () => onNoteClick(note));

    const disc = document.createElementNS(SVG_NS, "circle");
    disc.setAttribute("class", "note-disc");
    disc.setAttribute("r", NOTE_DISC_R);
    disc.dataset.note = note;

    const label = document.createElementNS(SVG_NS, "text");
    label.setAttribute("class", "note-label");
    label.setAttribute("data-note", note);
    label.textContent = displayNote(note);

    item.appendChild(disc);
    item.appendChild(label);
    group.appendChild(item);
  }
}

function renderScaleWeb(group, currentScale, roles) {
  group.innerHTML = "";
  const points = currentScale.indices.map((idx) => {
    const role = roles.find((item) => item.position === idx);
    const angle = role ? clockAngle(role.clock_hour) : idx * SEG_DEG;
    const [x, y] = polar(angle, SCALE_RADIUS);
    return { x, y, idx };
  });

  for (const point of points) {
    const spoke = document.createElementNS(SVG_NS, "line");
    spoke.setAttribute("class", "scale-spoke");
    spoke.setAttribute("x1", 0);
    spoke.setAttribute("y1", 0);
    spoke.setAttribute("x2", point.x);
    spoke.setAttribute("y2", point.y);
    group.appendChild(spoke);
  }

  const path = document.createElementNS(SVG_NS, "path");
  const d = points.map((point, idx) => `${idx === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ");
  path.setAttribute("class", "scale-path");
  path.setAttribute("d", `${d} Z`);
  group.appendChild(path);

  for (const point of points) {
    const node = document.createElementNS(SVG_NS, "circle");
    node.setAttribute("class", `scale-node${point.idx === currentScale.rootIdx ? " root" : ""}`);
    node.setAttribute("cx", point.x);
    node.setAttribute("cy", point.y);
    node.setAttribute("r", point.idx === currentScale.rootIdx ? 7 : 5);
    group.appendChild(node);
  }
}

function applyWheelTransforms(state, innerDisc, orbitDisc) {
  orbitDisc.setAttribute("transform", `rotate(${state.functionDeg})`);
  innerDisc.setAttribute("transform", `rotate(${state.visualDeg})`);

  for (const item of innerDisc.querySelectorAll(".note-item")) {
    const angle = parseFloat(item.dataset.angle);
    const [x, y] = polar(angle, NOTE_RADIUS);
    item.setAttribute("transform", `translate(${x} ${y}) rotate(${-state.visualDeg})`);
  }

  for (const glyph of orbitDisc.querySelectorAll(".role-glyph")) {
    const x = Number(glyph.dataset.x);
    const y = Number(glyph.dataset.y);
    glyph.setAttribute("transform", `rotate(${-state.functionDeg} ${x} ${y})`);
  }
}

function updateSymbolTrails(group, state) {
  const phase = state.flowPhase;
  for (const trail of group.querySelectorAll(".symbol-trail")) {
    const baseAngle = Number(trail.dataset.baseAngle);
    const radius = Number(trail.dataset.radius);
    const lane = Number(trail.dataset.lane);
    const position = Number(trail.dataset.position);
    const wave = Math.sin(phase * 0.018 + position * 0.9 + lane) * (5 + lane * 2);
    const breathing = Math.cos(phase * 0.014 + lane * 1.7 + position) * 4;
    const [x, y] = polar(baseAngle + wave, radius + breathing);
    trail.setAttribute("x", x);
    trail.setAttribute("y", y);
    trail.setAttribute("opacity", position === state.activeRolePosition ? 0.58 : 0.23 + lane * 0.05);
    trail.setAttribute("transform", `rotate(${-state.functionDeg + wave * 0.35} ${x} ${y})`);
  }
}

// --- Piano ---

function renderPiano(svg, chromatic) {
  const whiteW = PIANO_W / WHITE_KEYS.length;
  const blackW = whiteW * 0.62;
  const blackH = PIANO_H * 0.61;
  const whiteCol = {};

  WHITE_KEYS.forEach((key, col) => {
    if (key.idx < 12) whiteCol[key.idx] = col;
    else whiteCol[12] = col;
    const x = col * whiteW;
    const note = key.note;
    const chromaticIndex = key.idx % 12;
    const g = document.createElementNS(SVG_NS, "g");
    g.setAttribute("class", "piano-key piano-white");
    g.dataset.note = note;
    g.dataset.chromaticIndex = chromaticIndex;
    g.innerHTML = `
      <rect x="${x}" y="0" width="${whiteW}" height="${PIANO_H}"
            fill="#fffdfa" stroke="#171615" stroke-width="1.5"/>
      <rect class="piano-tint" x="${x + 5}" y="${PIANO_H - 72}"
            width="${whiteW - 10}" height="62" rx="4"/>
      <text class="piano-glyph" x="${x + whiteW / 2}" y="${PIANO_H - 52}"
            text-anchor="middle" dominant-baseline="central"
            font-size="20"></text>
      <text class="piano-note" x="${x + whiteW / 2}" y="${PIANO_H - 22}"
            text-anchor="middle" font-size="13"></text>`;
    svg.appendChild(g);
  });

  for (const idx of BLACK_INDICES) {
    const lowerCol = whiteCol[BLACK_LOWER[idx]];
    const x = lowerCol * whiteW + whiteW - blackW / 2;
    const note = chromatic[idx];
    const g = document.createElementNS(SVG_NS, "g");
    g.setAttribute("class", "piano-key piano-black");
    g.dataset.note = note;
    g.dataset.chromaticIndex = idx;
    g.innerHTML = `
      <rect x="${x}" y="0" width="${blackW}" height="${blackH}" rx="2" fill="#090807"/>
      <rect class="piano-tint" x="${x + 4}" y="${blackH - 52}"
            width="${blackW - 8}" height="43" rx="4"/>
      <text class="piano-glyph" x="${x + blackW / 2}" y="${blackH - 34}"
            text-anchor="middle" dominant-baseline="central"
            font-size="16" fill="#fff"></text>
      <text class="piano-note" x="${x + blackW / 2}" y="${blackH - 13}"
            text-anchor="middle" font-size="10.5" fill="#fff"></text>`;
    svg.appendChild(g);
  }
}

function repaintPiano(svg, roles, state, chromatic, currentScale) {
  for (const key of svg.querySelectorAll(".piano-key")) {
    const note = key.dataset.note;
    const noteIdx = Number(key.dataset.chromaticIndex);
    const role = roleAtNote(note, roles, state.tonicOffset, chromatic);
    if (!role) continue;

    const inScale = currentScale.indexSet.has(noteIdx);
    const isRoot = noteIdx === currentScale.rootIdx;
    const tint = key.querySelector(".piano-tint");
    const glyph = key.querySelector(".piano-glyph");
    const label = key.querySelector(".piano-note");
    const fill = state.palette === "mono" ? "#fff" : role.carta_color;
    const distance = normalizeOffset(noteIdx - currentScale.rootIdx);

    key.classList.toggle("in-scale", inScale);
    key.classList.toggle("is-root", isRoot);
    key.style.setProperty("--flow-delay", `${-(distance * 105)}ms`);
    key.style.setProperty("--flow-color", fill);
    tint.setAttribute("fill", fill);
    tint.setAttribute("stroke", isRoot ? "#111" : "rgba(23, 22, 21, 0.72)");
    glyph.textContent = role.display_glyph;
    label.textContent = displayNote(note);
  }
}

// --- Guitar fretboard ---

function renderFretboard(svg, chromatic) {
  const rows = GUITAR_TUNING.length;
  const bg = document.createElementNS(SVG_NS, "rect");
  bg.setAttribute("x", 0);
  bg.setAttribute("y", 0);
  bg.setAttribute("width", FRET_PAD_LEFT + FRET_COUNT * FRET_W);
  bg.setAttribute("height", rows * STRING_H + 22);
  bg.setAttribute("fill", "#f3e3c0");
  svg.appendChild(bg);

  for (let f = 0; f <= FRET_COUNT; f += 1) {
    const x = FRET_PAD_LEFT + f * FRET_W;
    const wire = document.createElementNS(SVG_NS, "line");
    wire.setAttribute("x1", x);
    wire.setAttribute("x2", x);
    wire.setAttribute("y1", 0);
    wire.setAttribute("y2", rows * STRING_H);
    wire.setAttribute("stroke", f === 0 ? "#171615" : "rgba(23, 22, 21, 0.58)");
    wire.setAttribute("stroke-width", f === 0 ? 3 : 1.45);
    svg.appendChild(wire);

    if (f > 0) {
      const num = document.createElementNS(SVG_NS, "text");
      num.setAttribute("class", "fret-number");
      num.setAttribute("x", x - FRET_W / 2);
      num.setAttribute("y", rows * STRING_H + 16);
      num.setAttribute("text-anchor", "middle");
      num.setAttribute("font-size", "12");
      num.textContent = f;
      svg.appendChild(num);
    }
  }

  const strings = [...GUITAR_TUNING].reverse();
  for (let s = 0; s < strings.length; s += 1) {
    const open = strings[s];
    const baseIdx = chromatic.indexOf(open);
    const stringLine = document.createElementNS(SVG_NS, "line");
    const yLine = s * STRING_H + STRING_H / 2;
    stringLine.setAttribute("x1", 0);
    stringLine.setAttribute("x2", FRET_PAD_LEFT + FRET_COUNT * FRET_W);
    stringLine.setAttribute("y1", yLine);
    stringLine.setAttribute("y2", yLine);
    stringLine.setAttribute("stroke", "rgba(23, 22, 21, 0.38)");
    stringLine.setAttribute("stroke-width", 1 + s * 0.16);
    svg.appendChild(stringLine);

    for (let f = 0; f <= FRET_COUNT; f += 1) {
      const chromIdx = (baseIdx + f) % 12;
      const note = chromatic[chromIdx];
      const x = f === 0 ? 0 : FRET_PAD_LEFT + (f - 1) * FRET_W;
      const w = f === 0 ? FRET_PAD_LEFT : FRET_W;
      const y = s * STRING_H;
      const g = document.createElementNS(SVG_NS, "g");
      g.setAttribute("class", "fret-cell");
      g.dataset.note = note;
      g.dataset.chromaticIndex = chromIdx;
      g.dataset.fret = f;
      g.dataset.string = s;
      g.innerHTML = `
        <rect class="fret-tint" x="${x + 4}" y="${y + 4}"
              width="${w - 8}" height="${STRING_H - 8}" rx="4"
              fill="#fffdfa" stroke="#171615" stroke-width="1"/>
        <text class="fret-glyph" x="${x + w / 2}" y="${y + STRING_H / 2 - 4}"
              text-anchor="middle" dominant-baseline="central"
              font-size="14">${note}</text>
        <text class="fret-label" x="${x + w / 2}" y="${y + STRING_H - 8}"
              text-anchor="middle" font-size="10">${note}</text>`;
      svg.appendChild(g);
    }
  }
}

function repaintFretboard(svg, roles, state, chromatic, currentScale) {
  for (const cell of svg.querySelectorAll(".fret-cell")) {
    const note = cell.dataset.note;
    const noteIdx = Number(cell.dataset.chromaticIndex);
    const role = roleAtNote(note, roles, state.tonicOffset, chromatic);
    if (!role) continue;

    const inScale = currentScale.indexSet.has(noteIdx);
    const isRoot = noteIdx === currentScale.rootIdx;
    const distance = normalizeOffset(noteIdx - currentScale.rootIdx);
    const fret = Number(cell.dataset.fret);
    const string = Number(cell.dataset.string);
    const tint = cell.querySelector(".fret-tint");
    const glyph = cell.querySelector(".fret-glyph");
    const label = cell.querySelector(".fret-label");
    const fill = state.palette === "mono" ? "#fff" : role.carta_color;

    cell.classList.toggle("in-scale", inScale);
    cell.classList.toggle("is-root", isRoot);
    cell.style.setProperty("--flow-delay", `${-(fret * 58 + string * 96 + distance * 24)}ms`);
    cell.style.setProperty("--flow-color", fill);
    tint.setAttribute("fill", fill);
    tint.setAttribute("stroke", isRoot ? "#111" : "rgba(23, 22, 21, 0.72)");
    glyph.textContent = role.display_glyph;
    label.textContent = displayNote(note);
  }
}

function transformSticker(parts, transform) {
  for (const part of parts) {
    if (part) part.style.transform = transform;
  }
}

function updateInstrumentFlow(piano, fretboard, state) {
  const currentScale = state.currentScale;
  if (!currentScale) return;

  const pianoPhase = state.flowPhase * 0.075 + state.visualDeg * 0.026;
  const fretPhase = state.flowPhase * 0.055 - state.functionDeg * 0.02;
  const energy = state.autoSpin ? 1 : 0.68;

  for (const key of piano.querySelectorAll(".piano-key")) {
    const noteIdx = Number(key.dataset.chromaticIndex);
    const distance = normalizeOffset(noteIdx - currentScale.rootIdx);
    const inScale = currentScale.indexSet.has(noteIdx);
    const isRoot = noteIdx === currentScale.rootIdx;
    const wave = Math.sin(pianoPhase + distance * 0.82);
    const lift = inScale ? -5 - (wave + 1) * 4.7 * energy : wave * 0.9;
    const scale = inScale ? 1 + (isRoot ? 0.052 : 0.032) * ((wave + 1) / 2) : 1;
    const opacity = inScale ? 0.76 + 0.22 * ((wave + 1) / 2) : 0.5 + 0.07 * ((wave + 1) / 2);
    const transform = `translateY(${lift.toFixed(2)}px) scale(${scale.toFixed(3)})`;
    transformSticker([
      key.querySelector(".piano-tint"),
      key.querySelector(".piano-glyph"),
      key.querySelector(".piano-note"),
    ], transform);
    key.querySelector(".piano-tint").style.opacity = opacity.toFixed(3);
  }

  for (const cell of fretboard.querySelectorAll(".fret-cell")) {
    const noteIdx = Number(cell.dataset.chromaticIndex);
    const fret = Number(cell.dataset.fret);
    const string = Number(cell.dataset.string);
    const distance = normalizeOffset(noteIdx - currentScale.rootIdx);
    const inScale = currentScale.indexSet.has(noteIdx);
    const isRoot = noteIdx === currentScale.rootIdx;
    const wave = Math.sin(fretPhase + fret * 0.36 + string * 0.7 + distance * 0.2);
    const drift = inScale ? wave * 5.4 * energy : wave * 1.2;
    const scale = inScale ? 1 + (isRoot ? 0.058 : 0.034) * ((wave + 1) / 2) : 1;
    const opacity = inScale ? 0.7 + 0.26 * ((wave + 1) / 2) : 0.48 + 0.08 * ((wave + 1) / 2);
    const transform = `translateX(${drift.toFixed(2)}px) scale(${scale.toFixed(3)})`;
    transformSticker([
      cell.querySelector(".fret-tint"),
      cell.querySelector(".fret-glyph"),
      cell.querySelector(".fret-label"),
    ], transform);
    cell.querySelector(".fret-tint").style.opacity = opacity.toFixed(3);
  }
}

// --- State readouts ---

function updateScaleOptions(select, roles, state, chromatic) {
  for (const option of select.options) {
    const role = roles.find((item) => item.position === Number(option.value));
    if (!role) continue;
    const root = noteFor(role.position, state.tonicOffset, chromatic);
    option.textContent = `${displayNote(root)} ${roleDisplay(role)}`;
  }
}

function updateBindings(roles, state, chromatic, currentScale) {
  const tbody = document.querySelector("#bindings tbody");
  tbody.innerHTML = "";
  const sorted = [...roles].sort((a, b) => a.clock_hour - b.clock_hour);
  for (const role of sorted) {
    const tr = document.createElement("tr");
    const note = noteFor(role.position, state.tonicOffset, chromatic);
    const swatch = `<span class="swatch" style="background:${role.wheel_color}"></span>`;
    const label = roleDisplay(role);
    tr.classList.toggle("is-active", role.position === currentScale.role.position);
    tr.innerHTML = `
      <td>${swatch}${label}</td>
      <td class="glyph-cell">${role.display_glyph}</td>
      <td>${displayNote(note)}</td>
      <td data-orbit-position="${role.position}">${orbitHour(role, state.functionDeg)}</td>`;
    tbody.appendChild(tr);
  }
}

function updateOrbitCells(roles, state) {
  for (const cell of document.querySelectorAll("[data-orbit-position]")) {
    const role = roles.find((item) => item.position === Number(cell.dataset.orbitPosition));
    if (!role) continue;
    const next = String(orbitHour(role, state.functionDeg));
    if (cell.textContent !== next) cell.textContent = next;
  }
}

function updateReadouts(state, roles, chromatic, currentScale) {
  const tonic = chromatic[state.tonicOffset];
  const tonicRole = roles.find((role) => role.position === 0);
  document.getElementById("tonic-label").textContent = displayNote(tonic);
  document.getElementById("tonic-mode").textContent = tonicRole?.mode_name ?? "";
  document.getElementById("scale-readout").textContent = currentScale.label;
  document.getElementById("piano-readout").textContent = currentScale.label;
  document.getElementById("fret-readout").textContent = `${currentScale.label} · EADGBE`;
}

function updateWheelClasses(roles, currentScale) {
  for (const seg of document.querySelectorAll(".role-segment")) {
    const pos = Number(seg.dataset.position);
    seg.classList.toggle("is-active", pos === currentScale.role.position);
    seg.classList.toggle("in-scale", currentScale.indexSet.has(pos));
  }
  for (const glyph of document.querySelectorAll(".role-glyph")) {
    const pos = Number(glyph.dataset.position);
    glyph.classList.toggle("is-active", pos === currentScale.role.position);
    glyph.classList.toggle("in-scale", currentScale.indexSet.has(pos));
  }
  for (const item of document.querySelectorAll(".note-item")) {
    const pos = Number(item.dataset.position);
    const inScale = currentScale.indexSet.has(pos);
    const isRoot = pos === currentScale.rootIdx;
    item.querySelector(".note-disc").classList.toggle("in-scale", inScale);
    item.querySelector(".note-disc").classList.toggle("is-root", isRoot);
    item.querySelector(".note-label").classList.toggle("is-root", isRoot);
  }
}

// --- Main ---

async function main() {
  const data = await fetch("../data.json").then((response) => response.json());
  const { chromatic, roles } = data;
  const roleByPosition = new Map(roles.map((role) => [role.position, role]));

  const wheel = document.getElementById("wheel");
  const orbitDisc = document.getElementById("orbit-disc");
  const outer = document.getElementById("outer-disc");
  const trails = document.getElementById("symbol-trails");
  const inner = document.getElementById("inner-disc");
  const scaleWeb = document.getElementById("scale-web");
  const piano = document.getElementById("piano");
  const fretboard = document.getElementById("fretboard");
  const scaleSelect = document.getElementById("scale-select");
  const spinToggle = document.getElementById("spin-toggle");
  const speedControl = document.getElementById("spin-speed");
  const orbitControl = document.getElementById("orbit-offset");

  const state = {
    activeRolePosition: 0,
    autoSpin: false,
    currentScale: null,
    flowPhase: 0,
    functionDeg: 0,
    palette: "carta",
    spinSpeed: Number(speedControl.value),
    tonicOffset: 0,
    visualDeg: 0,
  };

  function refresh() {
    const currentScale = scaleState(roles, state.activeRolePosition, state.tonicOffset, chromatic);
    state.currentScale = currentScale;
    renderScaleWeb(scaleWeb, currentScale, roles);
    updateScaleOptions(scaleSelect, roles, state, chromatic);
    scaleSelect.value = String(state.activeRolePosition);
    updateBindings(roles, state, chromatic, currentScale);
    updateReadouts(state, roles, chromatic, currentScale);
    updateWheelClasses(roles, currentScale);
    repaintPiano(piano, roles, state, chromatic, currentScale);
    repaintFretboard(fretboard, roles, state, chromatic, currentScale);
    applyWheelTransforms(state, inner, orbitDisc);
    updateInstrumentFlow(piano, fretboard, state);
    syncOrbitControl(orbitControl, state);
  }

  function setOffset(offset, syncVisual = true) {
    state.tonicOffset = normalizeOffset(offset);
    if (syncVisual) state.visualDeg = -state.tonicOffset * SEG_DEG;
    refresh();
  }

  function setTonic(note) {
    const idx = indexOfNote(note, chromatic);
    if (idx < 0) return;
    setOffset(idx);
  }

  function setActiveRole(position, focus = true) {
    state.activeRolePosition = Number(position);
    const role = roleByPosition.get(state.activeRolePosition);
    if (role && focus) {
      const currentAngle = normalizeDegrees(clockAngle(role.clock_hour) + state.functionDeg);
      state.functionDeg += shortestDelta(currentAngle, 0);
    }
    refresh();
  }

  function step(delta) {
    const next = normalizeOffset(state.tonicOffset + delta);
    state.functionDeg += delta * SEG_DEG * 0.32;
    setOffset(next);
  }

  for (const role of [...roles].sort((a, b) => a.clock_hour - b.clock_hour)) {
    const option = document.createElement("option");
    option.value = role.position;
    option.textContent = roleDisplay(role);
    scaleSelect.appendChild(option);
  }

  renderOuter(outer, roles, setActiveRole);
  renderSymbolTrails(trails, roles);
  renderInner(inner, roles, setTonic);
  renderPiano(piano, chromatic);
  renderFretboard(fretboard, chromatic);
  refresh();

  document.querySelectorAll("[data-action='reset']")
    .forEach((button) => button.addEventListener("click", () => {
      state.functionDeg = 0;
      state.activeRolePosition = 0;
      scaleSelect.value = "0";
      setTonic("A");
    }));
  document.querySelectorAll("[data-action='step-back']")
    .forEach((button) => button.addEventListener("click", () => step(-1)));
  document.querySelectorAll("[data-action='step-fwd']")
    .forEach((button) => button.addEventListener("click", () => step(1)));
  document.querySelectorAll("[data-palette]")
    .forEach((button) => button.addEventListener("click", () => {
      state.palette = button.dataset.palette;
      document.querySelectorAll("[data-palette]").forEach((item) => {
        item.classList.toggle("active", item.dataset.palette === state.palette);
      });
      refresh();
    }));

  scaleSelect.addEventListener("change", () => setActiveRole(Number(scaleSelect.value)));
  speedControl.addEventListener("input", () => {
    state.spinSpeed = Number(speedControl.value);
  });
  orbitControl.addEventListener("input", () => {
    state.functionDeg = Number(orbitControl.value);
    refresh();
  });
  spinToggle.addEventListener("click", () => {
    state.autoSpin = !state.autoSpin;
    spinToggle.setAttribute("aria-pressed", String(state.autoSpin));
    spinToggle.textContent = state.autoSpin ? "Pause" : "Spin";
  });

  document.addEventListener("keydown", (event) => {
    if (event.target.matches("input, textarea, select, button")) return;
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      step(-1);
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      step(1);
    } else if (event.key === " ") {
      event.preventDefault();
      spinToggle.click();
    }
  });

  let dragging = false;
  let dragStartAngle = 0;
  let dragStartVisual = 0;
  let dragStartFunction = 0;

  function pointerAngle(event) {
    const rect = wheel.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    return Math.atan2(event.clientY - cy, event.clientX - cx) * (180 / Math.PI);
  }

  function offsetFromVisual(deg) {
    return normalizeOffset(Math.round(-deg / SEG_DEG));
  }

  wheel.addEventListener("pointerdown", (event) => {
    dragging = true;
    state.autoSpin = false;
    spinToggle.setAttribute("aria-pressed", "false");
    spinToggle.textContent = "Spin";
    dragStartAngle = pointerAngle(event);
    dragStartVisual = state.visualDeg;
    dragStartFunction = state.functionDeg;
    wheel.classList.add("dragging");
    wheel.setPointerCapture(event.pointerId);
  });

  wheel.addEventListener("pointermove", (event) => {
    if (!dragging) return;
    const delta = shortestDelta(dragStartAngle, pointerAngle(event));
    state.visualDeg = dragStartVisual + delta;
    state.functionDeg = dragStartFunction + delta * 0.38;
    const nextOffset = offsetFromVisual(state.visualDeg);
    if (nextOffset !== state.tonicOffset) {
      state.tonicOffset = nextOffset;
      refresh();
    } else {
      applyWheelTransforms(state, inner, orbitDisc);
      updateOrbitCells(roles, state);
      syncOrbitControl(orbitControl, state);
    }
  });

  function endDrag(event) {
    if (!dragging) return;
    dragging = false;
    wheel.classList.remove("dragging");
    wheel.releasePointerCapture(event.pointerId);
    refresh();
  }

  wheel.addEventListener("pointerup", endDrag);
  wheel.addEventListener("pointercancel", endDrag);

  let lastFrame = performance.now();
  function animate(now) {
    const dt = Math.min((now - lastFrame) / 1000, 0.05);
    lastFrame = now;
    state.flowPhase += dt * (state.autoSpin ? 90 : 38);

    if (state.autoSpin && state.spinSpeed > 0) {
      state.visualDeg -= state.spinSpeed * dt;
      state.functionDeg += state.spinSpeed * 0.42 * dt;
      const nextOffset = offsetFromVisual(state.visualDeg);
      if (nextOffset !== state.tonicOffset) {
        state.tonicOffset = nextOffset;
        refresh();
      }
    }

    if (Math.abs(state.visualDeg) > 36000) {
      state.visualDeg %= 360;
      state.functionDeg %= 360;
    }

    updateSymbolTrails(trails, state);
    applyWheelTransforms(state, inner, orbitDisc);
    updateInstrumentFlow(piano, fretboard, state);
    updateOrbitCells(roles, state);
    syncOrbitControl(orbitControl, state);
    requestAnimationFrame(animate);
  }
  requestAnimationFrame(animate);
}

main();
