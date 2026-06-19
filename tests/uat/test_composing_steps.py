"""Step definitions for the composing-with-the-Gátople feature."""

import json
import sys
from pathlib import Path

import pytest
from fractalmusic.cartas import spell
from fractalmusic.dodecamundo import DODECAMUNDO
from fractalmusic.gatople import cero_pitagoras, interval_angle
from fractalmusic.scales import PENTA_MODES, microstructures, penta
from pytest_bdd import given, parsers, scenarios, then, when

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build_progressions_data import build_baked  # noqa: E402

scenarios("features/composing.feature")


@pytest.fixture
def ctx():
    return {}


@given("a fresh Dodecamundo")
def fresh_dodecamundo(ctx):
    ctx["worlds"] = DODECAMUNDO


@when(parsers.parse('I perform Cero Pitágoras from "{root}"'))
def do_cero_pitagoras(ctx, root):
    ctx["seed"] = cero_pitagoras(root)


@when(parsers.parse('I build all five pentatonic modes on "{root}"'))
def build_all_penta(ctx, root):
    ctx["scales"] = [penta(root, mode=m) for m in PENTA_MODES]


@when("I generate every pentatonic microstructure")
def generate_microstructures(ctx):
    ctx["micro"] = microstructures()


@when(parsers.parse('I measure the angle from "{a}" to "{b}"'))
def measure_angle(ctx, a, b):
    ctx["angle"] = interval_angle(a, b)


@when(parsers.parse('I spell the chord "{notes}"'))
def spell_chord(ctx, notes):
    ctx["glyphs"] = spell(notes.split())


@then("I get a 5-note pentatonic seed")
def seed_is_five(ctx):
    assert len(ctx["seed"]) == 5


@then("the seed has no semitone steps")
def seed_no_semitone(ctx):
    from fractalmusic.dodecamundo import world

    indices = [world(n).index for n in ctx["seed"]]
    steps = [(b - a) % 12 for a, b in zip(indices, indices[1:], strict=False)]
    assert 1 not in steps


@then("none of them contains a semitone step")
def none_semitone(ctx):
    assert all(s.has_semitone is False for s in ctx["scales"])


@then(parsers.parse("there are {count:d} microstructures"))
def count_microstructures(ctx, count):
    assert len(ctx["micro"]) == count


@then(parsers.parse("the angle is {degrees:d} degrees"))
def angle_is(ctx, degrees):
    assert ctx["angle"] == float(degrees)


@then(parsers.parse('it reads "{glyphs}" in glyphs'))
def reads_glyphs(ctx, glyphs):
    assert ctx["glyphs"] == glyphs


# ----- Book-sourced progressions (baked in all 12 keys) -----


CHROMATIC: list[str] = [
    "A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#",
]


@given("the baked progressions")
def load_baked(ctx):
    payload = build_baked()
    ctx["baked"] = {p["id"]: p for p in payload["progressions"]}


@when(parsers.parse('I spin "{prog_id}" to "{tonic}"'))
def spin_one(ctx, prog_id, tonic):
    prog = ctx["baked"][prog_id]
    tonic_offset = CHROMATIC.index(tonic)
    ctx["steps"] = prog["keys"][tonic_offset]


@when("I spin every progression to every key")
def spin_all(ctx):
    ctx["all_steps"] = [
        step
        for prog in ctx["baked"].values()
        for key in prog["keys"]
        for step in key
    ]


@then(parsers.parse('the first step is rooted on "{note}"'))
def first_step_root(ctx, note):
    assert ctx["steps"][0]["tonic_note"] == note


@then(parsers.parse('the first step\'s mode is "{mode}"'))
def first_step_mode(ctx, mode):
    assert ctx["steps"][0]["role_mode_name"] == mode


@then(parsers.parse('the last step is rooted on "{note}"'))
def last_step_root(ctx, note):
    assert ctx["steps"][-1]["tonic_note"] == note


@then(parsers.parse('step {n:d} is rooted on "{note}"'))
def step_n_root(ctx, n, note):
    assert ctx["steps"][n - 1]["tonic_note"] == note


@then(parsers.parse('step {n:d}\'s mode is "{mode}"'))
def step_n_mode(ctx, n, mode):
    assert ctx["steps"][n - 1]["role_mode_name"] == mode


@then(parsers.parse("the progression has {n:d} steps"))
def step_count(ctx, n):
    assert len(ctx["steps"]) == n


@then("every step has a unique mode")
def unique_modes(ctx):
    modes = [s["role_mode_name"] for s in ctx["steps"]]
    assert len(set(modes)) == len(modes), modes


@then("every step has a unique tonic")
def unique_tonics(ctx):
    tonics = [s["tonic_note"] for s in ctx["steps"]]
    assert len(set(tonics)) == len(tonics), tonics


@then("every step's scale is exactly seven or five notes")
def scale_size(ctx):
    sizes = {len(s["scale_notes"]) for s in ctx["all_steps"]}
    assert sizes <= {5, 7}, sizes


@then("every step's scale has no repeated notes")
def scale_unique(ctx):
    for step in ctx["all_steps"]:
        scale = step["scale_notes"]
        assert len(set(scale)) == len(scale), step
