"""SVG renderers — the Gátople wheel, the carta deck, and scale diagrams.

Produces standalone SVG strings (no dependencies) you can write to a file and
open in any browser. This is the visual counterpart to ``showcase`` (which is
terminal-only).
"""

from math import cos, radians, sin

from fractalmusic.dodecamundo import DODECAMUNDO, NoteWorld, world
from fractalmusic.scales import FractalScale

_FONT = "font-family='Helvetica,Arial,sans-serif'"

# The wheel is anchored so C Jónico sits at 12 o'clock (top) and A Eólico at
# 9 o'clock (West), matching the canonical clock. C is chromatic index 3, so we
# rotate the drawing by -3 segments to lift C to the top.
_TOP_ANCHOR_INDEX = 3  # C
_BODY = "#e8c4a0"  # cat-head silhouette (peach)
_FACE = "#d9e86a"  # interior face field (yellow-green)
_NOSE = "#ec6fb0"  # pink pyramid nose


def _contrast(hex_color: str) -> str:
    """Pick black or white text for legibility against a fill."""
    cleaned = hex_color.lstrip("#")
    r, g, b = (int(cleaned[i : i + 2], 16) for i in (0, 2, 4))
    return "#111" if (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.55 else "#fff"


def _wheel_angle(index: float) -> float:
    """Math-angle (degrees) for a world index, with C at the top, A at 9 o'clock."""
    # 90° = top. Each index advances 30° clockwise; offset so C (index 3) is at top.
    return 90.0 - (index - _TOP_ANCHOR_INDEX) * 30.0


def _ring_xy(index: float, radius: float, cx: float, cy: float) -> tuple[float, float]:
    """Position of a world index on a circle (C at top, A at 9 o'clock)."""
    angle = radians(_wheel_angle(index))
    return (cx + radius * cos(angle), cy - radius * sin(angle))


def _cat_head(cx: float, cy: float, r: float) -> str:
    """The peach cat-head silhouette with two pointed ears and a center notch."""
    left = cx - r
    right = cx + r
    top = cy - r
    bottom = cy + r * 1.05
    return (
        f"<path d='M {left:.0f},{cy - r * 0.2:.0f} "
        f"L {cx - r * 0.55:.0f},{top - r * 0.35:.0f} "  # left ear tip
        f"Q {cx - r * 0.3:.0f},{cy - r * 0.78:.0f} {cx:.0f},{cy - r * 0.72:.0f} "  # notch
        f"Q {cx + r * 0.3:.0f},{cy - r * 0.78:.0f} {cx + r * 0.55:.0f},{top - r * 0.35:.0f} "
        f"L {right:.0f},{cy - r * 0.2:.0f} "  # right ear tip → side
        f"Q {right + r * 0.08:.0f},{cy + r * 0.55:.0f} {cx + r * 0.6:.0f},{bottom:.0f} "
        f"Q {cx:.0f},{bottom + r * 0.15:.0f} {cx - r * 0.6:.0f},{bottom:.0f} "
        f"Q {left - r * 0.08:.0f},{cy + r * 0.55:.0f} {left:.0f},{cy - r * 0.2:.0f} Z' "
        f"fill='{_BODY}' stroke='#000' stroke-width='10' stroke-linejoin='round'/>"
    )


def _cyclops_eye(cx: float, ey: float, w: float, h: float) -> str:
    """A wide almond sclera with a pale iris and a vertical slit pupil (top-center)."""
    iris_r = min(w * 0.92, h * 0.62)
    return (
        # almond sclera (wider than tall)
        f"<path d='M {cx - w:.0f},{ey:.0f} Q {cx:.0f},{ey - h:.0f} {cx + w:.0f},{ey:.0f} "
        f"Q {cx:.0f},{ey + h:.0f} {cx - w:.0f},{ey:.0f} Z' fill='#fff' "
        f"stroke='#000' stroke-width='7'/>"
        # pale-green iris, clearly lighter than the face field
        f"<circle cx='{cx:.0f}' cy='{ey:.0f}' r='{iris_r:.0f}' fill='#3fa66a' "
        f"stroke='#000' stroke-width='2'/>"
        # vertical slit pupil
        f"<path d='M {cx:.0f},{ey - iris_r * 0.95:.0f} "
        f"Q {cx + iris_r * 0.34:.0f},{ey:.0f} {cx:.0f},{ey + iris_r * 0.95:.0f} "
        f"Q {cx - iris_r * 0.34:.0f},{ey:.0f} {cx:.0f},{ey - iris_r * 0.95:.0f} Z' "
        f"fill='#111'/>"
    )


def _nose_and_whiskers(cx: float, cy: float, r: float) -> str:
    """The pink pyramid nose plus three whiskers per side."""
    apex_y = cy + r * 0.08
    base_y = cy + r * 0.62
    half = r * 0.34
    nose = (
        f"<path d='M {cx:.0f},{apex_y:.0f} L {cx + half:.0f},{base_y:.0f} "
        f"L {cx - half:.0f},{base_y:.0f} Z' fill='{_NOSE}' stroke='#000' stroke-width='6'/>"
        f"<path d='M {cx:.0f},{apex_y + r * 0.16:.0f} L {cx + half * 0.55:.0f},{base_y:.0f} "
        f"L {cx - half * 0.55:.0f},{base_y:.0f} Z' fill='{_FACE}' stroke='#000' stroke-width='3'/>"
    )
    whiskers: list[str] = []
    wy = cy + r * 0.34
    for i in range(3):
        dy = (i - 1) * r * 0.16
        whiskers.append(
            f"<line x1='{cx - half * 0.6:.0f}' y1='{wy + dy:.0f}' "
            f"x2='{cx - r * 0.92:.0f}' y2='{wy + dy * 1.6 - r * 0.05:.0f}' "
            f"stroke='#000' stroke-width='5' stroke-linecap='round'/>"
            f"<line x1='{cx + half * 0.6:.0f}' y1='{wy + dy:.0f}' "
            f"x2='{cx + r * 0.92:.0f}' y2='{wy + dy * 1.6 - r * 0.05:.0f}' "
            f"stroke='#000' stroke-width='5' stroke-linecap='round'/>"
        )
    return nose + "".join(whiskers)


def gatople_wheel(size: int = 560) -> str:
    """Render the Gátople: a cat-face mandala with the 12-world chromatic ring."""
    cx = size / 2
    cy = size * 0.56  # leave headroom for the ears
    head_r = size * 0.46
    r_outer = size * 0.40
    r_inner = size * 0.33
    height = int(size * 1.12)

    segments: list[str] = []
    glyphs: list[str] = []
    for w in DODECAMUNDO:
        a_start = radians(_wheel_angle(w.index - 0.5))
        a_end = radians(_wheel_angle(w.index + 0.5))
        x1o, y1o = cx + r_outer * cos(a_start), cy - r_outer * sin(a_start)
        x2o, y2o = cx + r_outer * cos(a_end), cy - r_outer * sin(a_end)
        x1i, y1i = cx + r_inner * cos(a_start), cy - r_inner * sin(a_start)
        x2i, y2i = cx + r_inner * cos(a_end), cy - r_inner * sin(a_end)
        segments.append(
            f"<path d='M{x1i:.1f},{y1i:.1f} L{x1o:.1f},{y1o:.1f} "
            f"A{r_outer:.1f},{r_outer:.1f} 0 0 0 {x2o:.1f},{y2o:.1f} "
            f"L{x2i:.1f},{y2i:.1f} A{r_inner:.1f},{r_inner:.1f} 0 0 1 "
            f"{x1i:.1f},{y1i:.1f} Z' fill='{w.color_hex}' stroke='#000' stroke-width='2.5'/>"
        )
        # Glyphs + labels float OUTSIDE the ring on the cat body (per the logo).
        gx, gy = _ring_xy(w.index, r_outer + size * 0.055, cx, cy)
        label = w.roman if w.is_pentatonic else w.note
        glyphs.append(
            f"<text x='{gx:.1f}' y='{gy:.1f}' fill='#111' font-size='24' "
            f"font-weight='bold' text-anchor='middle' dominant-baseline='central' "
            f"{_FONT}>{w.glyph}</text>"
            f"<text x='{gx:.1f}' y='{gy + size * 0.045:.1f}' fill='#333' font-size='14' "
            f"text-anchor='middle' {_FONT}>{label}</text>"
        )

    eye_y = cy - r_inner * 0.42
    body = (
        f"<rect width='{size}' height='{height}' fill='#fff'/>"
        + _cat_head(cx, cy, head_r)
        + f"<circle cx='{cx:.0f}' cy='{cy:.0f}' r='{r_inner:.1f}' fill='{_FACE}'/>"
        + "".join(segments)
        + _nose_and_whiskers(cx, cy, r_inner)
        + _cyclops_eye(cx, eye_y, r_inner * 0.6, r_inner * 0.42)
        + "".join(glyphs)
    )
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{height}' "
        f"viewBox='0 0 {size} {height}'>"
        + body
        + "</svg>"
    )


