"""The 12-segment color wheel of the Gátople — canonical palette from the cartas.

Hex values are eyeballed from the dominant fields of Patricio Torres's
hand-painted 12-card deck (digitized 2026-06):

    1  ⋮  Dos Puntos     A    red ("dos puntos" on red)
    2  ★  Estrella V     A#   deep blue (water + window)
    3  △  Triángulo      B    green (white triangle on green field)
    4  ■  Casita         C    red roof + ivory wall + yellow door
    5  ★  Estrella I     C#   water blue + sunset orange (pelicans + boat)
    6  +  Más / Cruz     D    green (red flowers on green field)
    7  ★  Estrella II    D#   blue + orange sun (horizon + fish)
    8  ♀  Llave (koppa)  E    red (skeleton key on red)
    9  ↑  Flecha arriba  F    blue (sky / snow mountain)
    10 ★  Estrella III   F#   red (casa de Gátople — earth + fire)
    11 ↓  Flecha abajo   G    green (green fields, ant on string, moon)
    12 ★  Estrella IV    G#   blue + orange reflection (water table, drums)

Where a card has two dominant colors, ``WHEEL_HEX`` keeps the field/background
hue (the strongest reading from across the room).
"""

from typing import Final

# A-indexed canonical palette read directly from the 12 cartas.
WHEEL_HEX: Final[tuple[str, ...]] = (
    "#D43A2C",  # A  Eólico    Dos Puntos — red
    "#1B3A8C",  # A# Penta 5   Estrella V — deep blue
    "#3FA34D",  # B  Locrio    Triángulo — green
    "#F2E6D8",  # C  Jónico    Casita — ivory wall (the field; red roof is accent)
    "#3FA0C9",  # C# Penta 1   Estrella I — water blue
    "#3FA34D",  # D  Dórico    Más — green
    "#2E70C1",  # D# Penta 2   Estrella II — blue
    "#D43A2C",  # E  Frigio    Llave — red
    "#3FA0C9",  # F  Lidio     Flecha arriba — blue
    "#C0382C",  # F# Penta 3   Estrella III — red (casa de Gátople)
    "#3FA34D",  # G  Mixolidio Flecha abajo — green
    "#2E70C1",  # G# Penta 4   Estrella IV — blue
)

DEGREES_PER_SEMITONE: Final[int] = 30  # 360° / 12 worlds


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    """Parse ``#RRGGBB`` into an (r, g, b) tuple."""
    cleaned = value.lstrip("#")
    return (int(cleaned[0:2], 16), int(cleaned[2:4], 16), int(cleaned[4:6], 16))


def ansi_bg(hex_color: str, text: str) -> str:
    """Wrap text in a 24-bit ANSI truecolor background, auto-picking fg contrast."""
    red, green, blue = hex_to_rgb(hex_color)
    luminance = (0.299 * red + 0.587 * green + 0.114 * blue) / 255.0
    fg = "30" if luminance > 0.55 else "97"
    return f"\033[48;2;{red};{green};{blue}m\033[{fg}m{text}\033[0m"
