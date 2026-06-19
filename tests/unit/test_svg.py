"""Unit tests — SVG renderers and the gallery writer."""

import pytest
from fractalmusic.gallery import _stack, write_gallery
from fractalmusic.scales import mode_scale, penta
from fractalmusic.svg import (
    deck_grid,
    fretboard_stickers_svg,
    piano_stickers_svg,
    scale_strip,
)


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
        "deck.svg",
        "greek-modes.svg",
        "penta-modes.svg",
        "piano-stickers.svg",
        "fretboard-stickers.svg",
    }
    assert all(p.read_text().startswith("<svg") for p in paths)
