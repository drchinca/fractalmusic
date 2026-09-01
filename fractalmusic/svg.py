"""SVG renderers — the Gátople wheel, the carta deck, and scale diagrams.

Produces standalone SVG strings (no dependencies) you can write to a file and
open in any browser. This is the visual counterpart to ``showcase`` (which is
terminal-only).
"""

import math
from typing import TYPE_CHECKING

from fractalmusic.dodecamundo import DODECAMUNDO, NoteWorld, world
from fractalmusic.scales import FractalScale

if TYPE_CHECKING:
    from fractalmusic.wheel import Wheel

_FONT = "font-family='Helvetica,Arial,sans-serif'"


def _contrast(hex_color: str) -> str:
    """Pick black or white text for legibility against a fill."""
    cleaned = hex_color.lstrip("#")
    r, g, b = (int(cleaned[i : i + 2], 16) for i in (0, 2, 4))
    return "#111" if (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.55 else "#fff"


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
            parts.append(_carta_cell(w, x + 3, black_h - 44, black_w - 6, 38, font=16))
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' "
        f"viewBox='0 0 {width} {height}'>" + "".join(parts) + "</svg>"
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
        f"viewBox='0 0 {width} {height}'>" + "".join(parts) + "</svg>"
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
        f"<rect width='{width}' height='{height}' fill='#fff'/>" + "".join(cells) + "</svg>"
    )


def _polar(deg: float, radius: float) -> tuple[float, float]:
    """Calculate Euclidean (x, y) coordinates from fractal polar coordinates."""
    rad = (deg - 90) * (math.pi / 180.0)
    return radius * math.cos(rad), radius * math.sin(rad)


def _arc_path(start_deg: float, end_deg: float, r_outer: float, r_inner: float) -> str:
    """Generate deterministic SVG arc geometry for fractal sectors."""
    x1o, y1o = _polar(start_deg, r_outer)
    x2o, y2o = _polar(end_deg, r_outer)
    x1i, y1i = _polar(start_deg, r_inner)
    x2i, y2i = _polar(end_deg, r_inner)
    large = 1 if (end_deg - start_deg) > 180 else 0
    return (
        f"M {x1i:.3f} {y1i:.3f} "
        f"L {x1o:.3f} {y1o:.3f} "
        f"A {r_outer} {r_outer} 0 {large} 1 {x2o:.3f} {y2o:.3f} "
        f"L {x2i:.3f} {y2i:.3f} "
        f"A {r_inner} {r_inner} 0 {large} 0 {x1i:.3f} {y1i:.3f} Z"
    )


def gatople_wheel_svg(wheel: "Wheel", *, size: int = 600) -> str:
    """Render the deterministic spinning Gátople wheel natively using backend geometry math."""
    r_outer = size * 0.4
    r_inner = size * 0.275
    r_mid = (r_outer + r_inner) / 2
    note_radius = size * 0.21
    seg_deg = 30.0

    parts: list[str] = []
    
    # 1. Geometry of the Outer Disc (Fixed Roles)
    for role in wheel.all_modes():
        angle = (role.clock_hour % 12) * seg_deg
        start = angle - seg_deg / 2
        end = angle + seg_deg / 2
        path = _arc_path(start, end, r_outer, r_inner)
        gx, gy = _polar(angle, r_mid)

        w = DODECAMUNDO[role.role.position]
        fg = _contrast(w.color_hex)
        parts.append(
            f"<path d='{path}' fill='{w.color_hex}' stroke='#111' stroke-width='2'/>"
            f"<text x='{gx:.1f}' y='{gy + 8:.1f}' fill='{fg}' font-size='32' text-anchor='middle' {_FONT}>{w.glyph}</text>"
        )

    # 2. Geometry of the Inner Disc (Rotating Notes synced to Tonic)
    for role in wheel.all_modes():
        angle = (role.clock_hour % 12) * seg_deg
        nx, ny = _polar(angle, note_radius)
        # Format the display note dynamically 
        note_str = role.note.replace("#", "♯")
        parts.append(
            f"<circle cx='{nx:.1f}' cy='{ny:.1f}' r='{size * 0.04:.1f}' fill='#fff' stroke='#333' stroke-width='2'/>"
            f"<text x='{nx:.1f}' y='{ny + 5:.1f}' fill='#111' font-size='18' font-weight='bold' text-anchor='middle' {_FONT}>{note_str}</text>"
        )

    cx, cy = size / 2, size / 2
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{size}' viewBox='{-cx} {-cy} {size} {size}'>"
        f"<rect x='{-cx}' y='{-cy}' width='{size}' height='{size}' fill='#fcf8ee'/>"
        + "".join(parts) +
        f"<circle cx='0' cy='0' r='{size * 0.08}' fill='#fff' stroke='#333' stroke-width='2'/>"
        f"<text x='0' y='6' fill='#111' font-size='22' text-anchor='middle' {_FONT}>👁</text>"
        "</svg>"
    )
