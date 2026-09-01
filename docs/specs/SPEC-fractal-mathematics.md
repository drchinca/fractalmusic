---
title: fractal-mathematics — the canonical math reference
status: Implemented
author: drchinca
created: 2026-09-01
---

# Specification: Mathematical and Geometric Formulation of *El Sistema Fractal*

This specification defines the rigorous mathematical, algebraic, and group-theoretic foundations of the **Sistema Fractal / Gátople** core engine. It outlines how the 12 NoteWorlds, chord structures, and clock hours are derived deterministically on the Gátople wheel, moving beyond arbitrary western notation.

**This is the canonical, code-verified math reference for the system.** Every formula below was checked by direct substitution against the shipped implementation — `fractalmusic/modes.py` (`_clock_hour`), `fractalmusic/geometry.py` (chord polygons, icosahedron vertices), and `fractalmusic/formulas.py` (Fibonacci chords) — and against their test suites (`tests/unit/test_modes.py`, `test_geometry.py`, `test_formulas.py`). `docs/specs/WHITE-PAPER-fractal-music.md` cites this document rather than re-deriving these formulas, so a formula only needs fixing in one place.

---

## 1. The Chromatic Coordinate Space ($\mathbb{Z}_{12}$)

The Gátople ecosystem is modeled as the Ring of Integers Modulo 12, denoted as $\mathbb{Z}_{12} = \{0, 1, 2, \dots, 11\}$. 

In alignment with Patricio Torres's *matriarchal anchor*, the origin ($0$) is set to **La (A)** rather than the western convention of C:

$$x \in \mathbb{Z}_{12} \quad \text{where} \quad A = 0$$

### Chromatic Mapping Table:
$$\begin{array}{c|c|c|c|c|c|c|c|c|c|c|c}
A & A\#/B\flat & B & C & C\#/D\flat & D & D\#/E\flat & E & F & F\#/G\flat & G & G\#/A\flat \\
\hline
0 & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 & 11
\end{array}$$

The **chromatic interval** (distance) between any two note indices $a, b \in \mathbb{Z}_{12}$ is calculated via subtraction modulo 12:

$$d(a, b) = (b - a) \pmod{12}$$

---

## 2. The Circle of Fourths Isomorphism (Clock Hour $H$)

The Gátople wheel orders notes spatially by the **Circle of Fourths** to reflect harmonic gravity.

Let $n \in \mathbb{Z}_{12}$ be the A-origin chromatic note index. The bijection $H: \mathbb{Z}_{12} \to [1, 12]$ maps any note index to its exact **Gátople Clock Hour ($H$)**:

### Step 1: Map to Circle of Fourths step ($s$)
Perfect fourths correspond to jumps of 5 semitones in $\mathbb{Z}_{12}$. The number of fourth-steps from the origin $A$ is:

$$s(n) = (n \times 5) \pmod{12}$$

### Step 2: Align with the 9 o'clock Origin
In Gátople, the origin $A$ ($s=0$) sits at **9 o'clock**. Therefore, the clock hour $H$ is:

$$H(n) = \psi\Big(((n \times 5) + 9) \pmod{12}\Big)$$

$$\text{where} \quad \psi(y) = \begin{cases} 12 & \text{if } y = 0 \\ y & \text{otherwise} \end{cases}$$

---

## 3. The 12 NoteWorlds: Taxonomy & Spatial Regions

The Gátople clock face is divided into **two perfectly contiguous, segregated geometric regions** based on note families:

### ⚪ The Diatonic (Heptatonic) Region — Hours [7 to 1]
Consists of the 7 natural white-key notes representing the Greek family. Spans a continuous 7-hour block on the Gátople wheel:

$$\text{Hours} \in \{7, 8, 9, 10, 11, 12, 1\}$$

### ⚫ The Pentatonic Region — Hours [2 to 6]
Consists of the 5 sharp black-key notes representing the Star family (Roman numerals I to V). Spans a continuous 5-hour block:

$$\text{Hours} \in \{2, 3, 4, 5, 6\}$$

