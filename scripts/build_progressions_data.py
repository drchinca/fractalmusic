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
from typing import Final, TypedDict

from fractalmusic.modes import CHROMATIC_ORDER
from fractalmusic.wheel import Wheel

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


class StepInput(TypedDict):
    """The shape of a step entry in progressions.json (BE-side input)."""

    role: str
    glyph: str
    improvise_in: str
    bars: int
    hint: str


def _parse_improvise_in(text: str) -> tuple[str, str]:
    """Split 'A Eólico' / 'D# Penta 2' / 'C# Penta 1' into (note, mode_name)."""
    head, _, tail = text.partition(" ")
    return head, tail


# A-default wheel is the source of truth for `role_position` on the FE.
# Build a name->position lookup once so we don't rescan ALL_MODES per step.
_A_WHEEL: Final[Wheel] = Wheel(tonic="A")
_ROLE_POSITION_BY_MODE: Final[dict[str, int]] = {
    wm.role.mode_name: wm.role.position for wm in _A_WHEEL.all_modes()
}


def _resolve_step(
    step: StepInput,
    tonic_note: str,
    next_step: StepInput,
) -> BakedStep:
    """Expand one step at `tonic_note` via the canonical Wheel.

    `tonic_note` is the absolute pitch the step is rooted on — i.e. the
    note that, when placed under ⋮, makes this step's mode the Eólico
    relation of the wheel. The scale notes and the role identity come
    straight from `Wheel(tonic_note).mode_for(tonic_note)`, eliminating
    the hand-rolled transposition / step-pattern math.
    """
    _, mode_name = _parse_improvise_in(step["improvise_in"])
    _, next_mode_name = _parse_improvise_in(next_step["improvise_in"])

    # Spin the wheel so this step's tonic sits at Eólico. The role we
    # asked for (mode_name) is then bound to that note.
    wheel = Wheel(tonic=_step_root(step, tonic_note))
    wheel_mode = wheel.mode_for(tonic_note)
    if wheel_mode.mode_name != mode_name:
        raise ValueError(
            f"preset declares {mode_name!r} on {tonic_note!r}, "
            f"but Wheel says {wheel_mode.mode_name!r} — preset/wheel disagree"
        )

    return BakedStep(
        role_mode_name=mode_name,
        role_position=_ROLE_POSITION_BY_MODE[mode_name],
        display_glyph=step["glyph"],
        tonic_note=tonic_note,
        scale_notes=list(wheel_mode.scale_notes()),
        drone_octave=3,
        bars=step["bars"],
        hint=step["hint"],
        next_role_mode_name=next_mode_name,
        next_role_position=_ROLE_POSITION_BY_MODE[next_mode_name],
    )


def _step_root(step: StepInput, tonic_note: str) -> str:
    """The wheel-tonic that puts `tonic_note` under this step's mode.

    For Eólico this is `tonic_note` itself; for Dórico it's tonic_note - 2
    semitones (so D under +/Dórico means the wheel is tonic'd to C…
    no wait, A — see Wheel docstring). We solve generally by walking
    the role's offset back to position 0.
    """
    _, mode_name = _parse_improvise_in(step["improvise_in"])
    role_offset = _ROLE_POSITION_BY_MODE[mode_name]
    tonic_idx = CHROMATIC_ORDER.index(tonic_note)
    wheel_root_idx = (tonic_idx - role_offset) % 12
    return CHROMATIC_ORDER[wheel_root_idx]


def _transpose_tonic(step: StepInput, delta_semitones: int) -> str:
    """The step's tonic note, shifted by `delta_semitones` around the wheel."""
    bundled_note, _ = _parse_improvise_in(step["improvise_in"])
    bundled_idx = CHROMATIC_ORDER.index(bundled_note)
    return CHROMATIC_ORDER[(bundled_idx + delta_semitones) % 12]


def build_baked() -> BakedProgressionsPayload:
    """Read progressions.json, expand every preset to all 12 keys."""
    presets = json.loads(PRESETS_PATH.read_text())
    out_progs: list[BakedProgression] = []
    for prog in presets["progressions"]:
        steps: list[StepInput] = list(prog["steps"])
        # Preset's bundled home tonic = first step's tonic.
        home_note, _ = _parse_improvise_in(steps[0]["improvise_in"])
        home_offset = CHROMATIC_ORDER.index(home_note)

        keys: list[list[BakedStep]] = []
        for tonic_offset in range(12):
            delta = (tonic_offset - home_offset + 12) % 12
            baked_steps: list[BakedStep] = []
            for i, step in enumerate(steps):
                next_step = steps[(i + 1) % len(steps)]
                baked_steps.append(
                    _resolve_step(
                        step,
                        tonic_note=_transpose_tonic(step, delta),
                        next_step=next_step,
                    )
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
