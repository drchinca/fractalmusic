"""Two distinct color systems. They are NOT the same palette.

1. ``WHEEL_HEX`` — the 12 segments INSIDE the Gátople cat-face mandala. This is
   a CHROMATIC GRADIENT laid out by clock hour: yellow at 12, orange at 1,
   red at 4, violet at 6, blue at 8, green at 10, yellow-green at 11, back to
   yellow at 12. Pulled directly from the canonical Logo Gátople artwork.
   Used by: the spinning interactive wheel (docs/gatople/).

2. ``CARTA_HEX`` — the 12 hand-painted cards as standalone artworks. The
   palette here is mostly RED / GREEN / BLUE / WHITE-BLACK-IVORY (the cover
   legend's four-color rule), e.g. ⋮ Dos Puntos on red, ▲ Triángulo on green,
   ↑ Flecha arriba on blue, ■ Casita with red roof + ivory wall.
   Used by: piano stickers, fretboard stickers, mode strips — the
   educational sticker overlays a student would print and place.
"""

from typing import Final

# Canonical Gátople-logo gradient. The hue ROTATES around the wheel by clock
# hour (yellow→orange→red→pink→violet→blue→teal→green→yellow-green→yellow),
# NOT by chromatic-A index. The list below is keyed by chromatic-A index for
# back-compat with WHEEL_HEX consumers; each entry's color is the segment color
# at that note's clock hour in the canonical logo.
#
#   hour 12 (C)   yellow               #E8E66A
#   hour 1  (F)   orange               #F0A85A
#   hour 2  (A♯)  deeper orange        #F08A4A
#   hour 3  (D♯)  pink/coral           #F4B5B0
#   hour 4  (G♯)  red                  #DC4A38
#   hour 5  (C♯)  pale pink/lavender   #EFC4DA
#   hour 6  (F♯)  violet               #B687C6
#   hour 7  (B)   light blue           #BFD8E8
#   hour 8  (E)   slate blue           #6F86B8
#   hour 9  (A)   teal/blue-green      #2BA39A
#   hour 10 (D)   green-teal           #4FB387
#   hour 11 (G)   yellow-green/lime    #B5D04A
WHEEL_HEX: Final[tuple[str, ...]] = (
    "#2BA39A",  # A   hour 9   teal
    "#F08A4A",  # A#  hour 2   deeper orange
    "#BFD8E8",  # B   hour 7   light blue
    "#E8E66A",  # C   hour 12  yellow
    "#EFC4DA",  # C#  hour 5   pale pink/lavender
    "#4FB387",  # D   hour 10  green-teal
    "#F4B5B0",  # D#  hour 3   pink/coral
    "#6F86B8",  # E   hour 8   slate blue
    "#F0A85A",  # F   hour 1   orange
    "#B687C6",  # F#  hour 6   violet
    "#B5D04A",  # G   hour 11  yellow-green/lime
    "#DC4A38",  # G#  hour 4   red
)

# Glyph-foreground colors from the canonical logo (the ring shows the segment
# fill, but the glyph drawn OUTSIDE the ring on the cat body is in one of four
# colors only): red, green, blue, or — uniquely for ★III — red. Stars on the
# 4 other Penta cells are deep blue; the III star matches the red square at 12.
GLYPH_FG: Final[dict[str, str]] = {
    "⋮": "#D43A2C",  # red
    "★V": "#1B3A8C",  # deep blue
    "△": "#3FA34D",  # green
    "□": "#D43A2C",  # red — the Casita glyph (matches the red square in legend)
    "★I": "#1B3A8C",  # deep blue
    "+": "#3FA34D",  # green
    "★II": "#1B3A8C",  # deep blue
    "♀": "#D43A2C",  # red
    "↑": "#1B3A8C",  # deep blue
    "★III": "#D43A2C",  # RED — the casa-de-Gátople pair with the red □
    "↓": "#3FA34D",  # green
    "★IV": "#1B3A8C",  # deep blue
}


# Carta palette — the cover-legend four-color rule (red / green / blue /
# white-black-ivory). Used for the educational sticker overlays (piano,
# fretboard, mode strips). Each entry is the dominant background of the
# corresponding card in the digitized deck.
RED: Final[str] = "#D43A2C"
GREEN: Final[str] = "#3FA34D"
BLUE: Final[str] = "#2E70C1"
DEEP_BLUE: Final[str] = "#1B3A8C"
WATER_BLUE: Final[str] = "#3FA0C9"
SKY_BLUE: Final[str] = "#7CB6E0"
IVORY: Final[str] = "#F2E6D8"

CARTA_HEX: Final[tuple[str, ...]] = (
    RED,  # A   ⋮ Dos Puntos    on red
    DEEP_BLUE,  # A#  ★V Estrella V   on deep blue
    GREEN,  # B   △ Triángulo      on green
    IVORY,  # C   ■ Casita         ivory wall (red roof accent)
    WATER_BLUE,  # C#  ★I Estrella I    water blue
    GREEN,  # D   + Más            on green
    BLUE,  # D#  ★II Estrella II  blue + orange sun
    RED,  # E   ♀ Llave           on red
    SKY_BLUE,  # F   ↑ Flecha arriba  sky blue
    RED,  # F#  ★III Estrella III red (casa de Gátople)
    GREEN,  # G   ↓ Flecha abajo   on green
    BLUE,  # G#  ★IV Estrella IV  blue + orange
)


# Monochrome palette — for the black/white instructional view of stickers
# (piano, fretboard) where you want to focus on glyph + position only.
INK: Final[str] = "#111111"
PAPER: Final[str] = "#FFFFFF"
MONO_HEX: Final[tuple[str, ...]] = tuple([PAPER] * 12)

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