### 📋 Complete NoteWorld Taxonomy
$$\begin{array}{c|c|c|c|c|l|c|l}
\text{Index } (n) & \text{Note} & \text{Hour } (H) & \text{Glyph} & \text{Roman} & \text{Canonical Mode} & \text{Quality} & \text{Region/Family} \\
\hline
0 & A & 9 & \text{⋮} & - & \text{Eólico (Default Anchor)} & \text{minor} & \text{Diatonic (White)} \\
1 & A\# & 2 & \text{★} & \text{V} & \text{PentaV} & \text{minor} & \text{Pentatonic (Black)} \\
2 & B & 7 & \text{△} & - & \text{Locrio} & \text{diminished} & \text{Diatonic (White)} \\
3 & C & 12 & \text{□} & - & \text{Jónico} & \text{major} & \text{Diatonic (White)} \\
4 & C\# & 5 & \text{★} & \text{I} & \text{PentaI} & \text{minor} & \text{Pentatonic (Black)} \\
5 & D & 10 & \text{+} & - & \text{Dórico} & \text{minor} & \text{Diatonic (White)} \\
6 & D\# & 3 & \text{★} & \text{II} & \text{PentaII} & \text{minor} & \text{Pentatonic (Black)} \\
7 & E & 8 & \text{♀} & - & \text{Frigio} & \text{minor} & \text{Diatonic (White)} \\
8 & F & 1 & \text{↑} & - & \text{Lidio} & \text{major} & \text{Diatonic (White)} \\
9 & F\# & 6 & \text{★} & \text{III} & \text{PentaIII} & \text{major} & \text{Pentatonic (Black)} \\
10 & G & 11 & \text{↓} & - & \text{Mixolidio} & \text{major} & \text{Diatonic (White)} \\
11 & G\# & 4 & \text{★} & \text{IV} & \text{PentaIV} & \text{minor} & \text{Pentatonic (Black)}
\end{array}$$

