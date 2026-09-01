---
title: astronomical-gatople — solar/diurnal mapping of the wheel
status: Symbolic layer (not a verified physical claim)
author: drchinca
created: 2026-09-01
---

# Specification: Astronomical and Diurnal Mapping of the Gátople Wheel

> **Framing note (2026-09-01 audit).** This document describes a *symbolic/pedagogical* mapping this system's authors place onto the wheel — the 12-hour dial evenly divided into a 24-hour solar day — not a measured astronomical fact about the Gátople itself. No citation in the indexed fractal corpus (`f39cb7c5`, `b202598c`) was found asserting this solar correspondence (checked via `meridian-library search`); it is presented here as this project's own interpretive layer, in the same spirit as `docs/specs/WHITE-PAPER-fractal-music.md` §10, which this document should be read alongside. The mapping itself is internally consistent (each clock-hour step = 2 real hours, verified below) and is not in tension with anything — it just isn't a claim about the sun that requires outside evidence.

This specification outlines the diurnal/solar mapping laid onto the **Gátople wheel clock face**. In *El Sistema Fractal*, the 12 hours of the wheel do not merely represent a Circle of Fourths progression; they are also read, symbolically, against the sun's diurnal cycle (times of day and solar positions) on an astronomical dial.

---

## 1. The Astronomical Diurnal Clock Face

The Gátople wheel is aligned like an astronomical astrolabe where the four cardinal quadrants map directly to the four cardinal points of the sun's daily journey:

```text
                                ZENITH / MID-HEAVEN
                                  [12:00 PM - Noon]
                                    C [Jónico] ⚪
                                     [Square]
                                        □
                                        │
                                        │
      EASTERN HORIZON                   │                   WESTERN HORIZON
     [6:00 AM - Sunrise] ───────────────┼───────────────► [6:00 PM - Sunset]
        A [Eólico] ⚪                   │                   ⚫ D# [PentaII]
         [Two-Dots]                     │                      [Star]
            ⋮                           │                         ★
                                        │
                                        │
                                        ▼
                                  F# [PentaIII] ⚫
                                     [Star]
                                        ★
                                NADIR / MIDNIGHT
                               [12:00 AM - Midnight]
```

### The Cardinal Diurnal Anchors:
*   **🌅 9 o'clock — Note $A$ (Eólico, Glyph `⋮` [Two-Dots])**: Represents the **Eastern Horizon / 6:00 AM (Sunrise)**. It is the matriarchal horizon anchor of the entire system.
*   **☀️ 12 o'clock — Note $C$ (Jónico, Glyph `□` [Square])**: Represents the **Zenith / 12:00 PM (Noon)**. This is the "square-up" zenith node of maximum cosmic light.
*   **🌇 3 o'clock — Note $D\#$ (PentaII, Glyph `★` [Star])**: Represents the **Western Horizon / 6:00 PM (Sunset)**.
*   **🌙 6 o'clock — Note $F\#$ (PentaIII, Glyph `★` [Star])**: Represents the **Nadir / 12:00 AM (Midnight)**. This is the "fully south node", representing the absolute depths of darkness and rest.

---

## 2. Diurnal Mappings & Coordinates Table

This table maps each NoteWorld index ($n$) to its Gátople clock hour ($H$), its 2D coordinates on the unit circle, and its corresponding diurnal time of day:

$$\begin{array}{c|c|c|c|c|l|c}
\text{Hour } (H) & \text{Time of Day} & \text{Note} & \text{Glyph} & \text{2D Coordinate } (x, y) & \text{Family} & \text{Solar Position} \\
\hline
\mathbf{9} & \mathbf{6:00\text{ AM}} & A & \text{⋮} & (-1.000, 0.000) & \text{Diatonic (White)} & \text{Sunrise / Eastern Horizon} \\
10 & 8:00\text{ AM} & D & \text{+} & (-0.866, 0.500) & \text{Diatonic (White)} & \text{Morning Ascent} \\
11 & 10:00\text{ AM} & G & \text{↓} & (-0.500, 0.866) & \text{Diatonic (White)} & \text{Late Morning} \\
\mathbf{12} & \mathbf{12:00\text{ PM}} & C & \text{□} & (0.000, 1.000) & \text{Diatonic (White)} & \text{Noon / Zenith (Square Up)} \\
1 & 2:00\text{ PM} & F & \text{↑} & (0.500, 0.866) & \text{Diatonic (White)} & \text{Early Afternoon} \\
2 & 4:00\text{ PM} & A\# & \text{★} & (0.866, 0.500) & \text{Pentatonic (Black)} & \text{Late Afternoon} \\
\mathbf{3} & \mathbf{6:00\text{ PM}} & D\# & \text{★} & (1.000, 0.000) & \text{Pentatonic (Black)} & \text{Sunset / Western Horizon} \\
4 & 8:00\text{ PM} & G\# & \text{★} & (0.866, -0.500) & \text{Pentatonic (Black)} & \text{Dusk / Evening} \\
5 & 10:00\text{ PM} & C\# & \text{★} & (0.500, -0.866) & \text{Pentatonic (Black)} & \text{Late Night} \\
\mathbf{6} & \mathbf{12:00\text{ AM}} & F\# & \text{★} & (0.000, -1.000) & \text{Pentatonic (Black)} & \text{Midnight / Nadir (Fully South)} \\
7 & 2:00\text{ AM} & B & \text{△} & (-0.500, -0.866) & \text{Diatonic (White)} & \text{Witching Hour} \\
8 & 4:00\text{ AM} & E & \text{♀} & (-0.866, -0.500) & \text{Diatonic (White)} & \text{Predawn / Twilight}
\end{array}$$

---

## 3. Geometric Centroids and Chord Symmetries

Because Gátople is geometrically organized, chords draw distinct polygons inside the clock wheel.

### Augmented Triad (The Equilateral Symmetries)
An augmented triad (e.g., C augmented: C–E–G#) jumps exactly 4 semitones per note. On the Gátople clock face:
*   C sits at 12 o'clock (Noon)
*   G# sits at 4 o'clock (Dusk)
*   E sits at 8 o'clock (Twilight)

This draws a **perfectly regular equilateral triangle** on the wheel, placing its center of gravity (centroid) exactly at the origin `(0.0, 0.0)`!

```text
                  C [12] (Noon)
                  /\
                 /  \
                /    \
               /  👁  \
              /        \
             /          \
  E [8] (Twilight)------- G# [4] (Dusk)
```

### Diminished Seventh (The Chromatic Square)
A diminished 7th chord (e.g., Adim7: A–C–D#–F#) divides the 12 chromatic semitones into perfectly symmetric 3-semitone sectors `(0, 3, 6, 9)`. 

On the Gátople wheel (the Circle of Fourths), this connects the four cardinal points:
*   A sits at 9 o'clock (6:00 AM)
*   C sits at 12 o'clock (12:00 PM)
*   D# sits at 3 o'clock (6:00 PM)
*   F# sits at 6 o'clock (12:00 AM)

This forms a perfect cross/quadrilateral, symmetrically balancing the morning, noon, sunset, and midnight energies of the diurnal cycle.
