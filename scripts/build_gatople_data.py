#!/usr/bin/env python3
"""Regenerate docs/gatople/data.json from the canonical Wheel data.

Run after any change to fractalmusic.modes / fractalmusic.colors so the
interactive page stays in sync with the Python data model::

    uv run python scripts/build_gatople_data.py
"""

import json
from pathlib import Path
from typing import TypedDict

from fractalmusic.colors import CARTA_HEX, GLYPH_FG, WHEEL_HEX
from fractalmusic.modes import CHROMATIC_ORDER, PENTA_ROOTS
from fractalmusic.wheel import ROLES


class RoleEntry(TypedDict):
    """One role's serialized shape — every field the FE needs, fully baked."""

    position: int
    note_default: str
    mode_name: str
    glyph: str
    display_glyph: str
    display_label: str
    family: str
    quality: str
    clock_hour: int
    scale_steps: list[int]
    wheel_color: str
    carta_color: str
    glyph_fg: str
    carta_name: str
    is_penta: bool
    roman: str | None


class PentaRootEntry(TypedDict):
    """One penta root binding (roman ↔ canonical black-key note)."""

    roman: str
    note: str


class GatoplePayload(TypedDict):
    """Top-level shape of docs/gatople/data.json."""

    chromatic: list[str]
    roles: list[RoleEntry]
    penta_roots: list[PentaRootEntry]

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


def build_payload() -> GatoplePayload:
    """Snapshot ROLES + the canonical palette + carta names as JSON-ready data."""
    penta_label = {note: roman for roman, note in PENTA_ROOTS}
    roles: list[RoleEntry] = []
    for role in ROLES:
        note = CHROMATIC_ORDER[role.position]
        is_penta = role.family == "penta"
        roman = penta_label.get(note) if is_penta else None
        # Fully-baked display fields — the frontend is a dumb renderer.
        display_glyph = f"★{roman}" if is_penta else role.glyph
        display_label: str = roman if (is_penta and roman is not None) else note
        glyph_fg = GLYPH_FG[display_glyph]
        roles.append(
            RoleEntry(
                position=role.position,
                note_default=note,
                mode_name=role.mode_name,
                glyph=role.glyph,
                display_glyph=display_glyph,
                display_label=display_label,
                family=role.family,
                quality=role.quality,
                clock_hour=role.clock_hour,
                scale_steps=list(role.scale_steps),
                wheel_color=WHEEL_HEX[role.position],
                carta_color=CARTA_HEX[role.position],
                glyph_fg=glyph_fg,
                carta_name=CARTA_NAMES[role.position],
                is_penta=is_penta,
                roman=roman,
            )
        )
    penta_roots: list[PentaRootEntry] = [
        PentaRootEntry(roman=roman, note=note) for roman, note in PENTA_ROOTS
    ]
    return GatoplePayload(
        chromatic=list(CHROMATIC_ORDER),
        roles=roles,
        penta_roots=penta_roots,
    )


def main() -> None:
    """Write docs/gatople/data.json beside the package root."""
    repo_root = Path(__file__).resolve().parent.parent
    out = repo_root / "docs" / "gatople" / "data.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_payload(), indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {out.relative_to(repo_root)} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
