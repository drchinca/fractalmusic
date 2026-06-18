"""Generate the SVG visual gallery (wheel, deck, Greek + Penta mode charts).

    python -m fractalmusic.gallery [output_dir]
"""

import re
import sys
from pathlib import Path

from fractalmusic.scales import mode_scale, penta
from fractalmusic.svg import deck_grid, gatople_wheel, scale_strip

_DEFAULT_DIR = Path("docs/assets")
_GREEK_ROOTS = ("A", "B", "C", "D", "E", "F", "G")
_PENTA_ROOTS = (("I", "C#"), ("II", "D#"), ("III", "F#"), ("IV", "G#"), ("V", "A#"))


def _stack(svgs: list[str], *, gap: int = 8) -> str:
    """Stack standalone SVG strings vertically into one SVG."""
    bodies: list[str] = []
    y = 0
    max_w = 0
    for svg in svgs:
        width_match = re.search(r"width='(\d+)'", svg)
        height_match = re.search(r"height='(\d+)'", svg)
        assert width_match and height_match  # svg.py always emits both
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
    artifacts = {
        "gatople-wheel.svg": gatople_wheel(),
        "deck.svg": deck_grid(),
        "greek-modes.svg": _stack([scale_strip(mode_scale(n)) for n in _GREEK_ROOTS]),
        "penta-modes.svg": _stack(
            [scale_strip(penta(root, mode=roman)) for roman, root in _PENTA_ROOTS]
        ),
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