def _swatch_row(worlds: tuple[NoteWorld, ...], y: int, cell: int) -> str:
    """A horizontal row of colored, glyphed cells."""
    cells: list[str] = []
    for col, w in enumerate(worlds):
        x = col * cell
        fg = _contrast(w.color_hex)
        label = w.roman if w.is_pentatonic else w.note
        cells.append(
            f"<rect x='{x}' y='{y}' width='{cell}' height='{cell}' fill='{w.color_hex}' "
            f"stroke='#000'/>"
            f"<text x='{x + cell / 2:.0f}' y='{y + cell * 0.42:.0f}' fill='{fg}' "
            f"font-size='20' text-anchor='middle' {_FONT}>{w.glyph}</text>"
            f"<text x='{x + cell / 2:.0f}' y='{y + cell * 0.78:.0f}' fill='{fg}' "
            f"font-size='13' text-anchor='middle' {_FONT}>{label}</text>"
        )
    return "".join(cells)


def scale_strip(scale: FractalScale, *, cell: int = 64) -> str:
    """Render one scale as a row of colored carta cells."""
    worlds = tuple(world(n) for n in scale.notes)
    width = len(worlds) * cell
    height = cell + 28
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' "
        f"viewBox='0 0 {width} {height}'>"
        f"<rect width='{width}' height='{height}' fill='#fff'/>"
        f"<text x='4' y='18' fill='#111' font-size='14' {_FONT}>{scale.name}</text>"
        + _swatch_row(worlds, 24, cell)
        + "</svg>"
    )


