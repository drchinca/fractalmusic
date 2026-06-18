"""The 12-segment chromatic color wheel of the Gátople.

Colors follow the cues given in *El Sistema Fractal* Ch. 8 "Música de Colores"
and the Gátople logo: the penta worlds carry blues/violets ("el color azul del
penta"), Mixolidio pulls down with a green force, the lower house (Penta 3, "casa
de Gátople") is the heaviest red/earth-fire. Where the book is not explicit, hue
follows the chromatic A-order wheel (A = 0°, +30° per semitone).

These remain an interpretation of the hand-painted cartas; swap WHEEL_HEX with
the exact card palette when the originals are digitized.
"""

from typing import Final

# Per-note hex, A-indexed. Cues from the logo + Ch. 8 descriptions.
WHEEL_HEX: Final[tuple[str, ...]] = (
    "#3FA34D",  # A  Eólico    — green (stable horizon / earth-mountain)
    "#E03C8A",  # A# Penta 5   — magenta-pink
    "#8FD14F",  # B  Locrio    — yellow-green (sensible of Jónico)
    "#E6D72A",  # C  Jónico    — yellow (verticality, the major)
    "#3FB68B",  # C# Penta 1   — teal
    "#2E86C1",  # D  Dórico    — blue (cross / opening)
    "#1F4FD8",  # D# Penta 2   — deep blue
    "#7D5BA6",  # E  Frigio    — violet (closing key)
    "#5B6CC4",  # F  Lidio     — indigo (hepta→penta hybrid)
    "#9B59B6",  # F# Penta 3   — purple (casa de Gátople, earth+fire)
    "#E67E22",  # G  Mixolidio — orange (descending / compression)
    "#E74C3C",  # G# Penta 4   — red
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
