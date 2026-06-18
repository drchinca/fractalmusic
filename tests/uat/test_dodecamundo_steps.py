"""Step definitions for the Dodecamundo learning feature."""

import pytest
from fractalmusic.cartas import carta
from fractalmusic.dodecamundo import (
    DODECAMUNDO,
    heptatonic_worlds,
    pentatonic_worlds,
    world,
)
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("features/dodecamundo.feature")


@pytest.fixture
def ctx():
    return {}


@given("a fresh Dodecamundo")
def fresh_dodecamundo(ctx):
    ctx["worlds"] = DODECAMUNDO


@when("I look at the first world")
def first_world(ctx):
    ctx["world"] = ctx["worlds"][0]


@when("I count the worlds")
def count_worlds(ctx):
    ctx["count"] = len(ctx["worlds"])


@when(parsers.parse('I draw the carta for "{note}"'))
def draw_carta(ctx, note):
    ctx["world"] = world(note)
    ctx["carta"] = carta(ctx["world"])


@then(parsers.parse('its note is "{note}"'))
def its_note(ctx, note):
    assert ctx["world"].note == note


@then(parsers.parse('its mode is "{name}"'))
def its_mode(ctx, name):
    assert ctx["world"].mode.mode_name == name


@then(parsers.parse("there are {count:d} worlds in total"))
def total_worlds(ctx, count):
    assert ctx["count"] == count


@then(parsers.parse("{count:d} of them are pentatonic stars"))
def count_stars(ctx, count):
    assert len(pentatonic_worlds()) == count


@then(parsers.parse("{count:d} of them are natural notes"))
def count_naturals(ctx, count):
    assert len(heptatonic_worlds()) == count


@then(parsers.parse('the carta shows the glyph "{glyph}"'))
def carta_glyph(ctx, glyph):
    assert glyph in ctx["carta"]
    assert ctx["world"].glyph == glyph


@then(parsers.parse('the carta names the mode "{name}"'))
def carta_mode(ctx, name):
    assert ctx["world"].mode.mode_name == name


@then(parsers.parse('the carta shows the roman numeral "{roman}"'))
def carta_roman(ctx, roman):
    assert ctx["world"].roman == roman
