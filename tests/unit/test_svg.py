"""Unit tests — SVG renderers and the gallery writer."""

from fractalmusic.gallery import write_gallery
from fractalmusic.scales import mode_scale, penta
from fractalmusic.svg import deck_grid, gatople_wheel, scale_strip


def _is_svg(text: str) -> bool:
    return text.startswith("<svg") and text.rstrip().endswith("</svg>")


def test_wheel_is_valid_svg_with_all_glyphs():
    svg = gatople_wheel()
    assert _is_svg(svg)
    for glyph in ("⋮", "△", "□", "+", "♀", "↑", "↓", "★"):
        assert glyph in svg


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


def test_gallery_writes_four_files(tmp_path):
    paths = write_gallery(tmp_path)
    names = {p.name for p in paths}
    assert names == {"gatople-wheel.svg", "deck.svg", "greek-modes.svg", "penta-modes.svg"}
    assert all(p.read_text().startswith("<svg") for p in paths)