### 🎵 Mode Scale Patterns (A-Origin Spellings)
1. **Eólico**: $(A, B, C, D, E, F, G)$ — steps: $2, 1, 2, 2, 1, 2, 2$
2. **Locrio**: $(B, C, D, E, F, G, A)$ — steps: $1, 2, 2, 1, 2, 2, 2$
3. **Jónico**: $(C, D, E, F, G, A, B)$ — steps: $2, 2, 1, 2, 2, 2, 1$
4. **Dórico**: $(D, E, F, G, A, B, C)$ — steps: $2, 1, 2, 2, 2, 1, 2$
5. **Frigio**: $(E, F, G, A, B, C, D)$ — steps: $1, 2, 2, 2, 1, 2, 2$
6. **Lidio**: $(F, G, A, B, C, D, E)$ — steps: $2, 2, 2, 1, 2, 2, 1$
7. **Mixolidio**: $(G, A, B, C, D, E, F)$ — steps: $2, 2, 1, 2, 2, 1, 2$
8. **PentaI**: $(C\#, D\#, F\#, G\#, A\#)$ — steps: $2, 3, 2, 2, 3$
9. **PentaII**: $(D\#, F\#, G\#, A\#, C\#)$ — steps: $3, 2, 2, 3, 2$
10. **PentaIII**: $(F\#, G\#, A\#, C\#, D\#)$ — steps: $2, 2, 3, 2, 3$
11. **PentaIV**: $(G\#, A\#, C\#, D\#, F\#)$ — steps: $2, 3, 2, 3, 2$
12. **PentaV**: $(A\#, C\#, D\#, F\#, G\#)$ — steps: $3, 2, 3, 2, 2$

---

## 4. The Two-Disc Rotation Group (Transposition)

The rotating inner note disc and fixed outer role disc represent the **Additive Group of Integers Modulo 12** acting on the NoteWorld space.

Let $t \in \mathbb{Z}_{12}$ be the chromatic index of the active **Tonic** (the Eólico rotation anchor).

### The Transposition Function ($T_t$)
When the wheel is spun to place Eólico over tonic $t$, the note $n \in \mathbb{Z}_{12}$ that lands under any role position $p \in [0, 11]$ (where $p=0$ is the Eólico position) is:

$$T_t(p) = (p + t) \pmod{12}$$

### The Inverse Role Function ($R_t$)
Conversely, given any note $n \in \mathbb{Z}_{12}$, the role position $p$ it occupies under a tonic $t$ rotation is:

$$R_t(n) = (n - t) \pmod{12}$$

---

## 5. 2D Chord Polygons on the Gátople Wheel

A chord is a subset of NoteWorlds $C = \{w_1, w_2, \dots, w_k\}$. We project this chord onto the Gátople wheel (modeled as a 2D Euclidean unit circle).

Using our clock hour function $H(n)$, the angular coordinate $\theta_i$ (in radians) for each note $n_i$ in the chord is:

$$\theta_i = \left(\frac{H(n_i) \cdot \pi}{6}\right) - \frac{\pi}{2}$$

This yields the 2D vertex coordinate $(x_i, y_i)$ on the unit circle:

$$x_i = \cos(\theta_i), \quad y_i = \sin(\theta_i)$$

### Centroid of the Chord ($\bar{x}, \bar{y}$)
The center of gravity (centroid) of the chord polygon indicates its harmonic balance on the Gátople:

$$\bar{x} = \frac{1}{k} \sum_{i=1}^k x_i, \quad \bar{y} = \frac{1}{k} \sum_{i=1}^k y_i$$

### Symmetry Invariant
If the centroid is exactly at the origin $(\bar{x}, \bar{y}) = (0, 0)$, the chord represents a perfectly balanced regular polygon (e.g., the augmented triad C-E-G# forming an equilateral triangle).

---

## 6. 3D Golden-Ratio Platonic Solid Mapping

The 12 NoteWorlds are mapped to the 12 face centers of a regular **Dodecahedron** (the 12 vertices of its dual, a regular **Icosahedron**).

Using the **Golden Ratio ($\phi = \frac{1+\sqrt{5}}{2} \approx 1.618$)**, we define the 3D coordinates for each note index $n \in \mathbb{Z}_{12}$ as vertices of a regular icosahedron of circumradius $\sqrt{1 + \phi^2}$:

$$\mathbf{v}(n) \in \mathbb{R}^3$$

$$\begin{array}{c|c|c}
\text{Index } (n) & \text{Note} & \text{3D Coordinate } \mathbf{v}(n) \\
\hline
0 & A & (0.0, 1.0, \phi) \\
1 & A\# & (0.0, -1.0, \phi) \\
2 & B & (0.0, 1.0, -\phi) \\
3 & C & (0.0, -1.0, -\phi) \\
4 & C\# & (1.0, \phi, 0.0) \\
5 & D & (-1.0, \phi, 0.0) \\
6 & D\# & (1.0, -\phi, 0.0) \\
7 & E & (-1.0, -\phi, 0.0) \\
8 & F & (\phi, 0.0, 1.0) \\
9 & F\# & (-\phi, 0.0, 1.0) \\
10 & G & (\phi, 0.0, -1.0) \\
11 & G\# & (-\phi, 0.0, -1.0)
\end{array}$$

### Distance Invariant
For any two adjacent vertices in this icosahedral note space, their Euclidean distance is always exactly $2$ units:

$$d_{\text{3D}}(a, b) = \|\mathbf{v}(b) - \mathbf{v}(a)\| = 2.0$$

---

## 7. Dynamic Chord Spacing Formulas

Chord formulas are represented as relative semitone steps from a starting root world, allowing any chord to be projected dynamically.

### Chord Formulas List
*   **MAJOR_TRIAD**: $(0, 4, 7)$
*   **MINOR_TRIAD**: $(0, 3, 7)$
*   **DIMINISHED_TRIAD**: $(0, 3, 6)$
*   **AUGMENTED_TRIAD**: $(0, 4, 8)$ — equilateral triangle
*   **MAJOR_7TH**: $(0, 4, 7, 11)$
*   **MINOR_7TH**: $(0, 3, 7, 10)$
*   **DOMINANT_7TH**: $(0, 4, 7, 10)$
*   **HALF_DIMINISHED_7TH**: $(0, 3, 6, 10)$
*   **DIMINISHED_7TH**: $(0, 3, 6, 9)$ — perfect square on chromatic circle

### The Fibonacci Chord Formula
The Fibonacci series $F = [1, 2, 3, 5, 8, \dots]$ (the book's form: no repeated leading $1$) acts as the growth scale for interval spacing.

Let $w_0 \in \mathbb{Z}_{12}$ be the starting root world. `fractalmusic.formulas.fibonacci_chord` constructs a dynamic **Fibonacci Chord** of $k$ voices by using each Fibonacci number directly as that voice's semitone offset from the root (not a cumulative sum — verified against `fibonacci_chord()` and locked in by `test_fibonacci_chord_offsets`):

$$n_i = \left(w_0 + F_i - 1\right) \pmod{12} \quad \text{for } i \in [1, k]$$

For example, `fibonacci_chord("A", voices=4)` gives offsets $F_i - 1 = 0, 1, 2, 4$, i.e. $[A, A\#, B, C\#]$. The construction is still genuinely Fibonacci-shaped: the *gap* between consecutive voices, $\text{offset}_i - \text{offset}_{i-1} = F_i - F_{i-1}$, is itself a Fibonacci number (the gaps for $k=6$ are $1, 1, 2, 3, 5$) — so voices spread apart at Fibonacci-growing intervals even though no individual offset is a running total.

> An earlier revision of this document (and of `WHITE-PAPER-fractal-music.md`) stated the cumulative-sum form above as the formula. That was checked against the shipped code on 2026-09-01 and found to not match — the code was treated as the source of truth (per this project's BE-owns-logic cardinal invariant) and both documents were corrected to describe the offset form actually implemented and tested.
