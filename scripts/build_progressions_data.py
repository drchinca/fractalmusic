#!/usr/bin/env python3
"""Pre-bake all 12 transpositions of every progression for the FE.

The frontend (docs/gatople/compose.js) has zero music-theory logic — it just
renders whatever the BE hands it. This script reads progressions.json (the
hand-curated, book-sourced presets), then for each preset × each of the 12
chromatic tonics, expands every step into a fully-resolved BakedStep with
scale notes, drone tonic, glyphs, etc.

Run after editing progressions.json or any of the canonical bindings::

    uv run python scripts/build_progressions_data.py

The on-disk artifact lives at docs/gatople/progressions_baked.json. A
companion drift test in tests/integration/ guards staleness.
"""

import json
from pathlib import Path
from typing import TypedDict

from fractalmusic.modes import ALL_MODES, CHROMATIC_ORDER
from fractalmusic.wheel import Wheel  # noqa: F401 — re-exported for callers

REPO_ROOT = Path(__file__).resolve().parent.parent
PRESETS_PATH = REPO_ROOT / "docs" / "gatople" / "progressions.json"
OUT_PATH = REPO_ROOT / "docs" / "gatople" / "progressions_baked.json"


class BakedStep(TypedDict):
    """One step in one tonic, fully resolved by the canonical Wheel."""

    role_mode_name: str
    role_position: int  # 0..11, the role's chromatic offset from Eólico
    display_glyph: str
    tonic_note: str  # the absolute pitch this step is rooted on
    scale_notes: list[str]  # the in-scale notes at this rotation
    drone_octave: int
    bars: int
    hint: str
    next_role_mode_name: str
    next_role_position: int


class BakedProgression(TypedDict):
    """A progression, expanded to all 12 keys."""

    id: str
    name: str
    summary: str
    book_ref: list[str]
    home_tonic: str  # the bundled key the preset opens at
    home_offset: int  # CHROMATIC_ORDER index of home_tonic
    keys: list[list[BakedStep]]  # 12 entries, one per tonic_offset 0..11


class BakedProgressionsPayload(TypedDict):
    """Top-level shape of progressions_baked.json."""

    chromatic: list[str]
    progressions: list[BakedProgression]


def _parse_improvise_in(text: str) -> tuple[str, str]:
    """Split 'A Eólico' / 'D# Penta 2' / 'C# Penta 1' into (note, mode_name)."""
    head, _, tail = text.partition(" ")
    return head, tail


def _step_pattern(mode_name: str) -> list[int]:
    """Semitone step pattern for a mode, derived from its canonical note_order.

    e.g. Dórico note_order is ('D','E','F','G','A','B','C'); the chromatic
    indices are (5,7,8,10,0,2,3); the steps are [2,1,2,2,2,1] (six gaps for
    seven notes). The mode walks its own pattern from any root.
    """
    mode = next(m for m in ALL_MODES if m.mode_name == mode_name)
    indices = [CHROMATIC_ORDER.index(n) for n in mode.note_order]
    return [(indices[i + 1] - indices[i]) % 12 for i in range(len(indices) - 1)]


def _walk_scale(mode_name: str, root_note: str) -> list[str]:
    """Walk the scale of mode `mode_name` starting from `root_note`.

    The mode supplies the step pattern (e.g. Dórico = [2,1,2,2,2,1]); the
    root supplies the starting pitch. Together they produce the absolute
    scale spelling at that key.
    """
    out = [root_note]
    idx = CHROMATIC_ORDER.index(root_note)
    for step in _step_pattern(mode_name):
        idx = (idx + step) % 12
        out.append(CHROMATIC_ORDER[idx])
    return out


def _role_position(mode_name: str) -> int:
    """Default chromatic position of the role named `mode_name`."""
    mode = next(m for m in ALL_MODES if m.mode_name == mode_name)
    return CHROMATIC_ORDER.index(mode.note)


def _resolve_step(
    step: dict[str, object],
    tonic_offset: int,
    home_offset: int,
    next_step: dict[str, object],
) -> BakedStep:
    """Expand one step at a given tonic offset."""
    bundled_note, mode_name = _parse_improvise_in(str(step["improvise_in"]))
    bundled_idx = CHROMATIC_ORDER.index(bundled_note)
    # Transposition: wheel-spun by `tonic_offset` from the preset's home_offset
    # means every step shifts by the same delta in semitones.
    delta = (tonic_offset - home_offset + 12) % 12
    tonic_note = CHROMATIC_ORDER[(bundled_idx + delta) % 12]

    next_bundled_note, next_mode_name = _parse_improvise_in(str(next_step["improvise_in"]))

    return BakedStep(
        role_mode_name=mode_name,
        role_position=_role_position(mode_name),
        display_glyph=str(step["glyph"]),
        tonic_note=tonic_note,
        scale_notes=_walk_scale(mode_name, tonic_note),
        drone_octave=3,
        bars=int(step["bars"]),  # type: ignore[call-overload]  # JSON value is int; mypy sees object
        hint=str(step["hint"]),
        next_role_mode_name=next_mode_name,
        next_role_position=_role_position(next_mode_name),
    )


def build_baked() -> BakedProgressionsPayload:
    """Read progressions.json, expand every preset to all 12 keys."""
    presets = json.loads(PRESETS_PATH.read_text())
    out_progs: list[BakedProgression] = []
    for prog in presets["progressions"]:
        steps = list(prog["steps"])
        # Preset's bundled home tonic = first step's tonic.
        home_note, _ = _parse_improvise_in(steps[0]["improvise_in"])
        home_offset = CHROMATIC_ORDER.index(home_note)

        keys: list[list[BakedStep]] = []
        for tonic_offset in range(12):
            baked_steps: list[BakedStep] = []
            for i, step in enumerate(steps):
                next_step = steps[(i + 1) % len(steps)]
                baked_steps.append(
                    _resolve_step(step, tonic_offset, home_offset, next_step)
                )
            keys.append(baked_steps)

        out_progs.append(
            BakedProgression(
                id=prog["id"],
                name=prog["name"],
                summary=prog["summary"],
                book_ref=list(prog["book_ref"]),
                home_tonic=home_note,
                home_offset=home_offset,
                keys=keys,
            )
        )
    return BakedProgressionsPayload(
        chromatic=list(CHROMATIC_ORDER),
        progressions=out_progs,
    )


def main() -> None:
    """Write progressions_baked.json beside the static frontend assets."""
    payload = build_baked()
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUT_PATH.relative_to(REPO_ROOT)} ({OUT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
