# fractalmusic

<p align="center">
  <img src="docs/assets/gatople-logo.png" alt="El Gátople" width="240">
</p>

Patricio Torres's **Sistema Fractal** — the *Dodecamundo*, the *Gátople* clock,
the 12 Greek + Penta modes, pentatonic-first scales, the 12 *cartas*, and the
etno-matemática chord formulas — implemented as a typed layer over
[pytheory](https://pytheory.org).

New to the system itself? Read **[¿Qué es Fractal Music World?](./QUE_ES_FRACTALWORLD.md)**
first — it explains the method, grounded in the book *El Sistema Fractal* (2024).

Everything is **A-origin** (La menor / matriarchal), which is also pytheory's
native tone order: index 0 = A, index 3 = C.

## Function lives on the wheel — notes just visit

The Gátople is a **two-disc spinner**. The outer disc carries the 12 *roles* —
each role is a fixed `(glyph, color, clock-position, scale-pattern)`. The inner
disc carries the 12 *notes*, and it **rotates freely** under the outer.

So the meaning is in the **angle / role**, not in the note. A note like `D` has
no fixed identity in the system — it's whichever role it's currently sitting
under. Spin the wheel one click and the same `D` becomes a different mode with a
different glyph and color. The pedagogy is geometric, not nominal:

```python
import fractalmusic as fm

fm.Wheel("A").mode_for("D").mode_name   # 'Dórico'   (D under +)
fm.Wheel("F").mode_for("D").mode_name   # 'Frigio'   (D under ♀)
fm.Wheel("D").mode_for("D").mode_name   # 'Eólico'   (D under ⋮ — D is now the tonic)
```

`A`-tonic is the book's default ("La menor matriarchal") — but any of the 12
notes can be the tonic. **Use the cards.** The role's glyph and color stay
where they are; the note that fills it is whatever lands at that position when
you spin to your tonic of choice.

## Las 12 Cartas Fractales

The canonical hand-painted deck by Patricio Torres, in order. Each carta carries
a **glyph** and a **color** that belong to the role, plus a default-tonic note.
The notes shown are the A-tonic readings — they will all rotate when you spin.

<p align="center">
<table>
<tr>
  <td align="center"><img src="docs/assets/cartas/01-dos-puntos.jpg" width="120"><br><b>1 · ⋮ Dos Puntos</b><br>A · Eólico · red</td>
  <td align="center"><img src="docs/assets/cartas/02-estrella-v.jpg" width="120"><br><b>2 · ★ V Estrella V</b><br>A♯/B♭ · Penta 5 · blue</td>
  <td align="center"><img src="docs/assets/cartas/03-triangulo.jpg" width="120"><br><b>3 · △ Triángulo</b><br>B · Locrio · green</td>
  <td align="center"><img src="docs/assets/cartas/04-casita.jpg" width="120"><br><b>4 · ■ Casita</b><br>C · Jónico · red roof</td>
</tr>
<tr>
  <td align="center"><img src="docs/assets/cartas/05-estrella-i.jpg" width="120"><br><b>5 · ★ I Estrella I</b><br>C♯/D♭ · Penta 1 · water blue</td>
  <td align="center"><img src="docs/assets/cartas/06-mas.jpg" width="120"><br><b>6 · + Más / Cruz</b><br>D · Dórico · green</td>
  <td align="center"><img src="docs/assets/cartas/07-estrella-ii.jpg" width="120"><br><b>7 · ★ II Estrella II</b><br>D♯/E♭ · Penta 2 · blue + sun</td>
  <td align="center"><img src="docs/assets/cartas/08-llave.jpg" width="120"><br><b>8 · ♀ Llave (koppa)</b><br>E · Frigio · red</td>
</tr>
<tr>
  <td align="center"><img src="docs/assets/cartas/09-flecha-arriba.jpg" width="120"><br><b>9 · ↑ Flecha arriba</b><br>F · Lidio · sky blue</td>
  <td align="center"><img src="docs/assets/cartas/10-estrella-iii.jpg" width="120"><br><b>10 · ★ III Estrella III</b><br>F♯/G♭ · Penta 3 · red (casa de Gátople)</td>
  <td align="center"><img src="docs/assets/cartas/11-flecha-abajo.jpg" width="120"><br><b>11 · ↓ Flecha abajo</b><br>G · Mixolidio · green</td>
  <td align="center"><img src="docs/assets/cartas/12-estrella-iv.jpg" width="120"><br><b>12 · ★ IV Estrella IV</b><br>G♯/A♭ · Penta 4 · blue + orange</td>
</tr>
</table>
</p>

<p align="center">
  <img src="docs/assets/cartas/00-portada.jpg" alt="Cover — Fractal Music World" width="280">
  <img src="docs/assets/cartas/13-instructivo.png" alt="Instructivo de uso" width="320">
</p>

*All images © Patricio Torres / Fractal Music World. Reproduced here as the
canonical reference for this study implementation.*

## Gallery

> The **Gátople** mandala (cat-cyclops with the 12-world ring) is a two-disc
> spinner — outer disc fixed (glyphs + colors), inner disc rotates the notes.
> The renderer for that artifact is being rebuilt to match the canonical paper
> toy and is temporarily omitted from this gallery.

**Piano & fretboard sticker overlays** — every key / every fret gets its Fractal
carta (glyph + color + note/roman). This is Pattorres's "bolombombin" stickers
and the fractalized guitar neck:

<p align="center">
  <img src="docs/assets/piano-stickers.png" alt="Piano carta stickers" width="520">
  <br>
  <img src="docs/assets/fretboard-stickers.png" alt="Fretboard carta stickers" width="640">
</p>

The **7 Greek modes** (white keys) and **5 Penta modes** (black-key stars) — each
a rotation of the same colored cartas:

<p align="center">
  <img src="docs/assets/greek-modes.png" alt="The 7 Greek modes" width="560">
  <br>
  <img src="docs/assets/penta-modes.png" alt="The 5 Penta modes" width="560">
</p>

Regenerate every visual any time:

```bash
fractalmusic-gallery            # writes all SVGs to docs/assets/
```

## Install

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

For development tooling:

```bash
bash scripts/setup_dev.sh
source .venv/bin/activate
```

## Use

```python
import fractalmusic as fm

print(fm.deck())                      # the 12 cartas, colored + glyphed
fm.world("Bb")                        # → NoteWorld for A# (enharmonic-aware)
fm.mode_for("C")                      # → Jónico, □, major, 12 o'clock
fm.penta("C#", mode="I")              # C# D# F# G# A# — Penta 1 (no semitones)
fm.cero_pitagoras("A")                # ['A','B','D','E','F#'] — 5-note penta seed
fm.spell(["A", "C", "E"])             # '⋮ □ ♀' — a chord written in glyphs
fm.interval_angle("A", "C")           # 90.0° on the Gátople
fm.fibonacci_chord("A", voices=4)     # chord stacked by Fibonacci offsets
fm.microstructures()                  # all 60 (5 penta modes × 12 roots)
```

## What it models (from the book)

| Concept | Module | Notes |
|---|---|---|
| Dodecamundo — 12 note-worlds | `dodecamundo.py` | note + mode + glyph + color + number + roman |
| 12 modes (7 Greek + 5 Penta) | `modes.py` | canonical glyph, quality, clock-hour per Ch. 4 & 8 |
| Gátople clock | `gatople.py` | angles, intervals, polygons, Cero Pitágoras |
| Pentatonic-first scales | `scales.py` | 5 modes, 60 microstructures, penta→hepta |
| The 12 cartas | `cartas.py` | truecolor cards, piano/fretboard stickers |
| Fibonacci / Pythagoras | `formulas.py` | chord building, ratios, chessboard potenciación |
| Glyphs & color wheel | `symbols.py`, `colors.py` | the 8-symbol vocabulary, 12-hue palette |

### The 5 + 7 = 12 skeleton

```
7 naturals (white keys) → Greek modes:  A⋮  B△  C□  D+  E♀  F↑  G↓
5 black keys → pentatonic stars:         A#★V  C#★I  D#★II  F#★III  G#★IV
```

## See it in color

```bash
fractalmusic              # or: python -m fractalmusic.showcase
```

prints the full system in 24-bit terminal color — the 12 cartas, the color
wheel, the 7 Greek modes, the 5 Penta modes, the Gátople clock (hour + angle),
and sample chords spelled in glyphs:

```
THE 7 GREEK MODES (white keys)
⋮ Eólico     minor       A  B  C  D  E  F  G    ⋮ △ □ + ♀ ↑ ↓
△ Locrio     diminished  B  C  D  E  F  G  A    △ □ + ♀ ↑ ↓ ⋮
□ Jónico     major       C  D  E  F  G  A  B    □ + ♀ ↑ ↓ ⋮ △
...
THE GÁTOPLE CLOCK (hour & angle from A)
⋮ A   Eólico      9 o'clock       0°
□ C   Jónico     12 o'clock      90°
★ F#  Penta 3     6 o'clock     270°
...
COMBINATIONS — music written in glyphs
A minor triad          A  C  E                ⋮ □ ♀
Cero Pitágoras (A)     A  B  D  E  F#         ⋮ △ + ♀ ★
```

## Testing

Three tiers, **120 tests, 100% coverage**:

```bash
make test                         # pytest with coverage (all tiers)
make check                        # lint, format, type-check, test, security scan
uv run pytest tests/unit          # 98 — data model & invariants
uv run pytest tests/integration   # 13 — cross-module + pytheory interop
uv run pytest tests/uat           # 9  — Gherkin behavioral scenarios
```

- **Unit** — Dodecamundo, modes, scales, Gátople geometry, formulas, cartas.
- **Integration** — every world round-trips through pytheory; glyphs and
  clock-hours stay consistent across modules; Eólico and Jónico are relatives.
- **UAT** — pytest-bdd features (`tests/uat/features/*.feature`) written from the
  learner's point of view: *learning the Dodecamundo*, *composing with the Gátople*.

## Status & provenance

The canonical bindings (note→mode→glyph→clock-hour, penta-mode spellings, the
A-origin) are taken from *El Sistema Fractal: Música Viva y en Reproducción*
(Torres, 2024), chapters 3–9. The **color palette** in `colors.py` is an
interpretation of the hand-painted cartas and the Gátople logo — swap `WHEEL_HEX`
for the exact card colors when the originals are digitized.

*All rights to the Sistema Fractal and the Gátople belong to Patricio Torres
Rivera / Fractal Music World. This repository is a study implementation.*