def _carta_cell(w: NoteWorld, x: float, y: float, w_px: float, h_px: float, *, font: int) -> str:
    """A single colored sticker showing glyph + label, sized to a key/fret."""
    fg = _contrast(w.color_hex)
    label = w.roman if w.is_pentatonic else w.note
    return (
        f"<rect x='{x:.1f}' y='{y:.1f}' width='{w_px:.1f}' height='{h_px:.1f}' rx='3' "
        f"fill='{w.color_hex}' stroke='#000' stroke-width='1.5'/>"
        f"<text x='{x + w_px / 2:.1f}' y='{y + h_px * 0.42:.1f}' fill='{fg}' "
        f"font-size='{font}' text-anchor='middle' dominant-baseline='central' "
        f"{_FONT}>{w.glyph}</text>"
        f"<text x='{x + w_px / 2:.1f}' y='{y + h_px * 0.78:.1f}' fill='{fg}' "
        f"font-size='{max(8, font - 6)}' text-anchor='middle' {_FONT}>{label}</text>"
    )


def piano_stickers_svg(*, octaves: int = 1, white_w: int = 56, height: int = 220) -> str:
    """Piano keyboard with a Fractal carta sticker on every key (A-origin layout)."""
    # One octave in A-order: which chromatic indices are black keys.
    black = {1, 4, 6, 9, 11}
    naturals = [i for i in range(12) if i not in black]
    width = octaves * len(naturals) * white_w
    black_w = white_w * 0.62
    black_h = height * 0.6
    parts: list[str] = [f"<rect width='{width}' height='{height}' fill='#fff'/>"]
    # White keys first.
    white_x: dict[int, float] = {}
    col = 0
    for octave in range(octaves):
        for i in naturals:
            x: float = col * white_w
            white_x[octave * 12 + i] = x
            w = DODECAMUNDO[i]
            parts.append(
                f"<rect x='{x}' y='0' width='{white_w}' height='{height}' fill='#fff' "
                f"stroke='#000' stroke-width='1.5'/>"
            )
            parts.append(_carta_cell(w, x + 4, height - 70, white_w - 8, 60, font=22))
            col += 1
    # Black keys sit between the right edge of their lower white neighbour.
    lower = {1: 0, 4: 3, 6: 5, 9: 8, 11: 10}  # black index → white-key index below it
    for octave in range(octaves):
        for i, below in lower.items():
            x = white_x[octave * 12 + below] + white_w - black_w / 2
            w = DODECAMUNDO[i]
            parts.append(
                f"<rect x='{x:.1f}' y='0' width='{black_w:.1f}' height='{black_h:.1f}' "
                f"fill='#000'/>"
            )
            parts.append(
                _carta_cell(w, x + 3, black_h - 44, black_w - 6, 38, font=16)
            )
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' "
        f"viewBox='0 0 {width} {height}'>"
        + "".join(parts)
        + "</svg>"
    )


