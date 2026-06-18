#!/usr/bin/env python3
"""Regenerate docs/gatople/data.json from the canonical Wheel data.

Run after any change to fractalmusic.modes / fractalmusic.colors so the
interactive page stays in sync with the Python data model::

    uv run python scripts/build_gatople_data.py
"""

import json
from pathlib import Path

from fractalmusic.colors import CARTA_HEX, GLYPH_FG, WHEEL_HEX
from fractalmusic.modes import CHROMATIC_ORDER, PENTA_ROOTS
from fractalmusic.wheel import ROLES

CARTA_NAMES: tuple[str, ...] = (
    "Dos Puntos",
    "Estrella V",
    "Triángulo",
    "Casita",
    "Estrella I",
    "Más",
    "Estrella II",
    "Llave",
    "Flecha arriba",
    "Estrella III",
    "Flecha abajo",
    "Estrella IV",
)


def build_payload() -> dict[str, object]:
    """Snapshot ROLES + the canonical palette + carta names as JSON-ready data."""
    penta_label = {note: roman for roman, note in PENTA_ROOTS}
    roles: list[dict[str, object]] = []
    for role in ROLES:
        note = CHROMATIC_ORDER[role.position]
        is_penta = role.family == "penta"
        roman = penta_label.get(note) if is_penta else None
        # Fully-baked display fields — the frontend is a dumb renderer.
        display_glyph = f"★{roman}" if is_penta else role.glyph
        display_label = roman if is_penta else note
        glyph_fg = GLYPH_FG[display_glyph]
        roles.append(
            {
                "position": role.position,
                "note_default": note,
                "mode_name": role.mode_name,
                "glyph": role.glyph,  # raw Unicode glyph (no roman)
                "display_glyph": display_glyph,  # what the FE prints (e.g. "★III")
                "display_label": display_label,  # note for hepta, roman for penta
                "family": role.family,
                "quality": role.quality,
                "clock_hour": role.clock_hour,
                "scale_steps": list(role.scale_steps),
                "wheel_color": WHEEL_HEX[role.position],
                "carta_color": CARTA_HEX[role.position],
                "glyph_fg": glyph_fg,
                "carta_name": CARTA_NAMES[role.position],
                "is_penta": is_penta,
                "roman": roman,
            }
        )
    return {
        "chromatic": list(CHROMATIC_ORDER),
        "roles": roles,
        "penta_roots": [{"roman": roman, "note": note} for roman, note in PENTA_ROOTS],
    }


def main() -> None:
    """Write docs/gatople/data.json beside the package root."""
    repo_root = Path(__file__).resolve().parent.parent
    out = repo_root / "docs" / "gatople" / "data.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_payload(), indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {out.relative_to(repo_root)} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
