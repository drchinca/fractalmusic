"""Unit tests — SVG renderers and the gallery writer."""

import math

import pytest
from fractalmusic.gallery import _stack, write_gallery
from fractalmusic.scales import mode_scale, penta
from fractalmusic.svg import (
    _arc_path,
    _contrast,
    _polar,
    deck_grid,
    fretboard_stickers_svg,
    gatople_wheel_svg,
    piano_stickers_svg,
    scale_strip,
)
from fractalmusic.wheel import Wheel


def _is_svg(text: str) -> bool:
    return text.startswith("<svg") and text.rstrip().endswith("</svg>")


def test_deck_grid_has_twelve_number_labels():
    svg = deck_grid()
    assert _is_svg(svg)
    for number in range(1, 13):
        assert f">{number}<" in svg


def test_scale_strip_names_the_mode():
    assert ">Jónico<" in scale_strip(mode_scale("C"))


def test_penta_strip_is_all_stars():
    svg = scale_strip(penta("C#", mode="I"))
    assert svg.count("★") == 5


def test_piano_stickers_render_all_twelve_worlds():
    svg = piano_stickers_svg()
    assert _is_svg(svg)
    for glyph in ("⋮", "△", "□", "+", "♀", "↑", "↓", "★"):
        assert glyph in svg


def test_fretboard_stickers_render_open_and_frets():
    svg = fretboard_stickers_svg(frets=12)
    assert _is_svg(svg)
    assert ">12<" in svg  # 12th-fret label present


def test_stack_rejects_svg_without_dimensions():
    with pytest.raises(ValueError, match="width/height"):
        _stack(["<svg></svg>"])


def test_gallery_writes_all_artifacts(tmp_path):
    paths = write_gallery(tmp_path)
    names = {p.name for p in paths}
    assert names == {
        "gatople-wheel.svg",
        "deck.svg",
        "greek-modes.svg",
        "penta-modes.svg",
        "piano-stickers.svg",
        "fretboard-stickers.svg",
    }
    assert all(p.read_text().startswith("<svg") for p in paths)


def test_contrast_picks_dark_text_on_light_fill():
    assert _contrast("#FFFFFF") == "#111"


def test_contrast_picks_light_text_on_dark_fill():
    assert _contrast("#000000") == "#fff"


def test_polar_zero_degrees_points_straight_up():
    # deg=0 is the hour-12 direction; SVG y grows downward, so "up" is -y.
    x, y = _polar(0, 100)
    assert math.isclose(x, 0.0, abs_tol=1e-9)
    assert math.isclose(y, -100.0)


def test_polar_ninety_degrees_points_right():
    x, y = _polar(90, 100)
    assert math.isclose(x, 100.0)
    assert math.isclose(y, 0.0, abs_tol=1e-9)


def test_arc_path_uses_small_arc_flag_under_180_degrees():
    path = _arc_path(0, 30, 100, 50)
    assert "A 100 100 0 0 1" in path
    assert "A 50 50 0 0 0" in path


def test_arc_path_uses_large_arc_flag_over_180_degrees():
    path = _arc_path(0, 200, 100, 50)
    assert "A 100 100 0 1 1" in path
    assert "A 50 50 0 1 0" in path


def test_arc_path_uses_small_arc_flag_at_exactly_180_degrees():
    # Boundary case: a span of exactly 180° is not "over 180", so it must
    # still take the small-arc flag — this is what distinguishes `> 180`
    # from `>= 180` in the flag condition.
    path = _arc_path(0, 180, 100, 50)
    assert "A 100 100 0 0 1" in path
    assert "A 50 50 0 0 0" in path


def test_gatople_wheel_svg_renders_deterministic_geometry():
    wheel = Wheel("D")
    svg = gatople_wheel_svg(wheel)
    assert _is_svg(svg)
    # The SVG should contain the custom math-drawn center eye
    assert ">👁<" in svg
    # The SVG should contain the twelve roles
    for glyph in ("⋮", "△", "□", "+", "♀", "↑", "↓", "★"):
        assert f">{glyph}<" in svg
    # Under a D-tonic rotation, D should be visible
    assert ">D<" in svg
