"""Unit tests — hex parsing and ANSI truecolor contrast selection."""

from fractalmusic.colors import ansi_bg, hex_to_rgb


def test_hex_to_rgb_parses_hash_prefixed():
    assert hex_to_rgb("#2BA39A") == (43, 163, 154)


def test_hex_to_rgb_parses_bare_hex():
    assert hex_to_rgb("2BA39A") == (43, 163, 154)


def test_ansi_bg_picks_dark_text_on_light_background():
    # White is maximum luminance: dark foreground (ANSI code 30).
    assert ansi_bg("#FFFFFF", "X") == "\033[48;2;255;255;255m\033[30mX\033[0m"


def test_ansi_bg_picks_light_text_on_dark_background():
    # Black is minimum luminance: light foreground (ANSI code 97).
    assert ansi_bg("#000000", "X") == "\033[48;2;0;0;0m\033[97mX\033[0m"


def test_ansi_bg_resets_at_the_end():
    assert ansi_bg("#2BA39A", "hello").endswith("\033[0m")
