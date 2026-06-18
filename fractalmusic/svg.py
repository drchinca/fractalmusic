"""SVG renderers — the Gátople wheel, the carta deck, and scale diagrams.

Produces standalone SVG strings (no dependencies) you can write to a file and
open in any browser. This is the visual counterpart to ``showcase`` (which is
terminal-only).
"""

from math import cos, radians, sin

from fractalmusic.dodecamundo import DODECAMUNDO, NoteWorld, world
from fractalmusic.gatople import TOP_OF_CLOCK
from fractalmusic.scales import FractalScale

_FONT = "font-family='Helvetica,Arial,sans-serif'"


def _contrast(hex_color: str) -> str:
    """Pick black or white text for legibility against a fill."""
    cleaned = hex_color.lstrip("#")
    r, g, b = (int(cleaned[i : i + 2], 16) for i in (0, 2, 4))
    return "#111" if (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.55 else "#fff"


def _ring_xy(index: int, radius: float, cx: float, cy: float) -> tuple[float, float]:
    """Position of world ``index`` on a circle (A at 12 o'clock, clockwise)."""
    angle = radians(TOP_OF_CLOCK - index * 30.0)
    return (cx + radius * cos(angle), cy - radius * sin(angle))


def gatople_wheel(size: int = 520) -> str:
    """Render the 12-world color wheel with glyphs, notes, and numbers."""
    cx = cy = size / 2
    r_outer = size * 0.46
    r_inner = size * 0.26
    segments: list[str] = []
    labels: list[str] = []
    for w in DODECAMUNDO:
        start = radians(TOP_OF_CLOCK - (w.index - 0.5) * 30.0)
        end = radians(TOP_OF_CLOCK - (w.index + 0.5) * 30.0)
        x1o, y1o = cx + r_outer * cos(start), cy - r_outer * sin(start)
        x2o, y2o = cx + r_outer * cos(end), cy - r_outer * sin(end)
        x1i, y1i = cx + r_inner * cos(start), cy - r_inner * sin(start)
        x2i, y2i = cx + r_inner * cos(end), cy - r_inner * sin(end)
        segments.append(
            f"<path d='M{x1i:.1f},{y1i:.1f} L{x1o:.1f},{y1o:.1f} "
            f"A{r_outer:.1f},{r_outer:.1f} 0 0 1 {x2o:.1f},{y2o:.1f} "
            f"L{x2i:.1f},{y2i:.1f} A{r_inner:.1f},{r_inner:.1f} 0 0 0 "
            f"{x1i:.1f},{y1i:.1f} Z' fill='{w.color_hex}' stroke='#000' stroke-width='2'/>"
        )
        mid = (r_outer + r_inner) / 2
        lx, ly = _ring_xy(w.index, mid, cx, cy)
        fg = _contrast(w.color_hex)
        label = w.roman if w.is_pentatonic else w.note
        labels.append(
            f"<text x='{lx:.1f}' y='{ly - 6:.1f}' fill='{fg}' font-size='22' "
            f"text-anchor='middle' {_FONT}>{w.glyph}</text>"
            f"<text x='{lx:.1f}' y='{ly + 14:.1f}' fill='{fg}' font-size='14' "
            f"text-anchor='middle' {_FONT}>{label}</text>"
        )
    eye = (
        f"<circle cx='{cx}' cy='{cy}' r='{r_inner - 6:.1f}' fill='#f6e7c8' "
        f"stroke='#000' stroke-width='3'/>"
        f"<ellipse cx='{cx}' cy='{cy}' rx='14' ry='{r_inner - 22:.1f}' fill='#000'/>"
        f"<text x='{cx}' y='{cy + r_inner - 2:.1f}' fill='#000' font-size='13' "
        f"text-anchor='middle' {_FONT}>GÁTOPLE</text>"
    )
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{size}' "
        f"viewBox='0 0 {size} {size}'>"
        f"<rect width='{size}' height='{size}' fill='#fff'/>"
        + "".join(segments)
        + eye
        + "".join(labels)
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
