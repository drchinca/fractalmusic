"""Step definitions for the composing-with-the-Gátople feature."""

import pytest
from fractalmusic.cartas import spell
from fractalmusic.dodecamundo import DODECAMUNDO
from fractalmusic.gatople import cero_pitagoras, interval_angle
from fractalmusic.scales import PENTA_MODES, microstructures, penta
from pytest_bdd import given, parsers, scenarios, then, when

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