# Standard guitar tuning, low (6th) to high (1st), as chromatic A-indices.
_GUITAR_TUNING = ("E", "A", "D", "G", "B", "E")


def fretboard_stickers_svg(
    *, tuning: tuple[str, ...] = _GUITAR_TUNING, frets: int = 12, cell: int = 56
) -> str:
    """Fretboard with a Fractal carta sticker at every fret of every string."""
    rows = len(tuning)
    nut = cell  # left margin for the open-string label
    width = nut + frets * cell
    height = rows * cell + 24
    parts: list[str] = [f"<rect width='{width}' height='{height}' fill='#f3e3c0'/>"]
    # Fret wires + numbers.
    for f in range(frets + 1):
        x = nut + f * cell
        parts.append(
            f"<line x1='{x}' y1='0' x2='{x}' y2='{rows * cell}' stroke='#000' "
            f"stroke-width='{3 if f == 0 else 1.5}'/>"
        )
        if f > 0:
            parts.append(
                f"<text x='{x - cell / 2:.0f}' y='{rows * cell + 18:.0f}' fill='#333' "
                f"font-size='13' text-anchor='middle' {_FONT}>{f}</text>"
            )
    for s, open_note in enumerate(reversed(tuning)):  # top row = high string
        y = s * cell
        base = world(open_note).index
        parts.append(
            f"<line x1='{nut}' y1='{y + cell / 2:.0f}' x2='{width}' y2='{y + cell / 2:.0f}' "
            f"stroke='#000' stroke-width='1'/>"
        )
        for f in range(frets + 1):
            w = DODECAMUNDO[(base + f) % 12]
            x = nut + (f - 1) * cell if f > 0 else 0
            cw = cell if f > 0 else nut
            parts.append(_carta_cell(w, x + 4, y + 4, cw - 8, cell - 8, font=20))
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' "
        f"viewBox='0 0 {width} {height}'>"
        + "".join(parts)
        + "</svg>"
    )


def deck_grid(*, cols: int = 6, cell: int = 80) -> str:
    """Render all 12 cartas as a grid."""
    rows = (len(DODECAMUNDO) + cols - 1) // cols
    width, height = cols * cell, rows * cell
    cells: list[str] = []
    for i, w in enumerate(DODECAMUNDO):
        x, y = (i % cols) * cell, (i // cols) * cell
        fg = _contrast(w.color_hex)
        label = w.roman if w.is_pentatonic else w.note
        cells.append(
            f"<rect x='{x}' y='{y}' width='{cell}' height='{cell}' fill='{w.color_hex}' "
            f"stroke='#000' stroke-width='2'/>"
            f"<text x='{x + cell / 2:.0f}' y='{y + cell * 0.40:.0f}' fill='{fg}' "
            f"font-size='28' text-anchor='middle' {_FONT}>{w.glyph}</text>"
            f"<text x='{x + cell / 2:.0f}' y='{y + cell * 0.72:.0f}' fill='{fg}' "
            f"font-size='16' text-anchor='middle' {_FONT}>{label}</text>"
            f"<text x='{x + 6:.0f}' y='{y + 16:.0f}' fill='{fg}' font-size='11' "
            f"{_FONT}>{w.number}</text>"
        )
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' "
        f"viewBox='0 0 {width} {height}'>"
        f"<rect width='{width}' height='{height}' fill='#fff'/>"
        + "".join(cells)
        + "</svg>"
    )
