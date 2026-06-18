"""Generate the SVG visual gallery (wheel, deck, Greek + Penta mode charts).

    python -m fractalmusic.gallery [output_dir]
"""

import re
import sys
from pathlib import Path

from fractalmusic.modes import PENTA_ROOTS
from fractalmusic.scales import mode_scale, penta
from fractalmusic.svg import (
    deck_grid,
    fretboard_stickers_svg,
    piano_stickers_svg,
    scale_strip,
)

# Anchor the default output to the repo's docs/assets, not the caller's CWD, so
# the gallery never scatters files into an arbitrary working directory.
_DEFAULT_DIR = Path(__file__).resolve().parent.parent / "docs" / "assets"
_GREEK_ROOTS = ("A", "B", "C", "D", "E", "F", "G")


def _stack(svgs: list[str], *, gap: int = 8) -> str:
    """Stack standalone SVG strings vertically into one SVG."""
    bodies: list[str] = []
    y = 0
    max_w = 0
    for svg in svgs:
        width_match = re.search(r"width='(\d+)'", svg)
        height_match = re.search(r"height='(\d+)'", svg)
        if not (width_match and height_match):
            raise ValueError("svg is missing width/height attributes")
        width = int(width_match.group(1))
        height = int(height_match.group(1))
        inner = re.sub(r"^<svg[^>]*>", "", svg)
        inner = re.sub(r"</svg>$", "", inner)
        bodies.append(f"<g transform='translate(0,{y})'>{inner}</g>")
        y += height + gap
        max_w = max(max_w, width)
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{max_w}' height='{y}' "
        f"viewBox='0 0 {max_w} {y}'><rect width='{max_w}' height='{y}' fill='#fff'/>"
        + "".join(bodies)
        + "</svg>"
    )


def write_gallery(out_dir: Path = _DEFAULT_DIR) -> list[Path]:
    """Write all gallery SVGs and return the paths written."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    # The Gátople wheel renderer is omitted while it is rebuilt to honor the
    # two-disc (fixed outer / rotating inner) model — see fractalmusic.wheel.
    artifacts = {
        "deck.svg": deck_grid(),
        "greek-modes.svg": _stack([scale_strip(mode_scale(n)) for n in _GREEK_ROOTS]),
        "penta-modes.svg": _stack(
            [scale_strip(penta(root, mode=roman)) for roman, root in PENTA_ROOTS]
        ),
        "piano-stickers.svg": piano_stickers_svg(),
        "fretboard-stickers.svg": fretboard_stickers_svg(),
    }
    for name, svg in artifacts.items():
        path = out_dir / name
        path.write_text(svg)
        written.append(path)
    return written


def main() -> None:
    """CLI entry — write the gallery to the given (or default) directory."""
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else _DEFAULT_DIR
    paths = write_gallery(target)
    print("wrote:", ", ".join(p.name for p in paths), f"→ {target}/")


if __name__ == "__main__":
    main()
